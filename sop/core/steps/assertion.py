from __future__ import annotations

import re
from time import monotonic
from typing import Literal

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import expect
from pydantic import BaseModel, ConfigDict, model_validator

from ..errors import LocatorInvalid, LocatorTimeout, StepAssertion, StepFailure
from ..locator import Target, resolve, wait_absent
from .base import StepContext

ACTION = "assert"
LABEL = "断言"
RETRY_SAFE = False


class Params(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target: Target | None = None
    state: Literal[
        "visible", "hidden", "attached", "detached", "enabled", "disabled"
    ] = "visible"
    text: str | None = None
    value: str | None = None
    attr: str | None = None
    url_contains: str | None = None

    @model_validator(mode="after")
    def _check(self) -> "Params":
        if (
            self.target is None
            and not self.text
            and not self.url_contains
            and self.value is None
            and not self.attr
        ):
            raise ValueError(
                "assert 至少需要 target / text / value / attr / url_contains 之一"
            )
        if (self.value is not None or self.attr) and self.target is None:
            raise ValueError("value/attr 断言必须提供 target")
        if self.text and self.target is None and self.state not in ("visible", "attached"):
            raise ValueError("text 断言只支持 visible / attached 状态")
        return self


def _first_line(exc: Exception, limit: int = 220) -> str:
    text = str(exc).strip()
    line = text.splitlines()[0] if text else exc.__class__.__name__
    return line[:limit]


def run(step, ctx: StepContext) -> None:  # type: ignore[no-untyped-def]
    params: Params = step.params
    deadline = monotonic() + ctx.timeout_ms / 1000
    described: list[str] = []

    def remaining_ms() -> int:
        return max(int((deadline - monotonic()) * 1000), 100)

    try:
        if params.url_contains:
            expect(ctx.page).to_have_url(
                re.compile(re.escape(params.url_contains)), timeout=remaining_ms()
            )
            described.append(f"URL 包含 {params.url_contains!r}")

        if params.target is not None:
            if params.state in ("hidden", "detached"):
                try:
                    wait_absent(
                        ctx.page, params.target, remaining_ms(), state=params.state
                    )
                except LocatorTimeout as exc:
                    raise StepAssertion(f"断言失败: {exc}") from exc
                described.append(f"{params.target.describe()} {params.state}")
            else:
                try:
                    resolved = resolve(
                        ctx.page,
                        params.target,
                        remaining_ms(),
                        state="attached"
                        if params.state in ("enabled", "disabled", "attached")
                        else "visible",
                    )
                except LocatorTimeout as exc:
                    raise StepAssertion(str(exc)) from exc
                ctx.log(f"定位命中: {resolved.strategy}（{params.target.describe()}）")
                locator = resolved.first

                if params.text:
                    expect(locator).to_contain_text(
                        params.text, timeout=remaining_ms()
                    )
                    described.append(f"文本包含 {params.text!r}")
                if params.value is not None:
                    expect(locator).to_have_value(
                        params.value, timeout=remaining_ms()
                    )
                    described.append(f"值等于 {params.value!r}")
                if params.attr:
                    expect(locator).to_have_attribute(
                        params.attr, params.value or "", timeout=remaining_ms()
                    )
                    described.append(f"属性 {params.attr}={params.value!r}")
                if (
                    not params.text
                    and params.value is None
                    and not params.attr
                    and params.state == "visible"
                ):
                    expect(locator).to_be_visible(timeout=remaining_ms())
                    described.append(f"{params.target.describe()} 可见")
                elif (
                    not params.text
                    and params.value is None
                    and not params.attr
                    and params.state == "attached"
                ):
                    described.append(f"{params.target.describe()} 已挂载")
                elif (
                    not params.text
                    and params.value is None
                    and not params.attr
                    and params.state == "enabled"
                ):
                    expect(locator).to_be_enabled(timeout=remaining_ms())
                    described.append(f"{params.target.describe()} 可用")
                elif (
                    not params.text
                    and params.value is None
                    and not params.attr
                    and params.state == "disabled"
                ):
                    expect(locator).to_be_disabled(timeout=remaining_ms())
                    described.append(f"{params.target.describe()} 禁用")

        if params.text and params.target is None:
            expect(ctx.page.locator("body")).to_contain_text(
                params.text, timeout=remaining_ms()
            )
            described.append(f"页面包含文本 {params.text!r}")

    except (StepAssertion, StepFailure):
        raise
    except LocatorInvalid as exc:
        raise StepFailure(str(exc)) from exc
    except (AssertionError, PlaywrightTimeoutError) as exc:
        raise StepAssertion(f"断言失败: {_first_line(exc)}") from exc
    except PlaywrightError as exc:
        raise StepFailure(f"断言执行出错: {exc}") from exc

    for item in described:
        ctx.log(f"断言通过: {item}")
