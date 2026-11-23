"""执行引擎：启动浏览器、逐步执行、重试、截图与失败证据。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from time import monotonic
from typing import Any

from pydantic import ValidationError
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from .config import EnvConfig
from .console import Console
from .errors import (
    LocatorInvalid,
    StepAmbiguity,
    StepAssertion,
    StepFailure,
    StepTimeout,
    TemplateError,
)
from .evidence import Evidence
from .models import Flow, Step
from .redact import Redactor
from .result import FlowResult, StepResult
from .steps import StepContext, registry
from .template import TemplateContext


@dataclass
class RunOptions:
    headed: bool = False
    shots: str = "key"
    trace: bool = False
    browser: str | None = None
    timeout: float | None = None


def _resolve_path(value: str, project_root: Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def _short_error(message: str, limit: int = 300) -> str:
    line = " ".join(str(message).split())
    return line[:limit] + ("…" if len(line) > limit else "")


def _render_params(step: Step, template: TemplateContext):  # type: ignore[no-untyped-def]
    raw = step.params.model_dump(by_alias=True)
    rendered = template.render(raw)
    return type(step.params).model_validate(rendered)


class FlowRunner:
    def __init__(
        self,
        project_root: Path,
        env_config: EnvConfig,
        options: RunOptions,
        console: Console | None = None,
    ) -> None:
        self.project_root = project_root
        self.env = env_config
        self.options = options
        self.console = console or Console()

    # ---- 浏览器 ----
    def _launch(self, playwright, flow: Flow):  # type: ignore[no-untyped-def]
        browser_name = self.options.browser or flow.browser
        browser_type = getattr(playwright, browser_name, None)
        if browser_type is None:
            raise StepFailure(f"不支持的浏览器: {browser_name}")
        return browser_type.launch(
            headless=not self.options.headed,
            slow_mo=self.env.browser.slow_mo,
        )

    def _new_context(self, browser, flow: Flow, warnings: list[str]):  # type: ignore[no-untyped-def]
        kwargs: dict[str, Any] = {
            "viewport": self.env.browser.viewport_dict(),
            "locale": self.env.browser.locale,
        }
        state_value = flow.storage_state or self.env.storage_state
        if state_value:
            state_path = _resolve_path(state_value, self.project_root)
            if state_path.exists():
                kwargs["storage_state"] = str(state_path)
            else:
                warnings.append(f"storage_state 文件不存在，已忽略: {state_path}")
        return browser.new_context(**kwargs)

    def _save_storage(self, context, flow: Flow, warnings: list[str]) -> None:  # type: ignore[no-untyped-def]
        value = flow.save_storage_state or self.env.save_storage_state
        if not value:
            return
        path = _resolve_path(value, self.project_root)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            context.storage_state(path=str(path))
            self.console.line(self.console.dim(f"  已保存登录态: {path}"))
        except Exception as exc:
            warnings.append(f"保存 storage_state 失败: {exc}")

    # ---- 单步 ----
    def _classify(self, exc: Exception, redactor: Redactor) -> tuple[bool, str]:
        """返回 (是否可重试, 展示给用户/报告的错误信息)。"""
        if isinstance(exc, (StepTimeout, PlaywrightTimeoutError)):
            return True, redactor.text(f"超时: {_short_error(exc)}")
        if isinstance(exc, (StepAssertion, StepFailure, StepAmbiguity, LocatorInvalid)):
            return False, redactor.text(_short_error(exc))
        if isinstance(exc, PlaywrightError):
            return False, redactor.text(f"Playwright 错误: {_short_error(exc)}")
        return False, redactor.text(f"{type(exc).__name__}: {_short_error(exc)}")

    def _capture_auto_shot(
        self, page: Page, evidence: Evidence, step: Step, shots: list
    ) -> None:
        policy = self.options.shots
        if step.action == "screenshot":
            return
        if policy == "every" or (policy == "key" and step.key):
            shots.append(evidence.shot(page, step.title))

    def _run_step(
        self,
        index: int,
        total: int,
        step: Step,
        flow: Flow,
        page: Page,
        evidence: Evidence,
        template: TemplateContext,
        redactor: Redactor,
        remaining_s: float,
    ) -> StepResult:
        label = step.title
        action_label = self._label(step.action)
        self.console.begin_step(index, total, step.action, label)

        step_budget = min(step.timeout or flow.default_step_timeout, remaining_s)
        step_deadline = monotonic() + step_budget
        retries = step.retries if step.retries is not None else flow.retries
        module = registry.get(step.action)
        retry_safe = bool(getattr(module, "RETRY_SAFE", False))
        retry_enabled = (
            step.retry_on_timeout if step.retry_on_timeout is not None else retry_safe
        )

        started = monotonic()
        status = "passed"
        error: str | None = None
        attempts = 0
        logs: list[str] = []
        shots: list = []
        failure = None

        rendered_step: Step | None = None
        try:
            rendered_step = step.model_copy(
                update={"params": _render_params(step, template)}
            )
        except (TemplateError, ValidationError) as exc:
            status = "failed"
            error = redactor.text(f"参数渲染失败: {exc}")

        if rendered_step is not None:
            for attempt in range(1, retries + 2):
                left = step_deadline - monotonic()
                if left <= 0.05:
                    status = "failed"
                    error = f"步骤超时（预算已用尽，{step_budget:.1f}s）"
                    break
                attempts = attempt
                timeout_ms = max(int(left * 1000), 100)
                ctx = StepContext(
                    page=page,
                    env=template.data["env"],
                    template=template,
                    evidence=evidence,
                    project_root=self.project_root,
                    timeout_ms=timeout_ms,
                    step=rendered_step,
                    redactor=redactor,
                )
                try:
                    registry.run(rendered_step, ctx)
                    logs.extend(ctx.logs)
                    shots.extend(ctx.shots)
                    status = "passed"
                    error = None
                    break
                except Exception as exc:  # noqa: BLE001 - 统一归类
                    logs.extend(ctx.logs)
                    shots.extend(ctx.shots)
                    retryable, message = self._classify(exc, redactor)
                    if (
                        retryable
                        and retry_enabled
                        and attempt <= retries
                        and step_deadline - monotonic() > 0.05
                    ):
                        logs.append(f"第 {attempt} 次尝试超时，准备重试: {message}")
                        continue
                    if retryable and not retry_enabled:
                        logs.append(
                            "动作默认不允许超时重试；如确认无副作用，"
                            "可在步骤上设置 retry_on_timeout: true"
                        )
                    status = "failed"
                    error = message
                    break

        if status == "failed" and step.optional:
            status = "warn"

        if status == "passed":
            try:
                self._capture_auto_shot(page, evidence, step, shots)
            except Exception as exc:
                logs.append(f"自动截图失败: {exc}")
        elif status in ("failed", "warn"):
            try:
                failure = evidence.capture_failure(page, label)
                if failure.viewport:
                    shots.append(failure.viewport)
                if failure.full_page:
                    shots.append(failure.full_page)
            except Exception as exc:
                logs.append(f"失败现场采集失败: {exc}")

        duration = monotonic() - started
        result = StepResult(
            index=index,
            action=step.action,
            action_label=action_label,
            name=label,
            status=status,
            duration=duration,
            attempts=attempts,
            error=error,
            logs=logs,
            shots=shots,
            failure=failure,
        )

        if status == "passed":
            self.console.step_ok(duration, attempts)
        elif status == "warn":
            self.console.step_warn(duration, _short_error(error or ""))
        else:
            self.console.step_fail(duration, _short_error(error or ""))
        return result

    def _label(self, action: str) -> str:
        try:
            return str(getattr(registry.get(action), "LABEL", action))
        except Exception:
            return action

    def _append_skipped(
        self, flow: Flow, results: list[StepResult]
    ) -> None:
        total = len(flow.steps)
        while len(results) < total:
            index = len(results) + 1
            step = flow.steps[index - 1]
            self.console.step_skip(index, total, step.action, step.title)
            results.append(
                StepResult(
                    index=index,
                    action=step.action,
                    action_label=self._label(step.action),
                    name=step.title,
                    status="skipped",
                    attempts=0,
                )
            )

    # ---- 整条流程 ----
    def run(self, flow: Flow, run_dir: Path) -> FlowResult:
        started_at = datetime.now()
        started = monotonic()
        redactor = self.env.redactor()
        evidence = Evidence(run_dir, self.options.shots, redactor)
        template = TemplateContext({"env": self.env.template_values(), "vars": {}})
        results: list[StepResult] = []
        warnings: list[str] = []
        error: str | None = None
        trace_path: Path | None = None
        failed = False
        budget = self.options.timeout or flow.timeout
        browser_name = self.options.browser or flow.browser

        try:
            with sync_playwright() as playwright:
                playwright.selectors.set_test_id_attribute(
                    self.env.browser.test_id_attribute
                )
                browser = self._launch(playwright, flow)
                context = self._new_context(browser, flow, warnings)
                tracing = False
                try:
                    page = context.new_page()
                    evidence.bind_console(page)
                    if self.options.trace:
                        context.tracing.start(
                            screenshots=True, snapshots=True, sources=True
                        )
                        tracing = True

                    deadline = started + budget
                    for index, step in enumerate(flow.steps, start=1):
                        remaining = deadline - monotonic()
                        if remaining <= 0.1:
                            error = f"整场超时（{budget:.0f}s）"
                            failed = True
                            break
                        result = self._run_step(
                            index,
                            len(flow.steps),
                            step,
                            flow,
                            page,
                            evidence,
                            template,
                            redactor,
                            remaining,
                        )
                        results.append(result)
                        if result.status == "failed":
                            failed = True
                            error = result.error
                            break

                    if not failed:
                        self._save_storage(context, flow, warnings)

                    if tracing:
                        trace_path = run_dir / "trace.zip"
                        try:
                            context.tracing.stop(path=str(trace_path))
                        except Exception as exc:
                            warnings.append(f"保存 trace 失败: {exc}")
                            trace_path = None
                finally:
                    try:
                        context.close()
                    except Exception:
                        pass
                    try:
                        browser.close()
                    except Exception:
                        pass
        except Exception as exc:
            failed = True
            error = redactor.text(f"{type(exc).__name__}: {_short_error(exc)}")

        self._append_skipped(flow, results)
        evidence.write_console()

        status = "failed" if failed else "passed"
        return FlowResult(
            name=flow.name,
            description=flow.description,
            status=status,
            started_at=started_at,
            duration=monotonic() - started,
            env=self.env.name,
            base_url=self.env.base_url or "",
            headed=self.options.headed,
            shots_policy=self.options.shots,
            browser=browser_name,
            steps=results,
            console_errors=evidence.console_errors,
            warnings=warnings,
            run_dir=run_dir,
            trace_path=trace_path,
            error=error,
        )
