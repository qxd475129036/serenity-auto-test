"""环境配置加载。

configs/env.<name>.yaml 中可用 `${ENV_VAR}` 引用进程环境变量。
变量名里带 PASS / SECRET / TOKEN / KEY / CREDENTIAL 的值会被登记为敏感值，
从日志、报告、DOM 快照中统一替换成 ***。
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .errors import ConfigError
from .redact import Redactor

_ENV_REF = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
_SENSITIVE_NAME = re.compile(r"(PASS|SECRET|TOKEN|KEY|CREDENTIAL)", re.IGNORECASE)


class BrowserConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    viewport: list[int] = Field(default_factory=lambda: [1440, 900])
    locale: str = "en-US"
    slow_mo: int = 0
    test_id_attribute: str = "data-testid"

    def viewport_dict(self) -> dict[str, int]:
        return {"width": int(self.viewport[0]), "height": int(self.viewport[1])}


class EnvConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = "default"
    base_url: str | None = None
    vars: dict[str, Any] = Field(default_factory=dict)
    browser: BrowserConfig = Field(default_factory=BrowserConfig)
    storage_state: str | None = None
    save_storage_state: str | None = None
    secrets: list[str] = Field(default_factory=list, exclude=True)

    def redactor(self) -> Redactor:
        return Redactor(self.secrets)

    def template_values(self) -> dict[str, Any]:
        values: dict[str, Any] = {"name": self.name}
        if self.base_url:
            values["base_url"] = self.base_url
        values.update(self.vars)
        return values


def _resolve_env_refs(value: Any, secrets: list[str], config_path: Path) -> Any:
    if isinstance(value, str):

        def repl(match: re.Match[str]) -> str:
            var_name = match.group(1)
            if var_name not in os.environ:
                raise ConfigError(
                    f"{config_path} 引用了未设置的环境变量 ${{{var_name}}}。"
                    f"请先 export {var_name}=... 再执行。"
                )
            resolved = os.environ[var_name]
            if _SENSITIVE_NAME.search(var_name):
                secrets.append(resolved)
            return resolved

        if "${" in value:
            return _ENV_REF.sub(repl, value)
        return value
    if isinstance(value, dict):
        return {k: _resolve_env_refs(v, secrets, config_path) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_env_refs(v, secrets, config_path) for v in value]
    return value


def load_env_config(path: Path, *, env_name: str | None = None) -> EnvConfig:
    if not path.exists():
        raise ConfigError(f"环境配置文件不存在: {path}")

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"{path} 不是合法 YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigError(f"{path} 顶层必须是映射（key: value）")

    secrets: list[str] = []
    resolved = _resolve_env_refs(raw, secrets, path)
    resolved.setdefault("name", env_name or path.stem.removeprefix("env."))

    try:
        config = EnvConfig.model_validate(resolved)
    except ValidationError as exc:
        raise ConfigError(f"{path} 配置校验失败:\n{exc}") from exc

    config.secrets = sorted(set(secrets))
    return config
