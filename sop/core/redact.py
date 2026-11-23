"""敏感信息脱敏与文件名清洗。"""

from __future__ import annotations

import re
from typing import Any

_PLACEHOLDER = "***"


class Redactor:
    """把配置中来自环境变量的敏感值从日志 / 报告里替换掉。"""

    def __init__(self, secrets: list[str] | None = None) -> None:
        self._secrets = sorted(
            {s for s in (secrets or []) if s and len(s) >= 2},
            key=len,
            reverse=True,
        )

    def add(self, secret: str | None) -> None:
        if secret and len(secret) >= 2 and secret not in self._secrets:
            self._secrets.append(secret)
            self._secrets.sort(key=len, reverse=True)

    def text(self, value: object) -> str:
        result = str(value)
        for secret in self._secrets:
            result = result.replace(secret, _PLACEHOLDER)
        return result

    def obj(self, value: Any) -> Any:
        if isinstance(value, str):
            return self.text(value)
        if isinstance(value, dict):
            return {k: self.obj(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [self.obj(v) for v in value]
        return value


def slugify(text: str, *, limit: int = 60) -> str:
    """保留中文、字母、数字，其余字符转成连字符，用于文件名。"""
    cleaned = re.sub(r"[^\w\u4e00-\u9fff.-]+", "-", str(text), flags=re.UNICODE)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-._ ")
    return (cleaned or "step")[:limit]
