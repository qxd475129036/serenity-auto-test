"""定位描述与多策略兜底。

流程里不写裸选择器，而是给出一个定位描述对象，执行时按固定优先级尝试：

    testid  ->  role + name  ->  text  ->  css  ->  xpath

第一个可见命中的策略即为本次实际使用的定位方式，会记录到日志与报告里，
方便后续知道该删哪条兜底。
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from fnmatch import fnmatch
from typing import Iterator

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Frame, FrameLocator, Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .errors import LocatorInvalid, LocatorTimeout, StepAmbiguity

# Playwright 支持的 ARIA role（用于 dry-run 提前发现拼写错误）
ARIA_ROLES = {
    "alert",
    "alertdialog",
    "application",
    "article",
    "banner",
    "blockquote",
    "button",
    "caption",
    "cell",
    "checkbox",
    "code",
    "columnheader",
    "combobox",
    "complementary",
    "contentinfo",
    "definition",
    "deletion",
    "dialog",
    "directory",
    "document",
    "emphasis",
    "feed",
    "figure",
    "form",
    "generic",
    "grid",
    "gridcell",
    "group",
    "heading",
    "img",
    "insertion",
    "link",
    "list",
    "listbox",
    "listitem",
    "log",
    "main",
    "marquee",
    "math",
    "menu",
    "menubar",
    "menuitem",
    "menuitemcheckbox",
    "menuitemradio",
    "meter",
    "navigation",
    "none",
    "note",
    "option",
    "paragraph",
    "presentation",
    "progressbar",
    "radio",
    "radiogroup",
    "region",
    "row",
    "rowgroup",
    "rowheader",
    "scrollbar",
    "search",
    "searchbox",
    "separator",
    "slider",
    "spinbutton",
    "status",
    "strong",
    "subscript",
    "superscript",
    "switch",
    "tab",
    "table",
    "tablist",
    "tabpanel",
    "term",
    "textbox",
    "time",
    "timer",
    "toolbar",
    "tooltip",
    "tree",
    "treegrid",
    "treeitem",
}


class FrameSpec(BaseModel):
    """指定 iframe 的方式：CSS、name 属性或 URL 通配符，三者选其一。"""

    model_config = ConfigDict(extra="forbid")

    css: str | None = None
    name: str | None = None
    url: str | None = None

    @model_validator(mode="after")
    def _validate(self) -> "FrameSpec":
        chosen = [field for field in ("css", "name", "url") if getattr(self, field)]
        if len(chosen) != 1:
            raise ValueError("frame 需要 css / name / url 中恰好设置一个")
        for field in chosen:
            if not str(getattr(self, field)).strip():
                raise ValueError(f"frame.{field} 不能为空字符串")
        return self


def _selector_problem(value: str, kind: str) -> str | None:
    """基础选择器语法检查，让 dry-run 尽早发现明显笔误。

    只做低风险规则（括号/引号闭合、结尾逗号、``##``），
    更细的语法交给 Playwright 在运行时判断。
    """
    pairs = {")": "(", "]": "["}
    stack: list[str] = []
    quote: str | None = None
    escaped = False
    for char in value:
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if quote is not None:
            if char == quote:
                quote = None
            continue
        if char in "'\"":
            quote = char
        elif char in "([":
            stack.append(char)
        elif char in ")]":
            if not stack or stack[-1] != pairs[char]:
                return "括号不匹配"
            stack.pop()
    if quote is not None:
        return "引号未闭合"
    if stack:
        return "括号未闭合"
    if value.rstrip().endswith(","):
        return "选择器不能以逗号结尾"
    if kind == "css" and "##" in value:
        return "CSS 选择器出现连续的 ##"
    if kind == "xpath" and value.lstrip().startswith("["):
        return "XPath 不能以 [ 开头"
    return None


class Target(BaseModel):
    """一个元素的定位描述，多个字段同时存在时按优先级兜底。"""

    model_config = ConfigDict(extra="forbid")

    testid: str | None = None
    role: str | None = None
    name: str | None = None
    text: str | None = None
    css: str | None = None
    xpath: str | None = None
    exact: bool = False
    # 多个元素命中时的显式选择；不设置则视为歧义错误
    first: bool = False
    index: int | None = Field(default=None, ge=1)
    # 可选的 iframe（CSS / name / url）；within 用于先定位容器再查找子元素
    frame: FrameSpec | str | None = None
    within: "Target | None" = None

    @model_validator(mode="after")
    def _validate(self) -> "Target":
        if not any((self.testid, self.role, self.text, self.css, self.xpath)):
            raise ValueError(
                "定位描述至少需要 testid / role / text / css / xpath 之一"
            )
        if self.name and not self.role:
            raise ValueError("name 需要和 role 一起使用（表示可访问名称）")
        if self.role and self.role not in ARIA_ROLES:
            raise ValueError(f"未知的 ARIA role: {self.role!r}")
        if self.first and self.index is not None:
            raise ValueError("first 和 index 不能同时设置")
        if isinstance(self.frame, str) and not self.frame.strip():
            raise ValueError("frame 不能为空字符串")
        for field in ("testid", "role", "text", "css", "xpath"):
            value = getattr(self, field)
            if value is not None and not str(value).strip():
                raise ValueError(f"{field} 不能为空字符串")
        for field, kind in (("css", "css"), ("xpath", "xpath")):
            value = getattr(self, field)
            if value is None:
                continue
            problem = _selector_problem(value, kind)
            if problem is not None:
                raise ValueError(f"{field} 选择器非法（{problem}）: {value!r}")
        return self

    def describe(self) -> str:
        parts: list[str] = []
        if self.testid:
            parts.append(f'testid="{self.testid}"')
        if self.role:
            desc = f"role={self.role}"
            if self.name:
                desc += f' name="{self.name}"'
            parts.append(desc)
        if self.text:
            parts.append(f'text="{self.text}"')
        if self.css:
            parts.append(f"css={self.css}")
        if self.xpath:
            parts.append(f"xpath={self.xpath}")
        if self.first:
            parts.append("first")
        if self.index is not None:
            parts.append(f"index={self.index}")
        prefix = ""
        if self.frame is not None:
            prefix += f"frame({_frame_label(self.frame)}) "
        if self.within is not None:
            prefix += f"within({self.within.describe()}) "
        return prefix + " | ".join(parts)


@dataclass
class Resolved:
    strategy: str
    locator: Locator

    @property
    def first(self) -> Locator:
        return self.locator.first


Root = Page | Frame | FrameLocator | Locator

# Playwright 在选择器语法错误时抛出的消息特征；命中则视为确定性错误
_SELECTOR_ERROR_MARKERS = (
    "while parsing css selector",
    "while parsing selector",
    "unknown engine",
    "is not a valid selector",
    "invalid selector",
    "invalid xpath",
    "error while parsing selector",
    "unexpected token",
)


def _frame_label(spec: FrameSpec | str) -> str:
    if isinstance(spec, FrameSpec):
        if spec.css:
            return f"css={spec.css}"
        if spec.name:
            return f'name="{spec.name}"'
        return f'url~"{spec.url}"'
    return f"css={spec}"


def _open_frame(
    page: Page, root: Root, spec: FrameSpec | str, deadline: float
) -> Root:
    """把当前作用域切换到目标 iframe。"""
    if isinstance(spec, FrameSpec) and spec.url:
        if not isinstance(root, Page):
            raise LocatorInvalid("frame.url 只能用在最外层定位描述上")
        while True:
            for frame in page.frames:
                if frame is page.main_frame:
                    continue
                if fnmatch(frame.url, spec.url):
                    return frame
            if time.monotonic() >= deadline:
                raise LocatorTimeout(f"未找到 URL 匹配的 iframe: {spec.url}")
            time.sleep(0.1)

    if isinstance(spec, FrameSpec):
        selector = spec.css or f"iframe[name={json.dumps(spec.name)}]"
    else:
        selector = spec
    factory = getattr(root, "frame_locator", None)
    if factory is None:
        raise LocatorInvalid("within 之后不能再嵌套 frame，请把 frame 写在父级定位上")
    return factory(selector)


def _prepare_root(page: Page, root: Root, target: Target, deadline: float) -> Root:
    if target.frame is not None:
        root = _open_frame(page, root, target.frame, deadline)
    if target.within is not None:
        remaining_ms = max(int((deadline - time.monotonic()) * 1000), 100)
        container = _resolve_in_root(
            page, root, target.within, deadline, remaining_ms, state="attached"
        )
        root = container.locator
    return root


def _scope_label(target: Target) -> str | None:
    parts: list[str] = []
    if target.frame is not None:
        parts.append(f"frame({_frame_label(target.frame)})")
    if target.within is not None:
        parts.append(f"within({target.within.describe()})")
    return " > ".join(parts) if parts else None


def _is_selector_error(exc: PlaywrightError) -> bool:
    message = str(exc).lower()
    return any(marker in message for marker in _SELECTOR_ERROR_MARKERS)


def _candidates(root: Root, target: Target) -> Iterator[tuple[str, Locator]]:
    if target.testid:
        yield "testid", root.get_by_test_id(target.testid)
    if target.role:
        kwargs = {"name": target.name} if target.name else {}
        yield "role", root.get_by_role(target.role, exact=target.exact, **kwargs)
    if target.text:
        yield "text", root.get_by_text(target.text, exact=target.exact)
    if target.css:
        yield "css", root.locator(target.css)
    if target.xpath:
        yield "xpath", root.locator(f"xpath={target.xpath}")


def _resolve_in_root(
    page: Page,
    root: Root,
    target: Target,
    deadline: float,
    timeout_ms: int,
    *,
    state: str = "visible",
    multiple: bool = False,
) -> Resolved:
    tried: list[str] = []

    while True:
        for strategy, locator in _candidates(root, target):
            if strategy not in tried:
                tried.append(strategy)
            try:
                count = locator.count()
                if count == 0:
                    continue

                if count > 1:
                    if target.index is not None:
                        if count < target.index:
                            continue
                        chosen = locator.nth(target.index - 1)
                    elif target.first:
                        chosen = locator.first
                    elif multiple:
                        chosen = locator
                    else:
                        raise StepAmbiguity(
                            f"定位歧义: {target.describe()} 命中 {count} 个元素；"
                            "请用 first: true 或 index: N 明确选择"
                        )
                else:
                    chosen = locator

                if state == "attached":
                    return Resolved(strategy, chosen)
                remaining_ms = max(int((deadline - time.monotonic()) * 1000), 200)
                chosen.first.wait_for(
                    state=state, timeout=min(300, remaining_ms)
                )
                return Resolved(strategy, chosen)
            except StepAmbiguity:
                raise
            except PlaywrightTimeoutError:
                continue
            except PlaywrightError as exc:
                if _is_selector_error(exc):
                    raise LocatorInvalid(
                        f"选择器非法: {target.describe()}；{str(exc).splitlines()[0]}"
                    ) from exc
                continue

        if time.monotonic() >= deadline:
            raise LocatorTimeout(
                f"定位失败（{timeout_ms / 1000:.1f}s）: {target.describe()}"
                f"；已尝试策略: {', '.join(tried)}"
            )
        time.sleep(0.1)


def resolve(
    page: Page,
    target: Target,
    timeout_ms: int,
    *,
    state: str = "visible",
    multiple: bool = False,
) -> Resolved:
    """轮询所有候选策略，返回第一个命中的定位。

    支持先进入 ``frame`` / ``within`` 容器，再在作用域内查找；
    默认要求唯一命中；多个元素时必须显式设置 first/index，
    或由调用方传 multiple=True（例如 extract all）。
    """
    deadline = time.monotonic() + max(timeout_ms, 0) / 1000
    root = _prepare_root(page, page, target, deadline)
    resolved = _resolve_in_root(
        page, root, target, deadline, timeout_ms, state=state, multiple=multiple
    )
    scope = _scope_label(target)
    if scope:
        resolved.strategy = f"{scope} > {resolved.strategy}"
    return resolved


def count_matches(page: Page, target: Target, timeout_ms: int = 500) -> int:
    """即时统计定位描述第一个可用策略的命中数量（带 frame/within 作用域）。

    录制器用它挑选唯一命中的策略，因此不会像 ``resolve`` 那样等到超时。
    """
    deadline = time.monotonic() + max(timeout_ms, 0) / 1000
    root = _prepare_root(page, page, target, deadline)
    for _, locator in _candidates(root, target):
        try:
            return locator.count()
        except PlaywrightError as exc:
            if _is_selector_error(exc):
                raise LocatorInvalid(
                    f"选择器非法: {target.describe()}；{str(exc).splitlines()[0]}"
                ) from exc
            continue
    return 0


def wait_absent(page: Page, target: Target, timeout_ms: int, *, state: str) -> None:
    """等待 hidden（不可见或不存在）或 detached（从 DOM 移除）。"""
    deadline = time.monotonic() + max(timeout_ms, 0) / 1000
    root = _prepare_root(page, page, target, deadline)

    while True:
        absent = True
        for _, locator in _candidates(root, target):
            try:
                count = locator.count()
            except PlaywrightError as exc:
                if _is_selector_error(exc):
                    raise LocatorInvalid(
                        f"选择器非法: {target.describe()}；{str(exc).splitlines()[0]}"
                    ) from exc
                count = 0
            if count == 0:
                continue
            if state == "detached":
                absent = False
                break
            try:
                if locator.first.is_visible():
                    absent = False
                    break
            except PlaywrightError:
                continue
        if absent:
            return
        if time.monotonic() >= deadline:
            raise LocatorTimeout(
                f"等待元素 {state} 超时（{timeout_ms / 1000:.1f}s）: "
                f"{target.describe()}"
            )
        time.sleep(0.1)
