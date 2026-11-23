"""终端输出：步骤进度与结论。"""

from __future__ import annotations

import sys


class Console:
    def __init__(self) -> None:
        self._tty = sys.stdout.isatty()

    def _wrap(self, code: str, text: str) -> str:
        if not self._tty:
            return text
        return f"\033[{code}m{text}\033[0m"

    def green(self, text: str) -> str:
        return self._wrap("32", text)

    def red(self, text: str) -> str:
        return self._wrap("31", text)

    def yellow(self, text: str) -> str:
        return self._wrap("33", text)

    def dim(self, text: str) -> str:
        return self._wrap("2", text)

    def line(self, text: str = "") -> None:
        print(text, flush=True)

    def header(self, text: str) -> None:
        print(text, flush=True)

    def begin_step(self, index: int, total: int, action: str, name: str) -> None:
        print(f"  [{index}/{total}] {action:<10} {name}  ", end="", flush=True)

    def _end(self, text: str) -> None:
        print(text, flush=True)

    def step_ok(self, duration: float, attempts: int) -> None:
        extra = f"（重试 {attempts - 1} 次）" if attempts > 1 else ""
        self._end(self.green(f"ok {duration:.2f}s{extra}"))

    def step_warn(self, duration: float, error: str | None) -> None:
        self._end(self.yellow(f"warn {duration:.2f}s  {error or ''}"))

    def step_fail(self, duration: float, error: str | None) -> None:
        self._end(self.red(f"fail {duration:.2f}s  {error or ''}"))

    def step_skip(self, index: int, total: int, action: str, name: str) -> None:
        print(self.dim(f"  [{index}/{total}] {action:<10} {name}  skipped"), flush=True)

    def warn(self, message: str) -> None:
        print(self.yellow(f"! {message}"), flush=True)

    def error(self, message: str) -> None:
        print(self.red(f"✘ {message}"), flush=True)
