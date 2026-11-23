"""动作注册表：按目录自动发现，新增动作不需要改内核。

在 core/steps/ 下新建模块，提供以下四个名字即可被自动加载：
    ACTION: str          动作名（YAML 中 action 字段）
    LABEL: str           中文说明（报告里展示）
    Params: BaseModel     该动作的参数模型
    run(step, ctx)       执行函数
"""

from __future__ import annotations

import importlib
import pkgutil
from types import ModuleType

from ..errors import FlowError

_MODULES: dict[str, ModuleType] | None = None
_REQUIRED = ("ACTION", "LABEL", "Params", "run")


def _discover() -> dict[str, ModuleType]:
    global _MODULES
    if _MODULES is not None:
        return _MODULES

    package = importlib.import_module(__package__)
    modules: dict[str, ModuleType] = {}
    for info in pkgutil.iter_modules(package.__path__):
        if info.name.startswith("_") or info.name in {"base", "registry"}:
            continue
        module = importlib.import_module(f"{__package__}.{info.name}")
        action = getattr(module, "ACTION", None)
        if not action:
            continue
        missing = [name for name in _REQUIRED if not hasattr(module, name)]
        if missing:
            raise RuntimeError(
                f"动作模块 {module.__name__} 缺少定义: {', '.join(missing)}"
            )
        if action in modules:
            raise RuntimeError(
                f"动作 {action!r} 重复定义: {modules[action].__name__} / {module.__name__}"
            )
        modules[action] = module

    _MODULES = modules
    return modules


def actions() -> dict[str, ModuleType]:
    return _discover()


def get(action: str) -> ModuleType:
    modules = _discover()
    if action not in modules:
        raise FlowError(
            f"未知动作 {action!r}，可用动作: {', '.join(sorted(modules))}"
        )
    return modules[action]


def run(step, ctx) -> None:  # type: ignore[no-untyped-def]
    get(step.action).run(step, ctx)
