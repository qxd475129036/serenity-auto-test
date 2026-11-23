"""步骤上下文与公共字段。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from playwright.sync_api import Page

from ..evidence import Evidence, Shot
from ..redact import Redactor
from ..template import TemplateContext

# 步骤对象里除动作私有参数外的公共字段
STEP_COMMON_FIELDS = {
    "action",
    "name",
    "timeout",
    "retries",
    "retry_on_timeout",
    "optional",
    "key",
}


@dataclass
class StepContext:
    page: Page
    env: dict[str, Any]
    template: TemplateContext
    evidence: Evidence
    project_root: Path
    timeout_ms: int
    step: Any
    redactor: Redactor
    logs: list[str] = field(default_factory=list)
    shots: list[Shot] = field(default_factory=list)
    detail: str | None = None

    @property
    def variables(self) -> dict[str, Any]:
        return self.template.data["vars"]

    def log(self, message: object) -> None:
        self.logs.append(self.redactor.text(message))

    def set_var(self, name: str, value: Any) -> None:
        self.template.set_var(name, value)

    def shot(self, label: str, *, full_page: bool = False) -> Shot:
        shot = self.evidence.shot(self.page, label, full_page=full_page)
        self.shots.append(shot)
        self.log(f"截图: {shot.path.name}")
        return shot
