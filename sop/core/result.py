"""运行结果数据结构。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .evidence import FailureEvidence, Shot


@dataclass
class StepResult:
    index: int
    action: str
    action_label: str
    name: str
    status: str  # passed | failed | warn | skipped
    duration: float = 0.0
    attempts: int = 1
    error: str | None = None
    logs: list[str] = field(default_factory=list)
    shots: list[Shot] = field(default_factory=list)
    failure: FailureEvidence | None = None


@dataclass
class FlowResult:
    name: str
    description: str
    status: str  # passed | failed
    started_at: datetime
    duration: float
    env: str
    base_url: str
    headed: bool
    shots_policy: str
    browser: str
    steps: list[StepResult]
    console_errors: list[str]
    warnings: list[str]
    run_dir: Path
    trace_path: Path | None = None
    error: str | None = None
    report_path: Path | None = None

    @property
    def stats(self) -> dict[str, int]:
        stats = {"total": len(self.steps), "passed": 0, "failed": 0, "warn": 0, "skipped": 0}
        for step in self.steps:
            if step.status in stats:
                stats[step.status] += 1
        return stats

    @property
    def ok(self) -> bool:
        return self.status == "passed"
