from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from ..locator import Target
from ._util import playwright_call, resolve_or_timeout, short
from .base import StepContext

ACTION = "fill"
LABEL = "输入"
RETRY_SAFE = False


class Params(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target: Target
    value: str | int | float | bool
    clear: bool = True


def run(step, ctx: StepContext) -> None:  # type: ignore[no-untyped-def]
    params: Params = step.params
    resolved = resolve_or_timeout(ctx, params.target)
    text = str(params.value)
    if params.clear:
        playwright_call(
            "输入",
            lambda: resolved.first.fill(text, timeout=ctx.timeout_ms),
            ctx,
        )
    else:
        playwright_call(
            "追加输入",
            lambda: resolved.first.press_sequentially(text, timeout=ctx.timeout_ms),
            ctx,
        )
    ctx.log(f"已输入: {short(text)}")
