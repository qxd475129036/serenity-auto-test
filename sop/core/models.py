"""流程 YAML 的 Pydantic 模型与加载器。

步骤只保留公共字段（name / timeout / retries / optional / key），
其余字段交给对应动作模块自己的 Params 模型校验，因此新增动作
只需要新增模块，不用改这里。

加载阶段还会处理：
- `include_steps`：引用可复用的步骤片段
- `locators` + `target: {ref: name}`：页面对象/定位复用
- `pages.<module>.<CONST>`：从 pages/ 下的 Python 页面对象取定位
"""

from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

from .errors import FlowError
from .locator import Target
from .steps import STEP_COMMON_FIELDS, registry

SUPPORTED_VERSIONS = {1}


def _format_validation_error(exc: ValidationError) -> str:
    lines = []
    for item in exc.errors():
        location = ".".join(str(part) for part in item["loc"])
        lines.append(f"- {location or '<root>'}: {item['msg']}")
    return "\n".join(lines)


class Step(BaseModel):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    action: str
    name: str | None = None
    timeout: float | None = Field(default=None, gt=0)
    retries: int | None = Field(default=None, ge=0)
    retry_on_timeout: bool | None = None
    optional: bool = False
    key: bool = False
    params: BaseModel = Field(exclude=True)

    @model_validator(mode="before")
    @classmethod
    def _split_params(cls, data: Any) -> Any:
        if isinstance(data, cls):
            return data
        if not isinstance(data, dict):
            raise ValueError("步骤必须是映射（action + 参数）")

        values = dict(data)
        action = values.pop("action", None)
        if not action:
            raise ValueError("缺少 action 字段")
        if not isinstance(action, str):
            raise ValueError("action 必须是字符串")

        module = registry.get(action)
        common = {
            key: values.pop(key) for key in list(values) if key in STEP_COMMON_FIELDS
        }
        try:
            params = module.Params.model_validate(values)
        except ValidationError as exc:
            raise ValueError(
                f"动作 {action} 的参数不合法:\n{_format_validation_error(exc)}"
            ) from exc
        return {"action": action, "params": params, **common}

    @property
    def title(self) -> str:
        return self.name or self.action


class Flow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = 1
    name: str = ""
    description: str = ""
    env: str | None = None
    timeout: float = Field(default=90, gt=0)
    default_step_timeout: float = Field(default=12, gt=0)
    retries: int = Field(default=1, ge=0)
    browser: Literal["chromium", "firefox", "webkit"] = "chromium"
    storage_state: str | None = None
    save_storage_state: str | None = None
    requires: list[str] = Field(default_factory=list)
    include_steps: list[str] = Field(default_factory=list)
    locators: dict[str, Target] = Field(default_factory=dict)
    steps: list[Step] = Field(min_length=1)

    @field_validator("version")
    @classmethod
    def _validate_version(cls, value: int) -> int:
        if value not in SUPPORTED_VERSIONS:
            supported = ", ".join(str(item) for item in sorted(SUPPORTED_VERSIONS))
            raise ValueError(f"不支持的流程版本 {value}，当前支持: {supported}")
        return value


def _read_yaml(path: Path) -> Any:
    if not path.exists():
        raise FlowError(f"流程文件不存在: {path}")
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise FlowError(f"{path} 不是合法 YAML: {exc}") from exc


def _resolve_include_path(base_dir: Path, project_root: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    local = base_dir / candidate
    if local.exists():
        return local
    return project_root / candidate


def _load_steps_fragment(
    path: Path,
    project_root: Path,
    stack: set[Path],
) -> tuple[list[Any], dict[str, Any]]:
    """加载步骤片段，返回 (steps, locators)。片段可以是步骤列表或映射。"""
    resolved = path.resolve()
    if resolved in stack:
        raise FlowError(f"include_steps 存在循环引用: {resolved}")
    stack = {*stack, resolved}

    raw = _read_yaml(resolved)
    if isinstance(raw, list):
        return raw, {}
    if not isinstance(raw, dict):
        raise FlowError(f"步骤片段 {resolved} 必须是列表或映射（steps/locators）")

    locators: dict[str, Any] = dict(raw.get("locators") or {})
    steps: list[Any] = []
    for item in raw.get("include_steps") or []:
        if not isinstance(item, str):
            raise FlowError(f"步骤片段 {resolved} 的 include_steps 必须都是字符串")
        child = _resolve_include_path(resolved.parent, project_root, item)
        child_steps, child_locators = _load_steps_fragment(child, project_root, stack)
        steps.extend(child_steps)
        locators.update(child_locators)

    fragment_steps = raw.get("steps")
    if fragment_steps is None:
        raise FlowError(f"步骤片段 {resolved} 缺少 steps")
    if not isinstance(fragment_steps, list):
        raise FlowError(f"步骤片段 {resolved} 的 steps 必须是列表")
    steps.extend(fragment_steps)
    return steps, locators


def load_page_module(module_name: str, project_root: Path) -> Any:
    """加载 ``pages/<module_name>.py``，供页面对象常量解析与录制器复用。"""
    module_path = project_root / "pages" / f"{module_name}.py"
    if not module_path.exists():
        raise FlowError(f"页面对象模块不存在: {module_path}")

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    module_key = f"sop_page_{module_name}"
    module_spec = importlib.util.spec_from_file_location(module_key, module_path)
    if module_spec is None or module_spec.loader is None:
        raise FlowError(f"无法加载页面对象模块: {module_path}")
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_key] = module
    try:
        module_spec.loader.exec_module(module)
    except Exception as exc:
        raise FlowError(f"加载页面对象模块 {module_path} 失败: {exc}") from exc
    return module


