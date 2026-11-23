"""`run`：自定义 Python 脚本兜底。

脚本需提供 `def run(ctx, **args)`，可以访问：
    ctx.page           Playwright Page
    ctx.variables      extract 得到的变量
    ctx.env            env 配置中的变量
    ctx.log(msg)       写入步骤日志（会自动脱敏）
    ctx.set_var(k, v)  设置模板变量
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..errors import StepFailure
from .base import StepContext

ACTION = "run"
LABEL = "自定义脚本"
RETRY_SAFE = False


class Params(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file: str
    function: str = "run"
    args: dict[str, Any] = Field(default_factory=dict)


def _script_path(params: Params, project_root: Path) -> Path:
    path = Path(params.file)
    return path if path.is_absolute() else (project_root / path)


def validate(step, project_root: Path) -> list[str]:  # type: ignore[no-untyped-def]
    params: Params = step.params
    path = _script_path(params, project_root)
    return [] if path.exists() else [f"脚本文件不存在: {path}"]


def run(step, ctx: StepContext) -> None:  # type: ignore[no-untyped-def]
    params: Params = step.params
    path = _script_path(params, ctx.project_root).resolve()
    if not path.exists():
        raise StepFailure(f"脚本文件不存在: {path}")

    if str(ctx.project_root) not in sys.path:
        sys.path.insert(0, str(ctx.project_root))

    module_name = f"sop_user_script_{abs(hash(str(path)))}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise StepFailure(f"无法加载脚本: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    try:
        spec.loader.exec_module(module)
        func = getattr(module, params.function, None)
        if not callable(func):
            raise StepFailure(f"脚本 {path} 中不存在可调用函数 {params.function}()")
        result = func(ctx, **params.args)
    except (StepFailure,):
        raise
    except Exception as exc:
        raise StepFailure(
            f"自定义脚本执行失败: {type(exc).__name__}: {exc}"
        ) from exc

    suffix = "" if result is None else f"，返回 {type(result).__name__}"
    ctx.log(f"脚本 {path.name}:{params.function} 执行完成{suffix}")
