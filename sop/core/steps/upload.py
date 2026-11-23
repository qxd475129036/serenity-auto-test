from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from ..errors import StepFailure
from ..locator import Target
from ._util import playwright_call, resolve_or_timeout
from .base import StepContext

ACTION = "upload"
LABEL = "上传文件"
RETRY_SAFE = False


class Params(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target: Target
    files: str | list[str] = Field(min_length=1)


def _paths(params: Params, project_root: Path) -> list[Path]:
    raw = [params.files] if isinstance(params.files, str) else params.files
    result = []
    for item in raw:
        path = Path(item)
        result.append(path if path.is_absolute() else project_root / path)
    return result


def validate(step, project_root: Path) -> list[str]:  # type: ignore[no-untyped-def]
    params: Params = step.params
    errors = []
    for path in _paths(params, project_root):
        if not path.exists():
            errors.append(f"待上传文件不存在: {path}")
    return errors


def run(step, ctx: StepContext) -> None:  # type: ignore[no-untyped-def]
    params: Params = step.params
    paths = _paths(params, ctx.project_root)
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        raise StepFailure(f"待上传文件不存在: {', '.join(missing)}")

    resolved = resolve_or_timeout(ctx, params.target)
    playwright_call(
        "上传文件",
        lambda: resolved.first.set_input_files([str(p) for p in paths]),
        ctx,
    )
    ctx.log(f"已上传 {len(paths)} 个文件: {', '.join(p.name for p in paths)}")
