from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PIL import Image

from core.evidence import Shot
from core.redact import Redactor
from core.report import write_report
from core.result import FlowResult, StepResult

REPO_ROOT = Path(__file__).resolve().parents[1]


def _result(tmp_path: Path) -> FlowResult:
    image = tmp_path / "01-测试.png"
    Image.new("RGB", (16, 16), "white").save(image)
    step = StepResult(
        index=1,
        action="goto",
        action_label="打开页面",
        name="测试步骤",
        status="passed",
        duration=0.1,
        attempts=1,
        shots=[Shot(label="测试截图", path=image)],
    )
    return FlowResult(
        name="demo",
        description="报告测试",
        status="passed",
        started_at=datetime.now(),
        duration=0.1,
        env="test",
        base_url="https://example.com",
        headed=False,
        shots_policy="key",
        browser="chromium",
        steps=[step],
        console_errors=[],
        warnings=[],
        run_dir=tmp_path,
    )


def test_report_embeds_screenshot(tmp_path: Path) -> None:
    flow = _result(tmp_path)
    output = write_report([flow], tmp_path / "report.html", REPO_ROOT)
    html = output.read_text(encoding="utf-8")
    assert "demo" in html
    assert "测试步骤" in html
    assert "data:image/png;base64" in html
    assert flow.report_path == output


def test_redactor_replaces_secret_values() -> None:
    redactor = Redactor(["secret_sauce"])
    assert redactor.text("password=secret_sauce") == "password=***"
    assert redactor.obj({"nested": ["secret_sauce"]}) == {"nested": ["***"]}
