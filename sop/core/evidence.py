"""证据采集：截图、失败现场（全页截图 / DOM / 控制台日志）。"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from playwright.sync_api import Page

from .redact import Redactor, slugify


@dataclass
class Shot:
    label: str
    path: Path
    full_page: bool = False


@dataclass
class FailureEvidence:
    viewport: Shot | None
    full_page: Shot | None
    html_path: Path | None
    console_path: Path | None
    html_excerpt: str
    console_text: str


class Evidence:
    """一次流程运行对应一个独立目录。"""

    def __init__(self, run_dir: Path, shots_policy: str, redactor: Redactor) -> None:
        self.run_dir = run_dir
        self.shots_policy = shots_policy
        self.redactor = redactor
        self.console_errors: list[str] = []
        self._counter = 0

    # ---- 控制台 ----
    def bind_console(self, page: Page) -> None:
        def on_console(msg) -> None:  # type: ignore[no-untyped-def]
            if msg.type == "error":
                self.console_errors.append(self.redactor.text(f"[console.error] {msg.text}"))

        def on_page_error(error) -> None:  # type: ignore[no-untyped-def]
            self.console_errors.append(self.redactor.text(f"[pageerror] {error}"))

        page.on("console", on_console)
        page.on("pageerror", on_page_error)

    # ---- 截图 ----
    def shot(self, page: Page, label: str, *, full_page: bool = False) -> Shot:
        self._counter += 1
        name = f"{self._counter:02d}-{slugify(label)}.png"
        path = self.run_dir / name
        page.screenshot(path=str(path), full_page=full_page, animations="disabled")
        return Shot(label=label, path=path, full_page=full_page)

    def capture_failure(self, page: Page, label: str) -> FailureEvidence:
        viewport = self.shot(page, f"{label}-失败现场")
        full = self.shot(page, f"{label}-全页", full_page=True)

        html = ""
        html_path: Path | None = None
        try:
            html = self.redactor.text(page.content())
            html_path = self.run_dir / "failure.html"
            html_path.write_text(html, encoding="utf-8")
        except Exception:  # 页面可能已经关闭，失败证据尽量别二次抛错
            html = ""

        console_text = "\n".join(self.console_errors) or "（无控制台错误）"
        console_path = self.run_dir / "console.log"
        console_path.write_text(console_text, encoding="utf-8")

        return FailureEvidence(
            viewport=viewport,
            full_page=full,
            html_path=html_path,
            console_path=console_path,
            html_excerpt=html[:300_000],
            console_text=console_text,
        )

    def write_console(self) -> Path:
        path = self.run_dir / "console.log"
        text = "\n".join(self.console_errors) or "（无控制台错误）"
        path.write_text(text, encoding="utf-8")
        return path


def make_run_dir(base: Path, name: str) -> Path:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    candidate = base / f"{stamp}_{slugify(name)}"
    index = 2
    while candidate.exists():
        candidate = base / f"{stamp}_{slugify(name)}-{index}"
        index += 1
    candidate.mkdir(parents=True, exist_ok=False)
    return candidate
