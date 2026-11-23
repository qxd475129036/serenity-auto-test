from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from .base import StepContext

ACTION = "screenshot"
LABEL = "截图"
RETRY_SAFE = True


class Params(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    full_page: bool = False


def run(step, ctx: StepContext) -> None:  # type: ignore[no-untyped-def]
    params: Params = step.params
    label = params.name or step.name or "截图"
    ctx.shot(label, full_page=params.full_page)
