from __future__ import annotations

import time
from pathlib import Path

import pytest

from core.config import EnvConfig
from core.console import Console
from core.engine import FlowRunner, RunOptions
from core.errors import StepAssertion, StepTimeout
from core.evidence import FailureEvidence
from core.models import Flow
from core.redact import Redactor
from core.template import TemplateContext


class NullConsole(Console):
    def __init__(self) -> None:
        super().__init__()
        self.lines: list[str] = []

    def line(self, text: str = "") -> None:
        self.lines.append(text)

    def header(self, text: str) -> None:
        self.lines.append(text)

    def begin_step(self, index: int, total: int, action: str, name: str) -> None:
        return

    def step_ok(self, duration: float, attempts: int) -> None:
        return

    def step_warn(self, duration: float, error: str | None) -> None:
        return

    def step_fail(self, duration: float, error: str | None) -> None:
        return

    def step_skip(self, index: int, total: int, action: str, name: str) -> None:
        return

    def warn(self, message: str) -> None:
        return

    def error(self, message: str) -> None:
        return


class FakeEvidence:
    def capture_failure(self, page, label):  # type: ignore[no-untyped-def]
        return FailureEvidence(None, None, None, None, "", "")


def _flow(step: dict, retries: int = 0) -> Flow:
    return Flow.model_validate({"name": "retry-test", "retries": retries, "steps": [step]})


def _run_step(monkeypatch, step: dict, *, retries: int = 0, remaining: float = 5.0):  # type: ignore[no-untyped-def]
    flow = _flow(step, retries=retries)
    runner = FlowRunner(
        Path.cwd(),
        EnvConfig(name="test"),
        RunOptions(shots="fail"),
        NullConsole(),
    )
    return runner._run_step(
        1,
        1,
        flow.steps[0],
        flow,
        object(),
        FakeEvidence(),  # type: ignore[arg-type]
        TemplateContext({"env": {}, "vars": {}}),
        Redactor(),
        remaining,
    )


def test_unsafe_click_is_not_retried(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    def boom(step, ctx):  # type: ignore[no-untyped-def]
        raise StepTimeout("boom")

    monkeypatch.setattr("core.steps.registry.run", boom)
    result = _run_step(
        monkeypatch,
        {"action": "click", "target": {"testid": "save"}},
        retries=3,
    )
    assert result.status == "failed"
    assert result.attempts == 1


def test_click_can_opt_in_to_retry(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    def boom(step, ctx):  # type: ignore[no-untyped-def]
        raise StepTimeout("boom")

    monkeypatch.setattr("core.steps.registry.run", boom)
    result = _run_step(
        monkeypatch,
        {
            "action": "click",
            "target": {"testid": "save"},
            "retry_on_timeout": True,
        },
        retries=1,
    )
    assert result.status == "failed"
    assert result.attempts == 2


def test_safe_goto_is_retried(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    def boom(step, ctx):  # type: ignore[no-untyped-def]
        raise StepTimeout("boom")

    monkeypatch.setattr("core.steps.registry.run", boom)
    result = _run_step(
        monkeypatch,
        {"action": "goto", "url": "https://example.com"},
        retries=2,
    )
    assert result.attempts == 3


def test_assertion_is_never_retried(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    def boom(step, ctx):  # type: ignore[no-untyped-def]
        raise StepAssertion("nope")

    monkeypatch.setattr("core.steps.registry.run", boom)
    result = _run_step(
        monkeypatch,
        {"action": "assert", "text": "nope"},
        retries=3,
    )
    assert result.status == "failed"
    assert result.attempts == 1


def test_step_timeout_is_clamped_by_remaining_budget(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    seen: list[int] = []

    def slow_timeout(step, ctx):  # type: ignore[no-untyped-def]
        seen.append(ctx.timeout_ms)
        time.sleep(0.05)
        raise StepTimeout("boom")

    monkeypatch.setattr("core.steps.registry.run", slow_timeout)
    started = time.monotonic()
    result = _run_step(
        monkeypatch,
        {"action": "wait_for", "target": {"testid": "x"}},
        retries=10,
        remaining=0.5,
    )
    elapsed = time.monotonic() - started
    assert result.status == "failed"
    assert seen
    assert max(seen) <= 500
    assert elapsed < 0.8


def _run_assert_value(page, value: str):  # type: ignore[no-untyped-def]
    flow = _flow(
        {"action": "assert", "target": {"css": "#username"}, "value": value}
    )
    runner = FlowRunner(
        Path.cwd(),
        EnvConfig(name="test"),
        RunOptions(shots="fail"),
        NullConsole(),
    )
    return runner._run_step(
        1,
        1,
        flow.steps[0],
        flow,
        page,
        FakeEvidence(),  # type: ignore[arg-type]
        TemplateContext({"env": {}, "vars": {}}),
        Redactor(),
        5.0,
    )


def test_assert_value_checks_input_value(page) -> None:  # type: ignore[no-untyped-def]
    page.fill("#username", "Alice")
    assert _run_assert_value(page, "Alice").status == "passed"
    assert _run_assert_value(page, "Bob").status == "failed"
