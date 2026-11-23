from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from pydantic import BaseModel, ConfigDict

from ..errors import StepFailure, StepTimeout
from ..locator import Target
from ._util import resolve_or_timeout
from .base import StepContext

ACTION = "download"
LABEL = "下载文件"
RETRY_SAFE = False


class Params(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target: Target
    save_as: str


def run(step, ctx: StepContext) -> None:  # type: ignore[no-untyped-def]
    params: Params = step.params
    resolved = resolve_or_timeout(ctx, params.target)

    try:
        with ctx.page.expect_download(timeout=ctx.timeout_ms) as info:
            resolved.first.click(timeout=ctx.timeout_ms)
        download = info.value
    except PlaywrightTimeoutError as exc:
        raise StepTimeout(
            f"等待下载超时（{ctx.timeout_ms / 1000:.1f}s）"
        ) from exc
    except PlaywrightError as exc:
        raise StepFailure(f"触发下载失败: {exc}") from exc

    target_path = Path(params.save_as)
    if not target_path.is_absolute():
        target_path = ctx.project_root / target_path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    download.save_as(str(target_path))
    ctx.log(f"已保存下载文件: {target_path}")
