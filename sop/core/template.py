"""`{{变量}}` 模板插值。

支持：
- `{{env.base_url}}`、`{{env.username}}`：来自 configs/env.<name>.yaml
- `{{products}}`、`{{vars.products}}`：extract 步骤产出的变量

整个字符串只有一个占位符时保留原始类型（数字 / 列表等），
否则按字符串拼接。
"""

from __future__ import annotations

import re
from typing import Any

from .errors import TemplateError

_PATH = r"[A-Za-z_][\w]*(?:\.[\w]+)*"
_PLACEHOLDER = re.compile(r"\{\{\s*(" + _PATH + r")\s*\}\}")
_SINGLE = re.compile(r"^\s*\{\{\s*(" + _PATH + r")\s*\}\}\s*$")


class TemplateContext:
    def __init__(self, data: dict[str, Any] | None = None) -> None:
        self.data: dict[str, Any] = data or {}
        self.data.setdefault("env", {})
        self.data.setdefault("vars", {})

    def set_var(self, name: str, value: Any) -> None:
        self.data["vars"][name] = value
        self.data[name] = value

    def _lookup_path(self, path: str) -> Any:
        parts = path.split(".")
        root = parts[0]

        if root in ("env", "vars"):
            node: Any = self.data[root]
            rest = parts[1:]
        elif path in self.data:
            return self.data[path]
        elif root in self.data["vars"]:
            node = self.data["vars"][root]
            rest = parts[1:]
        elif root in self.data["env"]:
            node = self.data["env"][root]
            rest = parts[1:]
        else:
            raise TemplateError(f"模板变量不存在: {{{{ {path} }}}}")

        for key in rest:
            if isinstance(node, dict) and key in node:
                node = node[key]
            else:
                raise TemplateError(f"模板变量不存在: {{{{ {path} }}}}")
        return node

    def render(self, value: Any) -> Any:
        if isinstance(value, str):
            single = _SINGLE.match(value)
            if single:
                return self._lookup_path(single.group(1))
            if "{{" not in value:
                return value

            def repl(match: re.Match[str]) -> str:
                resolved = self._lookup_path(match.group(1))
                if resolved is None:
                    return ""
                if isinstance(resolved, (dict, list)):
                    raise TemplateError(
                        f"变量 {match.group(1)} 是复杂类型，不能直接拼进字符串"
                    )
                return str(resolved)

            return _PLACEHOLDER.sub(repl, value)
        if isinstance(value, dict):
            return {k: self.render(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self.render(v) for v in value]
        return value
