from __future__ import annotations

from typing import Literal

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from pydantic import BaseModel, ConfigDict

from ..errors import StepFailure, StepTimeout
from ._util import absolute_url
from .base import StepContext

ACTION = "goto"
LABEL = "打开页面"
RETRY_SAFE = True


class Params(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str
    wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "load"


def run(step, ctx: StepContext) -> None:  # type: ignore[no-untyped-def]
    params: Params = step.params
    url = absolute_url(params.url, ctx.env)
    ctx.log(f"打开 {url}（wait_until={params.wait_until}）")
    try:
        response = ctx.page.goto(
            url, wait_until=params.wait_until, timeout=ctx.timeout_ms
        )
    except PlaywrightTimeoutError as exc:
        raise StepTimeout(f"页面打开超时（{ctx.timeout_ms / 1000:.1f}s）: {url}") from exc
    except PlaywrightError as exc:
        raise StepFailure(f"页面打开失败: {url}（{exc}）") from exc

    if response is not None:
        ctx.log(f"HTTP {response.status}")
        if response.status >= 400:
            # 有些 SPA 会对深链接返回 404，但前端仍能正常渲染，
            # 因此这里只记录状态码，页面是否正确交给后续 assert 判断。
            ctx.log("HTTP 状态 >= 400，继续由后续断言校验页面内容")
