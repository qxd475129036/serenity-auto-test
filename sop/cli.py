"""sop 命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from playwright.sync_api import Error as PlaywrightError

from core import __version__
from core.config import EnvConfig, load_env_config
from core.console import Console
from core.engine import FlowRunner, RunOptions
from core.errors import ConfigError, FlowError, SopError
from core.evidence import make_run_dir
from core.models import Flow, load_flow, validate_flow
from core.recorder import RecordOptions, Recorder, default_output
from core.report import write_report
from core.redact import slugify


def _find_project_root(target: Path) -> Path:
    start = target.resolve()
    if start.is_file():
        start = start.parent
    for candidate in [start, *start.parents]:
        if (
            (candidate / "configs").is_dir()
            or (candidate / "flows").is_dir()
            or (candidate / "templates").is_dir()
        ):
            return candidate
    return Path.cwd().resolve()


def _collect_flows(target: Path) -> tuple[list[Path], bool]:
    if target.is_dir():
        files = sorted(
            path
            for path in target.iterdir()
            if path.is_file() and path.suffix.lower() in {".yaml", ".yml"}
        )
        if not files:
            raise FlowError(f"目录中没有 YAML 流程: {target}")
        return files, True
    if target.is_file():
        return [target], False
    raise FlowError(f"流程路径不存在: {target}")


class EnvLoader:
    def __init__(self, project_root: Path, console: Console) -> None:
        self.project_root = project_root
        self.console = console
        self._cache: dict[str, EnvConfig] = {}
        self._warned: set[str] = set()

    def path_for(self, name: str) -> Path:
        return self.project_root / "configs" / f"env.{name}.yaml"

    def get(self, name: str) -> EnvConfig:
        if name in self._cache:
            return self._cache[name]
        path = self.path_for(name)
        if not path.exists():
            if name not in self._warned:
                self.console.warn(
                    f"未找到 {path}，本次不提供任何 env 变量（流程里的 {{{{env.*}}}} 会解析失败）"
                )
                self._warned.add(name)
            config = EnvConfig(name=name)
        else:
            config = load_env_config(path, env_name=name)
        self._cache[name] = config
        return config


def _flow_env_name(flow: Flow, override: str | None) -> str:
    return override or flow.env or "dev"


def _uses_env(step) -> bool:  # type: ignore[no-untyped-def]
    def walk(value: Any) -> bool:
        if isinstance(value, str):
            return "{{" in value and "env." in value
        if isinstance(value, dict):
            return any(walk(item) for item in value.values())
        if isinstance(value, list):
            return any(walk(item) for item in value)
        return False

    return walk(step.params.model_dump(by_alias=True))


def _print_step_plan(flow: Flow, console: Console) -> None:
    console.line(f"  流程 {flow.name} — {len(flow.steps)} 步，预算 {flow.timeout:.0f}s，重试 {flow.retries} 次")
    for index, step in enumerate(flow.steps, start=1):
        marker = " [key]" if step.key else ""
        optional = " [optional]" if step.optional else ""
        console.line(f"    {index:>2}. {step.action:<10} {step.title}{marker}{optional}")


def _dry_run(paths: list[Path], args: argparse.Namespace, project_root: Path, console: Console) -> int:
    env_loader = EnvLoader(project_root, console)
    errors = 0
    total_steps = 0
    console.header(f"sop dry-run · 共 {len(paths)} 个流程文件 · 只校验，不启动浏览器")
    console.line()

    for path in paths:
        try:
            flow = load_flow(path, project_root)
        except FlowError as exc:
            console.error(f"{path}\n{exc}")
            errors += 1
            continue

        env_name = _flow_env_name(flow, args.env)
        total_steps += len(flow.steps)
        console.line(f"• {path}")
        try:
            env_loader.get(env_name)
        except ConfigError as exc:
            console.error(str(exc))
            errors += 1
            continue

        config_path = env_loader.path_for(env_name)
        if not config_path.exists() and any(_uses_env(step) for step in flow.steps):
            console.error(f"{path} 使用了 {{{{env.*}}}}，但缺少 {config_path}")
            errors += 1
            continue

        _print_step_plan(flow, console)
        if flow.requires:
            console.line(
                f"  依赖: {', '.join(flow.requires)}（单独执行前请确认已运行）"
            )
        if flow.storage_state:
            state = Path(flow.storage_state)
            state = state if state.is_absolute() else project_root / state
            if not state.exists():
                console.warn(f"storage_state 文件尚不存在（运行时会被忽略）: {state}")

        problems = validate_flow(flow, project_root)
        for problem in problems:
            console.error(problem)
        if problems:
            errors += len(problems)
        else:
            console.line(console.green("  ✔ 语法、定位描述、脚本/文件引用校验通过"))
        console.line()

    if errors:
        console.error(f"dry-run 失败：{errors} 个问题")
        return 2
    console.line(console.green(f"✔ dry-run 通过：{len(paths)} 个流程，{total_steps} 步"))
    return 0


def _conclusion(result, console: Console) -> str:  # type: ignore[no-untyped-def]
    stats = result.stats
    duration = f"{result.duration:.1f}s"
    if result.ok:
        text = f"✔ {result.name} {stats['passed']} 步全过 用时 {duration}"
        if stats["warn"]:
            text += f"（{stats['warn']} 步警告）"
        return console.green(text)
    reason = result.error or "存在失败步骤"
    failed_step = next((s for s in result.steps if s.status == "failed"), None)
    position = f"第 {failed_step.index} 步「{failed_step.name}」" if failed_step else reason
    return console.red(
        f"✘ {result.name} {stats['passed']}/{stats['total']} 步通过，{position}失败 用时 {duration}"
    )


def _order_by_requires(
    entries: list[tuple[Path, Flow]], console: Console
) -> list[tuple[Path, Flow]]:
    """把声明了 requires 的流程排在依赖之后；缺失依赖只告警，循环依赖报错。"""
    by_name: dict[str, tuple[Path, Flow]] = {}
    for path, flow in entries:
        if flow.name in by_name:
            raise FlowError(f"流程名重复: {flow.name}（{path}）")
        by_name[flow.name] = (path, flow)

    ordered: list[tuple[Path, Flow]] = []
    state: dict[str, int] = {}
    missing_warned: set[str] = set()

    def visit(name: str, chain: list[str]) -> None:
        if state.get(name) == 1:
            cycle = " -> ".join([*chain, name])
            raise FlowError(f"requires 存在循环依赖: {cycle}")
        if state.get(name) == 2:
            return
        path, flow = by_name[name]
        state[name] = 1
        for dependency in flow.requires:
            if dependency not in by_name:
                if dependency not in missing_warned:
                    console.warn(
                        f"{flow.name} 声明依赖 {dependency}，但本次执行列表中没有它"
                    )
                    missing_warned.add(dependency)
                continue
            visit(dependency, [*chain, name])
        state[name] = 2
        ordered.append((path, flow))

    for _, flow in entries:
        visit(flow.name, [])
    return ordered


def _run(paths: list[Path], batch: bool, args: argparse.Namespace, project_root: Path, console: Console) -> int:
    entries: list[tuple[Path, Flow]] = []
    for path in paths:
        entries.append((path, load_flow(path, project_root)))
    entries = _order_by_requires(entries, console)
    flows = [flow for _, flow in entries]
    paths = [path for path, _ in entries]

    env_loader = EnvLoader(project_root, console)
    runs_dir = project_root / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    batch_dir: Path | None = None
    if batch:
        batch_dir = make_run_dir(runs_dir, "batch")
        console.header(
            f"sop batch · {len(flows)} 个流程 · env={args.env or '按流程'} · shots={args.shots}"
            f" · {'headed' if args.headed else 'headless'}{' · trace' if args.trace else ''}"
        )
    else:
        console.header(
            f"sop run · env={args.env or flows[0].env or 'dev'} · shots={args.shots}"
            f" · {'headed' if args.headed else 'headless'}{' · trace' if args.trace else ''}"
        )
    console.line()

    options = RunOptions(
        headed=args.headed,
        shots=args.shots,
        trace=args.trace,
        browser=args.browser,
        timeout=args.timeout,
    )
    results = []

    for index, (path, flow) in enumerate(zip(paths, flows), start=1):
        env_name = _flow_env_name(flow, args.env)
        env_config = env_loader.get(env_name)

        if batch_dir is not None:
            run_dir = batch_dir / slugify(flow.name)
            if run_dir.exists():
                run_dir = batch_dir / f"{index:02d}_{slugify(flow.name)}"
            run_dir.mkdir(parents=True, exist_ok=False)
        else:
            run_dir = make_run_dir(runs_dir, flow.name)

        console.header(
            f"▶ {flow.name}"
            + (f"（{flow.description}）" if flow.description else "")
            + f"  · {flow.browser if not args.browser else args.browser} · {len(flow.steps)} 步"
        )
        runner = FlowRunner(project_root, env_config, options, console)
        result = runner.run(flow, run_dir)
        results.append(result)
        console.line()

        if not result.ok and args.stop_on_failure:
            break

    report_dir = batch_dir if batch_dir is not None else results[0].run_dir
    report_path = write_report(
        results,
        report_dir / "report.html",
        project_root,
        title="sop 批量执行报告" if batch else f"sop · {results[0].name}",
    )

    console.header("执行结论")
    for result in results:
        console.line(_conclusion(result, console))
    if batch:
        steps_passed = sum(r.stats["passed"] for r in results)
        steps_total = sum(r.stats["total"] for r in results)
        total_duration = sum(r.duration for r in results)
        flows_passed = sum(1 for r in results if r.ok)
        summary = (
            f"总计 {flows_passed}/{len(results)} 个流程通过，"
            f"{steps_passed}/{steps_total} 步通过，用时 {total_duration:.1f}s"
        )
        console.line((console.green if flows_passed == len(results) else console.red)(summary))
    console.line()
    console.line(f"报告: {report_path}")

    return 0 if all(result.ok for result in results) else 1


def _record(args: argparse.Namespace, console: Console) -> int:
    project_root = _find_project_root(Path.cwd())
    env_loader = EnvLoader(project_root, console)
    env_config = env_loader.get(args.env)

    out = Path(args.out) if args.out else default_output(project_root)
    options = RecordOptions(
        url=args.url,
        out=out,
        env_name=args.env,
        name=args.name,
        include_steps=list(args.include_steps or []),
        page_objects=list(args.page_object or []),
        browser=args.browser or "chromium",
        storage_state=args.storage_state,
    )
    recorder = Recorder(project_root, env_config, console)
    try:
        path = recorder.run(options)
    except PlaywrightError as exc:
        console.error(f"录制失败: {exc}")
        return 2
    console.line()
    console.line(f"录制完成: {path}")
    return 0 if recorder.validation_ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sop",
        description="配置驱动的浏览器 RPA：YAML 流程 + Playwright + 单文件 HTML 报告",
    )
    parser.add_argument("--version", action="version", version=f"sop {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    record_parser = subparsers.add_parser(
        "record", help="打开浏览器录制操作，生成流程 YAML"
    )
    record_parser.add_argument("url", help="录制起始地址（完整 URL）")
    record_parser.add_argument("--env", default="dev", help="环境名，默认 dev")
    record_parser.add_argument(
        "--out", help="输出 YAML 路径，默认 flows/recorded_<时间戳>.yaml"
    )
    record_parser.add_argument("--name", help="流程名，默认取输出文件名")
    record_parser.add_argument(
        "--include-steps",
        action="append",
        default=[],
        metavar="PATH",
        help="复用已有的步骤片段，可重复",
    )
    record_parser.add_argument(
        "--page-object",
        action="append",
        default=[],
        metavar="MODULE",
        help="复用 pages/<module>.py 中的定位常量，可重复",
    )
    record_parser.add_argument(
        "--browser", choices=["chromium", "firefox", "webkit"], help="浏览器"
    )
    record_parser.add_argument(
        "--storage-state", help="启动时加载登录态文件（相对项目根目录）"
    )

    run_parser = subparsers.add_parser("run", help="执行流程文件或 flows/ 目录")
    run_parser.add_argument("target", help="流程 YAML 文件或目录")
    run_parser.add_argument("--env", help="环境名，对应 configs/env.<name>.yaml")
    run_parser.add_argument("--headed", action="store_true", help="显示浏览器窗口")
    run_parser.add_argument(
        "--shots",
        choices=["every", "key", "fail"],
        default="key",
        help="截图策略：every 每步 / key 关键步骤 / fail 仅失败（默认 key）",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只校验流程语法、定位描述与文件引用，不启动浏览器",
    )
    run_parser.add_argument("--trace", action="store_true", help="记录 Playwright trace.zip")
    run_parser.add_argument(
        "--browser", choices=["chromium", "firefox", "webkit"], help="覆盖流程里的浏览器"
    )
    run_parser.add_argument(
        "--timeout", type=float, help="覆盖整场超时预算（秒）"
    )
    run_parser.add_argument(
        "--stop-on-failure",
        action="store_true",
        help="批量执行时遇到第一个失败流程就停止",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    console = Console()

    try:
        if args.command == "record":
            return _record(args, console)
        target = Path(args.target)
        paths, batch = _collect_flows(target)
        project_root = _find_project_root(target)
        if args.dry_run:
            return _dry_run(paths, args, project_root, console)
        return _run(paths, batch, args, project_root, console)
    except (ConfigError, FlowError, SopError) as exc:
        console.error(str(exc))
        return 2
    except KeyboardInterrupt:
        console.error("已中断")
        return 130


if __name__ == "__main__":
    sys.exit(main())
