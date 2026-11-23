from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from ..errors import LocatorInvalid, LocatorTimeout, StepFailure, StepTimeout
from ..locator import Target, wait_absent
from ._util import resolve_or_timeout
from .base import StepContext

ACTION = "wait_for"
LABEL = "等待元素"
RETRY_SAFE = True


class Params(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target: Target
    state: Literal["visible", "hidden", "attached", "detached"] = "visible"


def run(step, ctx: StepContext) -> None:  # type: ignore[no-untyped-def]
    params: Params = step.params
    try:
        if params.state in ("hidden", "detached"):
            wait_absent(ctx.page, params.target, ctx.timeout_ms, state=params.state)
            ctx.log(f"元素已 {params.state}: {params.target.describe()}")
        else:
            resolved = resolve_or_timeout(
                ctx, params.target, state="attached" if params.state == "attached" else "visible"
            )
            ctx.log(f"元素已 {params.state}（{resolved.strategy}）")
    except LocatorTimeout as exc:
        raise StepTimeout(str(exc)) from exc
    except LocatorInvalid as exc:
        raise StepFailure(str(exc)) from exc
