"""单文件 HTML 报告：图片内嵌 base64，可直接转发。"""

from __future__ import annotations

import base64
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import __version__
from .evidence import Shot
from .result import FlowResult, StepResult

_STATUS_TEXT = {
    "passed": "通过",
    "failed": "失败",
    "warn": "警告",
    "skipped": "跳过",
}


def _format_duration(seconds: float) -> str:
    if seconds >= 60:
        minutes = int(seconds // 60)
        return f"{minutes}m {seconds - minutes * 60:.1f}s"
    return f"{seconds:.1f}s"


def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def _shot_payload(shot: Shot, project_root: Path) -> dict:
    payload = {
        "label": shot.label,
        "file": shot.path.name,
        "rel": _relative(shot.path, project_root),
        "src": "",
        "full_page": shot.full_page,
    }
    try:
        encoded = base64.b64encode(shot.path.read_bytes()).decode("ascii")
        payload["src"] = f"data:image/png;base64,{encoded}"
    except OSError:
        pass
    return payload


def _step_payload(step: StepResult, project_root: Path) -> dict:
    failure = None
    if step.failure is not None:
        failure = {
            "html_excerpt": step.failure.html_excerpt,
            "console": step.failure.console_text,
            "html_file": _relative(step.failure.html_path, project_root)
            if step.failure.html_path
            else None,
            "console_file": _relative(step.failure.console_path, project_root)
            if step.failure.console_path
            else None,
        }
    return {
        "index": step.index,
        "action": step.action,
        "action_label": step.action_label,
        "name": step.name,
        "status": step.status,
        "status_text": _STATUS_TEXT.get(step.status, step.status),
        "duration": step.duration,
        "duration_text": f"{step.duration:.2f}s",
        "attempts": step.attempts,
        "retried": step.attempts > 1,
        "error": step.error,
        "logs": step.logs,
        "shots": [_shot_payload(shot, project_root) for shot in step.shots],
        "failure": failure,
    }


def _flow_payload(flow: FlowResult, project_root: Path, report_dir: Path) -> dict:
    stats = flow.stats
    return {
        "name": flow.name,
        "description": flow.description,
        "ok": flow.ok,
        "status": flow.status,
        "status_text": _STATUS_TEXT.get(flow.status, flow.status),
        "duration": flow.duration,
        "duration_text": _format_duration(flow.duration),
        "started_text": flow.started_at.strftime("%Y-%m-%d %H:%M:%S"),
        "env": flow.env,
        "base_url": flow.base_url,
        "browser": flow.browser,
        "headed_text": "有头模式" if flow.headed else "无头模式",
        "shots": flow.shots_policy,
        "trace": _relative(flow.trace_path, report_dir) if flow.trace_path else None,
        "run_dir": _relative(flow.run_dir, project_root),
        "error": flow.error,
        "warnings": flow.warnings,
        "console_errors": flow.console_errors,
        "stats": stats,
        "steps": [_step_payload(step, project_root) for step in flow.steps],
    }


def write_report(
    results: list[FlowResult],
    report_path: Path,
    project_root: Path,
    *,
    title: str = "sop 执行报告",
) -> Path:
    template_file = project_root / "templates" / "report.html"
    if not template_file.exists():
        template_file = Path(__file__).resolve().parent.parent / "templates" / "report.html"
    environment = Environment(
        loader=FileSystemLoader(str(template_file.parent)),
        autoescape=select_autoescape(["html"]),
    )
    template = environment.get_template(template_file.name)

    flows = [_flow_payload(result, project_root, report_path.parent) for result in results]
    totals = {
        "flows": len(flows),
        "flows_passed": sum(1 for flow in flows if flow["ok"]),
        "flows_failed": sum(1 for flow in flows if not flow["ok"]),
        "steps": sum(flow["stats"]["total"] for flow in flows),
        "passed": sum(flow["stats"]["passed"] for flow in flows),
        "failed": sum(flow["stats"]["failed"] for flow in flows),
        "warn": sum(flow["stats"]["warn"] for flow in flows),
        "skipped": sum(flow["stats"]["skipped"] for flow in flows),
        "duration_text": _format_duration(sum(flow["duration"] for flow in flows)),
        "ok": all(flow["ok"] for flow in flows),
    }

    html = template.render(
        title=title,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        tool_version=__version__,
        batch=len(flows) > 1,
        flows=flows,
        totals=totals,
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(html, encoding="utf-8")
    for result in results:
        result.report_path = report_path
    return report_path
