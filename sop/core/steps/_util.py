"""动作模块共用的小工具（下划线开头，不会被注册为动作）。"""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from ..errors import LocatorInvalid, LocatorTimeout, StepFailure, StepTimeout
from ..locator import Resolved, Target, resolve
from .base import StepContext

T = TypeVar("T")


def resolve_or_timeout(
    ctx: StepContext,
    target: Target,
    *,
    state: str = "visible",
    multiple: bool = False,
) -> Resolved:
    try:
        resolved = resolve(
            ctx.page, target, ctx.timeout_ms, state=state, multiple=multiple
        )
    except LocatorTimeout as exc:
        raise StepTimeout(str(exc)) from exc
    except LocatorInvalid as exc:
        raise StepFailure(str(exc)) from exc
    ctx.log(f"定位命中: {resolved.strategy}（{target.describe()}）")
    return resolved


def playwright_call(description: str, fn: Callable[[], T], ctx: StepContext) -> T:
    try:
        return fn()
    except PlaywrightTimeoutError as exc:
        raise StepTimeout(f"{description}超时（{ctx.timeout_ms / 1000:.1f}s）") from exc
    except PlaywrightError as exc:
        raise StepFailure(f"{description}失败: {exc}") from exc


def absolute_url(url: str, env: dict[str, Any]) -> str:
    if url.startswith("/"):
        base = str(env.get("base_url") or "").rstrip("/")
        return f"{base}{url}"
    return url


def short(value: Any, limit: int = 120) -> str:
    text = str(value).replace("\n", " ")
    return text if len(text) <= limit else text[:limit] + "…"
