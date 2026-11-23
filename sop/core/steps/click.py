from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ..locator import Target
from ._util import playwright_call, resolve_or_timeout
from .base import StepContext

ACTION = "click"
LABEL = "点击"
# 点击可能已经触发跳转/提交，超时重试可能重复执行副作用
RETRY_SAFE = False


class Params(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target: Target
    button: Literal["left", "right", "middle"] = "left"
    click_count: int = Field(default=1, ge=1)


def run(step, ctx: StepContext) -> None:  # type: ignore[no-untyped-def]
    params: Params = step.params
    resolved = resolve_or_timeout(ctx, params.target)
    playwright_call(
        "点击",
        lambda: resolved.first.click(
            button=params.button,
            click_count=params.click_count,
            timeout=ctx.timeout_ms,
        ),
        ctx,
    )
    ctx.log("点击完成")
