from __future__ import annotations

from pydantic import BaseModel, ConfigDict, model_validator

from ..locator import Target
from ._util import playwright_call, resolve_or_timeout
from .base import StepContext

ACTION = "select"
LABEL = "下拉选择"
RETRY_SAFE = False


class Params(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target: Target
    value: str | None = None
    label: str | None = None

    @model_validator(mode="after")
    def _check(self) -> "Params":
        if bool(self.value) == bool(self.label):
            raise ValueError("select 需要且只能提供 value 或 label 之一")
        return self


def run(step, ctx: StepContext) -> None:  # type: ignore[no-untyped-def]
    params: Params = step.params
    resolved = resolve_or_timeout(ctx, params.target)
    if params.value is not None:
        playwright_call(
            "下拉选择",
            lambda: resolved.first.select_option(
                value=params.value, timeout=ctx.timeout_ms
            ),
            ctx,
        )
        ctx.log(f"已选择 value={params.value}")
    else:
        playwright_call(
            "下拉选择",
            lambda: resolved.first.select_option(
                label=params.label, timeout=ctx.timeout_ms
            ),
            ctx,
        )
        ctx.log(f"已选择 label={params.label}")