def _load_page_constant(spec: str, project_root: Path) -> dict[str, Any]:
    """把 `pages.saucedemo.LOGIN_BUTTON` 解析成 Python 页面对象里的字典。"""
    parts = spec.split(".")
    if parts and parts[0] == "pages":
        parts = parts[1:]
    if len(parts) < 2:
        raise FlowError(
            f"页面对象引用格式应为 pages.<module>.<CONST>，收到: {spec!r}"
        )

    module_name = parts[0]
    attr_path = parts[1:]
    module = load_page_module(module_name, project_root)
    try:
        value: Any = module
        for attr in attr_path:
            value = getattr(value, attr)
    except Exception as exc:
        raise FlowError(f"解析页面对象 {spec} 失败: {exc}") from exc

    if not isinstance(value, dict):
        raise FlowError(f"页面对象 {spec} 必须导出字典，实际为 {type(value).__name__}")
    return value


def _resolve_locator_values(
    locators: dict[str, Any], project_root: Path
) -> dict[str, Any]:
    resolved: dict[str, Any] = {}
    for name, value in locators.items():
        if isinstance(value, str):
            resolved[name] = _load_page_constant(value, project_root)
        elif isinstance(value, dict):
            resolved[name] = value
        else:
            raise FlowError(
                f"locators.{name} 必须是映射或 pages.<module>.<CONST> 字符串"
            )
    return resolved


def _resolve_step_targets(
    step: Any, locators: dict[str, Any], where: str
) -> Any:
    if not isinstance(step, dict):
        return step
    values = dict(step)
    target = values.get("target")

    if isinstance(target, str):
        ref = target
        if ref not in locators:
            raise FlowError(f"{where} 引用了不存在的 locators.{ref}")
        values["target"] = copy.deepcopy(locators[ref])
    elif isinstance(target, dict) and "ref" in target:
        ref = target.get("ref")
        if not isinstance(ref, str) or not ref:
            raise FlowError(f"{where} 的 target.ref 必须是非空字符串")
        if len(target) > 1:
            raise FlowError(f"{where} 的 target 不能同时使用 ref 和其他字段")
        if ref not in locators:
            raise FlowError(f"{where} 引用了不存在的 locators.{ref}")
        values["target"] = copy.deepcopy(locators[ref])
    return values


def load_flow(path: Path, project_root: Path | None = None) -> Flow:
    if not path.exists():
        raise FlowError(f"流程文件不存在: {path}")
    project_root = (project_root or path.parent).resolve()
    raw = _read_yaml(path)
    if not isinstance(raw, dict):
        raise FlowError(f"{path} 顶层必须是映射（name / steps ...）")

    version = raw.get("version", 1)
    if version not in SUPPORTED_VERSIONS:
        supported = ", ".join(str(item) for item in sorted(SUPPORTED_VERSIONS))
        raise FlowError(
            f"{path} 使用了不支持的流程版本 {version}，当前支持: {supported}"
        )

    all_steps: list[Any] = []
    locators: dict[str, Any] = {}
    for item in raw.get("include_steps") or []:
        if not isinstance(item, str):
            raise FlowError(f"{path} 的 include_steps 必须都是字符串")
        include_path = _resolve_include_path(path.parent, project_root, item)
        fragment_steps, fragment_locators = _load_steps_fragment(
            include_path, project_root, {path.resolve()}
        )
        all_steps.extend(fragment_steps)
        locators.update(fragment_locators)

    locators.update(raw.get("locators") or {})
    locators = _resolve_locator_values(locators, project_root)

    main_steps = raw.get("steps") or []
    if not isinstance(main_steps, list):
        raise FlowError(f"{path} 的 steps 必须是列表")
    all_steps.extend(main_steps)
    all_steps = [
        _resolve_step_targets(step, locators, f"{path} 的步骤 {index}")
        for index, step in enumerate(all_steps, start=1)
    ]

    raw["steps"] = all_steps
    raw["locators"] = locators
    raw.setdefault("name", path.stem)
    try:
        return Flow.model_validate(raw)
    except ValidationError as exc:
        raise FlowError(f"{path} 校验失败:\n{_format_validation_error(exc)}") from exc


def validate_flow(flow: Flow, project_root: Path) -> list[str]:
    """dry-run 的额外检查（文件存在性等），语法错误在加载时已抛出。"""
    errors: list[str] = []
    for index, step in enumerate(flow.steps, start=1):
        module = registry.get(step.action)
        validator = getattr(module, "validate", None)
        if validator is None:
            continue
        for message in validator(step, project_root):
            errors.append(f"步骤 {index}（{step.title}）: {message}")
    return errors
