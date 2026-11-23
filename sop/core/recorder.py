"""浏览器操作录制器：把真实点击/输入转换成现有流程 YAML。

录制器只负责采集事件、挑选定位并生成数据；执行仍然由 core.engine 完成，
不引入第二套执行内核，也不改变现有流程 schema。
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

import yaml
from pydantic import ValidationError
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, sync_playwright

from .config import EnvConfig
from .console import Console
from .errors import FlowError
from .locator import ARIA_ROLES, FrameSpec, Target
from .models import load_flow, load_page_module, validate_flow
from .redact import slugify

_SENSITIVE_FIELD = re.compile(r"(pass|secret|token|key|credential)", re.IGNORECASE)
_ALNUM_TOKEN = re.compile(r"^[A-Za-z0-9+/=_\-]+$")
_HEX_TOKEN = re.compile(r"^[0-9a-fA-F]+$")


def is_dynamic_text(value: str) -> bool:
    """判断文本是否更像随机数据（密文、token、纯数字 ID），不适合做 text 定位。"""
    text = value.strip()
    if not text or re.search(r"\s", text):
        return False
    if re.fullmatch(r"\d{4,}", text):
        return True
    if len(text) < 24:
        return False
    if _HEX_TOKEN.fullmatch(text):
        return True
    if _ALNUM_TOKEN.fullmatch(text):
        return any(char.isdigit() for char in text) and any(
            char.isalpha() for char in text
        )
    return False


def _selector_hint(css: str) -> str:
    """从 CSS 中提取一个可读名字；没有稳定信息时用短哈希。"""
    id_match = re.search(r"#([A-Za-z_][\w-]*)", css)
    if id_match:
        return id_match.group(1)
    attr_match = re.search(r"\[([\w-]+)=[\"']([^\"']+)[\"']\]", css)
    if attr_match:
        return attr_match.group(2)
    return "css-" + hashlib.md5(css.encode("utf-8")).hexdigest()[:8]


@dataclass
class Descriptor:
    """浏览器脚本回传的元素特征。"""

    testid: str | None = None
    role: str | None = None
    name: str | None = None
    text: str | None = None
    css: str | None = None
    field_name: str | None = None
    input_type: str | None = None
    frame_name: str | None = None
    frame_url: str | None = None
    is_top: bool = True
    form: bool = False
    counts: dict[str, int] = field(default_factory=dict)
    scopes: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Descriptor":
        def text(key: str, limit: int = 200) -> str | None:
            value = payload.get(key)
            if not isinstance(value, str):
                return None
            value = " ".join(value.split())
            return value[:limit] or None

        raw_counts = payload.get("counts")
        counts: dict[str, int] = {}
        if isinstance(raw_counts, dict):
            for key, value in raw_counts.items():
                if isinstance(value, int):
                    counts[str(key)] = value

        scopes: list[dict[str, Any]] = []
        raw_scopes = payload.get("scopes")
        if isinstance(raw_scopes, list):
            for item in raw_scopes[:3]:
                if not isinstance(item, dict):
                    continue
                target = item.get("target")
                if not isinstance(target, dict):
                    continue
                scope_counts: dict[str, int] = {}
                raw_scope_counts = item.get("counts")
                if isinstance(raw_scope_counts, dict):
                    for key, value in raw_scope_counts.items():
                        if isinstance(value, int):
                            scope_counts[str(key)] = value
                scopes.append({"target": target, "counts": scope_counts})

        return cls(
            testid=text("testid"),
            role=text("role", 40),
            name=text("name", 80),
            text=text("text", 200),
            css=text("css", 2000),
            field_name=text("fieldName", 80),
            input_type=text("inputType", 20),
            frame_name=text("frameName", 200),
            frame_url=text("frameUrl", 1000),
            is_top=bool(payload.get("isTop", True)),
            form=bool(payload.get("form", False)),
            counts=counts,
            scopes=scopes,
        )

    def label(self) -> str:
        if self.testid:
            return self.testid
        if self.name and not is_dynamic_text(self.name):
            return self.name
        if self.text and not is_dynamic_text(self.text):
            return self.text
        if self.css:
            hint = _selector_hint(self.css)
            return hint if len(hint) <= 40 else "元素"
        return "元素"


def _frame_spec(descriptor: Descriptor) -> FrameSpec | None:
    if descriptor.is_top:
        return None
    if descriptor.frame_name:
        return FrameSpec(name=descriptor.frame_name)
    if descriptor.frame_url:
        return FrameSpec(url=descriptor.frame_url)
    return None


@dataclass
class Candidate:
    target: Target
    count: int | None


def candidate_targets(descriptor: Descriptor) -> list[Candidate]:
    """按 testid → role/name → within+role/name → text → within+text → css 生成候选。"""
    frame = _frame_spec(descriptor)
    candidates: list[Candidate] = []

    def add(count: int | None, within: Target | None = None, **kwargs: Any) -> None:
        try:
            target = Target(**kwargs)
        except ValidationError:
            return
        updates: dict[str, Any] = {}
        if within is not None:
            updates["within"] = within
        if frame is not None:
            updates["frame"] = frame
        if updates:
            target = target.model_copy(update=updates)
        candidates.append(Candidate(target, count))

    scopes: list[tuple[Target, dict[str, int]]] = []
    for scope in descriptor.scopes:
        try:
            scopes.append((Target.model_validate(scope["target"]), scope["counts"]))
        except (ValidationError, KeyError):
            continue

    if descriptor.testid:
        add(descriptor.counts.get("testid"), testid=descriptor.testid)

    name = descriptor.name
    role_ok = (
        descriptor.role
        and name
        and descriptor.role in ARIA_ROLES
        and not is_dynamic_text(name)
    )
    if role_ok:
        add(descriptor.counts.get("role"), role=descriptor.role, name=name, exact=True)
        for scope, counts in scopes:
            add(
                counts.get("role"),
                within=scope,
                role=descriptor.role,
                name=name,
                exact=True,
            )

    text_ok = bool(descriptor.text and not is_dynamic_text(descriptor.text))
    if text_ok:
        add(descriptor.counts.get("text"), text=descriptor.text, exact=True)
        for scope, counts in scopes:
            add(
                counts.get("text"),
                within=scope,
                text=descriptor.text,
                exact=True,
            )

    if descriptor.css:
        add(descriptor.counts.get("css", 1), css=descriptor.css)
    return candidates


def choose_target(descriptor: Descriptor) -> Target:
    """挑选第一个在录制时唯一命中的策略；都不唯一时退回 CSS。"""
    candidates = candidate_targets(descriptor)
    if not candidates:
        raise FlowError(f"无法为元素生成定位描述: {descriptor}")
    for candidate in candidates:
        if candidate.count is None or candidate.count == 1:
            return candidate.target
    return candidates[-1].target


def target_key(target: Target) -> str:
    data = target.model_dump(exclude_none=True, exclude_defaults=True, mode="json")
    return json.dumps(data, sort_keys=True, ensure_ascii=False)


# ---------------------------------------------------------------- 页面对象复用


class PageObjectIndex:
    """把录制到的定位匹配回 pages/<module>.py 里的常量。"""

    def __init__(
        self, project_root: Path, modules: list[str], console: Console
    ) -> None:
        self._exact: dict[str, tuple[str, str]] = {}
        self._by_testid: dict[str, tuple[str, str]] = {}
        self._by_role: dict[tuple[str, str], tuple[str, str]] = {}
        self._names: set[str] = set()

        for raw in modules:
            module_name = raw[7:] if raw.startswith("pages.") else raw
            try:
                module = load_page_module(module_name, project_root)
            except FlowError as exc:
                console.warn(f"页面对象加载失败: {exc}")
                continue
            for const, value in vars(module).items():
                if const.startswith("_") or not isinstance(value, dict):
                    continue
                try:
                    target = Target.model_validate(value)
                except ValidationError:
                    continue
                name = const
                if name in self._names:
                    name = f"{module_name}.{const}"
                self._names.add(name)
                spec = f"pages.{module_name}.{const}"
                entry = (name, spec)
                self._exact.setdefault(target_key(target), entry)
                if target.testid:
                    self._by_testid.setdefault(target.testid, entry)
                if target.role and target.name:
                    self._by_role.setdefault((target.role, target.name), entry)

    def match(self, target: Target) -> tuple[str, str] | None:
        found = self._exact.get(target_key(target))
        if found:
            return found
        if target.frame is not None or target.within is not None:
            # 页面对象常量通常没有 frame/within，不能为了复用丢掉作用域
            return None
        if target.testid:
            found = self._by_testid.get(target.testid)
            if found:
                return found
        if target.role and target.name:
            return self._by_role.get((target.role, target.name))
        return None


# ---------------------------------------------------------------- 步骤与 YAML


class StepBuilder:
    """把录制事件累积成流程步骤，并去重 locators。"""

    def __init__(self, page_objects: PageObjectIndex | None = None) -> None:
        self.page_objects = page_objects
        self.locators: dict[str, Any] = {}
        self.steps: list[dict[str, Any]] = []
        self.warnings: list[str] = []
        self._index: dict[str, str] = {}
        self._last_fill: str | None = None

    def register(self, target: Target) -> str:
        if self.page_objects is not None:
            matched = self.page_objects.match(target)
            if matched is not None:
                name, spec = matched
                self.locators.setdefault(name, spec)
                return name

        key = target_key(target)
        if key in self._index:
            return self._index[key]

        name = self._unique_name(target)
        self._index[key] = name
        self.locators[name] = target.model_dump(
            exclude_none=True, exclude_defaults=True, mode="json"
        )
        return name

    def _unique_name(self, target: Target) -> str:
        parts: list[str] = []
        if target.within is not None:
            parts.append(self._scope_name(target.within))
        parts.append(self._target_name(target))
        base = slugify("-".join(part for part in parts if part), limit=60) or "target"
        name = base
        counter = 2
        while name in self.locators:
            name = f"{base}-{counter}"
            counter += 1
        return name

    def _scope_name(self, scope: Target) -> str:
        if scope.testid:
            return scope.testid
        if scope.css:
            return _selector_hint(scope.css)
        if scope.role and scope.name:
            return f"{scope.role}-{scope.name}"
        return "scope"

    def _target_name(self, target: Target) -> str:
        if target.testid:
            return target.testid
        if target.role and target.name:
            return f"{target.role}-{target.name}"
        if target.text:
            return target.text
        if target.css:
            return _selector_hint(target.css)
        return "target"

    def add_after_click(self, target: Target, step: dict[str, Any]) -> None:
        """把异步等待插到最近一次同目标点击之后。"""
        ref = self.register(target)
        step = {"target": ref, **step}
        for index in range(len(self.steps) - 1, -1, -1):
            current = self.steps[index]
            if current.get("action") == "click" and current.get("target") == ref:
                self.steps.insert(index + 1, step)
                self._last_fill = None
                return
        self.steps.append(step)
        self._last_fill = None

    def add(
        self,
        action: str,
        *,
        name: str,
        target: Target | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        step: dict[str, Any] = {"action": action, "name": name}
        if target is not None:
            step["target"] = self.register(target)
        step.update(params)
        self.steps.append(step)
        self._last_fill = None
        return step

    def add_fill(self, target: Target, value: str, name: str) -> None:
        ref = self.register(target)
        if (
            self._last_fill == ref
            and self.steps
            and self.steps[-1]["action"] == "fill"
        ):
            self.steps[-1]["value"] = value
            self.steps[-1]["name"] = name
            return
        self.steps.append(
            {"action": "fill", "name": name, "target": ref, "value": value}
        )
        self._last_fill = ref

    def flow_data(
        self,
        *,
        name: str,
        env_name: str,
        include_steps: list[str],
        description: str,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {
            "version": 1,
            "name": name,
            "description": description,
            "env": env_name,
        }
        if include_steps:
            data["include_steps"] = list(include_steps)
        if self.locators:
            data["locators"] = self.locators
        data["steps"] = self.steps
        return data


class ValuePolicy:
    """把敏感输入转换成模板变量；非敏感字段一律保留字面量。"""

    def __init__(self, env: EnvConfig, warn: Callable[[str], None]) -> None:
        self.env = env
        self.warn = warn
        self._reverse: dict[str, str] = {}
        for key, value in env.vars.items():
            if isinstance(value, (str, int, float)):
                text = str(value)
                if len(text) >= 2 and text not in self._reverse:
                    self._reverse[text] = key

    @staticmethod
    def _placeholder(key: str) -> str:
        return "{{env." + key + "}}"

    @staticmethod
    def _field_key(name: str) -> str:
        key = re.sub(r"[^0-9A-Za-z_]+", "_", name).strip("_").lower()
        return key or "secret"

    def is_sensitive(self, field_name: str | None, input_type: str | None) -> bool:
        name = (field_name or "").strip().lower()
        return (input_type or "").lower() == "password" or bool(
            _SENSITIVE_FIELD.search(name)
        )

    def for_input(
        self, value: str, field_name: str | None, input_type: str | None
    ) -> str:
        if not self.is_sensitive(field_name, input_type):
            # 普通测试数据不做按值反查，避免把用户名/明文意外绑定到密码
            return value

        if value and value in self._reverse:
            return self._placeholder(self._reverse[value])

        key = self._field_key(field_name or "")
        if key not in self.env.vars:
            self.warn(
                f"敏感输入未在 env 中找到变量，已写入 "
                f"{{{{env.{key}}}}} 占位；"
                f"请先在 configs/env.{self.env.name}.yaml 中补充 {key}"
            )
        return self._placeholder(key)


# ---------------------------------------------------------------- 录制器


@dataclass
class RecordOptions:
    url: str
    out: Path
    env_name: str = "dev"
    name: str | None = None
    include_steps: list[str] = field(default_factory=list)
    page_objects: list[str] = field(default_factory=list)
    browser: str = "chromium"
    storage_state: str | None = None
    # 测试用：无头录制，且不经过真实桌面操作
    headless: bool = False


class Recorder:
    def __init__(
        self,
        project_root: Path,
        env: EnvConfig,
        console: Console | None = None,
    ) -> None:
        self.project_root = project_root
        self.env = env
        self.console = console or Console()
        self.options: RecordOptions | None = None
        self.page_objects: PageObjectIndex | None = None
        self.builder: StepBuilder | None = None
        self.values: ValuePolicy | None = None
        self.page: Page | None = None
        self.done = False
        self.validation_ok = True
        self._shot_count = 0
        self._warned: set[str] = set()
        self._variables: list[tuple[str, str]] = []
        self._async_seen: set[str] = set()
        self._goto_raw: str | None = None

    # ---- 事件 ----
    def _warn(self, message: str) -> None:
        if message in self._warned:
            return
        self._warned.add(message)
        if self.builder is not None:
            self.builder.warnings.append(message)
        self.console.warn(message)

    def _on_event(self, source: dict[str, Any], payload: Any) -> None:
        try:
            self._handle(payload)
        except Exception as exc:  # noqa: BLE001 - 录制过程中不能因为单个事件崩掉
            self._warn(f"录制事件处理失败: {exc}")

    def _handle(self, payload: Any) -> None:
        if not isinstance(payload, dict) or self.builder is None or self.values is None:
            return

        kind = payload.get("type")
        if kind == "stop":
            self.done = True
            return
        if kind == "screenshot":
            self._shot_count += 1
            self.builder.add("screenshot", name=f"截图 {self._shot_count}")
            return

        descriptor = Descriptor.from_payload(payload.get("target") or {})
        target = choose_target(descriptor)

        if kind == "click":
            self.builder.add("click", name=f"点击 {descriptor.label()}", target=target)
        elif kind == "fill":
            raw_value = payload.get("value")
            text = "" if raw_value is None else str(raw_value)
            variable = self._variable_for_value(text)
            source = payload.get("source")
            if variable is None and isinstance(source, dict):
                variable = self._ensure_variable(Descriptor.from_payload(source), text)
            if variable is not None:
                value = "{{" + variable + "}}"
            else:
                value = self.values.for_input(
                    text, descriptor.field_name, descriptor.input_type
                )
            self.builder.add_fill(target, value, f"输入 {descriptor.label()}")
        elif kind == "extract":
            self._add_extract(payload, descriptor, target)
        elif kind == "async_ready":
            key = target_key(target)
            if key in self._async_seen:
                return
            self._async_seen.add(key)
            self.builder.add_after_click(
                target,
                {
                    "action": "assert",
                    "name": f"等待 {descriptor.label()} 可用",
                    "state": "enabled",
                },
            )
        elif kind == "select":
            label = str(payload.get("label") or "").strip()
            if label:
                self.builder.add(
                    "select",
                    name=f"选择 {label}",
                    target=target,
                    label=label,
                )
            else:
                self.builder.add(
                    "select",
                    name=f"选择 {descriptor.label()}",
                    target=target,
                    value=str(payload.get("value") or ""),
                )
        elif kind == "wait_for":
            self.builder.add(
                "wait_for",
                name=f"等待 {descriptor.label()} 出现",
                target=target,
                state="visible",
            )
        elif kind == "assert":
            if payload.get("value") is not None:
                value = self._template_value(
                    str(payload.get("value") or ""), descriptor
                )
                self.builder.add(
                    "assert",
                    name=f"断言 {descriptor.label()} 的值",
                    target=target,
                    value=value,
                )
            else:
                text = str(payload.get("text") or "").strip()
                if text:
                    self.builder.add(
                        "assert",
                        name=f"断言文本 {text[:40]}",
                        target=target,
                        text=text,
                    )
                else:
                    self.builder.add(
                        "assert",
                        name=f"断言 {descriptor.label()} 可见",
                        target=target,
                        state="visible",
                    )

    def _template_value(self, value: str, descriptor: Descriptor) -> str:
        """优先引用已提取的变量，其次按敏感值规则处理。"""
        variable = self._variable_for_value(value)
        if variable is not None:
            return "{{" + variable + "}}"
        assert self.values is not None
        return self.values.for_input(
            value, descriptor.field_name, descriptor.input_type
        )

    def _variable_for_value(self, value: str) -> str | None:
        if len(value) < 2:
            return None
        for name, stored in reversed(self._variables):
            if stored and stored == value:
                return name
        return None

    def _ensure_variable(self, source: Descriptor, value: str) -> str:
        """粘贴到另一个输入框时，自动补一条 extract 并返回变量名。"""
        assert self.builder is not None
        variable = self._variable_for_value(value)
        if variable is not None:
            return variable
        target = choose_target(source)
        name = self._variable_name(source)
        self._variables.append((name, value))
        params: dict[str, Any] = {"as": name}
        if source.form:
            params["attr"] = "value"
        self.builder.add(
            "extract",
            name=f"提取 {source.label()}",
            target=target,
            **params,
        )
        return name

    def _add_extract(
        self, payload: dict[str, Any], descriptor: Descriptor, target: Target
    ) -> None:
        assert self.builder is not None
        raw_value = payload.get("value")
        value = "" if raw_value is None else str(raw_value)
        name = self._variable_name(descriptor)
        self._variables.append((name, value))
        params: dict[str, Any] = {"as": name}
        if bool(payload.get("form")):
            params["attr"] = "value"
        self.builder.add(
            "extract",
            name=f"提取 {descriptor.label()}",
            target=target,
            **params,
        )

    def _variable_name(self, descriptor: Descriptor) -> str:
        base = descriptor.field_name or ""
        base = re.sub(r"[^0-9A-Za-z_]+", "_", base).strip("_").lower()
        if not base or not base[0].isalpha():
            base = f"value{len(self._variables) + 1}"
        name = base
        counter = 2
        existing = {item[0] for item in self._variables}
        while name in existing:
            name = f"{base}_{counter}"
            counter += 1
        return name

    # ---- 录制主流程 ----
    def run(
        self,
        options: RecordOptions,
        on_ready: Callable[[Page], None] | None = None,
        *,
        playwright: Any = None,
    ) -> Path:
        if playwright is not None:
            return self._run(playwright, options, on_ready)
        with sync_playwright() as session:
            return self._run(session, options, on_ready)

    def _run(
        self,
        playwright: Any,
        options: RecordOptions,
        on_ready: Callable[[Page], None] | None,
    ) -> Path:
        self.options = options
        self.page_objects = PageObjectIndex(
            self.project_root, options.page_objects, self.console
        )
        self.builder = StepBuilder(self.page_objects)
        self.values = ValuePolicy(self.env, self._warn)

        out = options.out
        if not out.is_absolute():
            out = self.project_root / out

        browser_type = getattr(playwright, options.browser, None)
        if browser_type is None:
            raise FlowError(f"不支持的浏览器: {options.browser}")
        browser = browser_type.launch(
            headless=options.headless, slow_mo=self.env.browser.slow_mo
        )
        context_kwargs: dict[str, Any] = {
            "viewport": self.env.browser.viewport_dict(),
            "locale": self.env.browser.locale,
        }
        state_value = options.storage_state or self.env.storage_state
        if state_value:
            state_path = Path(state_value)
            if not state_path.is_absolute():
                state_path = self.project_root / state_path
            if state_path.exists():
                context_kwargs["storage_state"] = str(state_path)

        context = browser.new_context(**context_kwargs)
        page = context.new_page()
        self.page = page
        page.expose_binding("__sop_emit", self._on_event)
        page.add_init_script(build_init_script(self.env.browser.test_id_attribute))
        page.on("dialog", lambda dialog: dialog.dismiss())

        self.console.header(f"sop record · {options.url} · {options.browser}")
        self.console.line(
            "在浏览器里正常操作；右下角浮层可截图/等待/断言/提取/结束，"
            "快捷键 Alt+S / Alt+W / Alt+A / Alt+X / Alt+E。"
        )
        self.console.line()

        page.goto(options.url, wait_until="domcontentloaded", timeout=60_000)
        self._goto_raw = options.url
        self.builder.add("goto", name="打开页面", url=self._template_url(options.url))

        if on_ready is not None:
            on_ready(page)

        try:
            while not self.done:
                page.wait_for_timeout(150)
                if page.is_closed():
                    break
        except PlaywrightError:
            pass
        except KeyboardInterrupt:
            self.console.warn("录制已中断，保存已录内容")

        result = self._write(options, out)

        try:
            context.close()
        except PlaywrightError:
            pass
        try:
            browser.close()
        except PlaywrightError:
            pass

        return result

    def _template_url(self, url: str) -> str:
        base = (self.env.base_url or "").rstrip("/")
        if base and url == base:
            return "{{env.base_url}}"
        if base and url.startswith(base + "/"):
            return "{{env.base_url}}" + url[len(base) :]
        return url

    def _write(self, options: RecordOptions, out: Path) -> Path:
        assert self.builder is not None
        name = options.name or slugify(out.stem or "recorded")
        data = self.builder.flow_data(
            name=name,
            env_name=options.env_name,
            include_steps=options.include_steps,
            description="由 sop record 录制",
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000),
            encoding="utf-8",
        )
        self.console.line()
        self.console.line(f"已写入流程: {out}")

        try:
            flow = load_flow(out, self.project_root)
        except FlowError as exc:
            self.validation_ok = False
            self.console.error(f"录制结果校验失败:\n{exc}")
            return out

        problems = validate_flow(flow, self.project_root)
        if problems:
            self.validation_ok = False
            for problem in problems:
                self.console.error(problem)
        else:
            self.console.line(
                self.console.green(f"✔ dry-run 通过：{len(flow.steps)} 步")
            )

        try:
            shown = out.relative_to(self.project_root)
        except ValueError:
            shown = out
        self.console.line(f"运行: sop run {shown} --env {options.env_name}")

        self._print_env_hint(options.env_name)
        return out

    def _print_env_hint(self, env_name: str) -> None:
        """说明 goto 是否复用了 env.base_url，以及应该配置哪个 env 文件。"""
        if not self._goto_raw:
            return
        base = (self.env.base_url or "").rstrip("/")
        if base and (
            self._goto_raw == base or self._goto_raw.startswith(base + "/")
        ):
            return

        origin = urlparse(self._goto_raw)
        suggested = f"{origin.scheme}://{origin.netloc}" if origin.netloc else self._goto_raw
        self.console.warn(
            f"goto 使用 {self._goto_raw}，与 env.{env_name}.base_url 不一致；"
            f"建议在 configs/env.{env_name}.yaml 配置 base_url: {suggested}"
        )


# ---------------------------------------------------------------- 页面脚本


def build_init_script(test_id_attribute: str) -> str:
    """生成注入到每个页面/iframe 的采集脚本。"""
    attr = json.dumps(test_id_attribute)
    return (
        _INIT_SCRIPT.replace("__SOP_TESTID_ATTR__", attr)
        .replace("__SOP_OVERLAY_ATTR__", json.dumps("data-sop-overlay"))
    )


_INIT_SCRIPT = r"""
(() => {
  if (window.__sopInstalled) return;
  window.__sopInstalled = true;

  const ATTR = __SOP_TESTID_ATTR__;
  const OVERLAY = __SOP_OVERLAY_ATTR__;
  const isTop = window.top === window;

  let mode = null;
  let recorded = 0;
  let overlayStatus = null;
  let lastClickAt = 0;
  const inputTimers = new WeakMap();

  const collapse = (value) => String(value || '').replace(/\s+/g, ' ').trim();

  function emit(type, target, extra, silent) {
    const payload = Object.assign({
      type,
      isTop,
      frameName: window.name || '',
      frameUrl: location.href
    }, extra || {});
    if (target) payload.target = target;
    try { window.__sop_emit(payload); } catch (error) {}
    if (!silent) {
      recorded += 1;
      if (overlayStatus) overlayStatus.textContent = '已记录 ' + recorded + ' 个动作';
    }
  }

  function isDynamicValue(value) {
    const text = collapse(value);
    if (!text || /\s/.test(text)) return false;
    if (/^\d{4,}$/.test(text)) return true;
    if (text.length < 24) return false;
    if (/^[0-9a-fA-F]+$/.test(text)) return true;
    if (/^[A-Za-z0-9+/=_-]+$/.test(text)) {
      return /\d/.test(text) && /[A-Za-z]/.test(text);
    }
    return false;
  }

  function cssEscape(value) {
    if (window.CSS && CSS.escape) return CSS.escape(value);
    return String(value).replace(/[^a-zA-Z0-9_-]/g, (ch) => '\\' + ch);
  }

  function attrSelector(name, value) {
    return '[' + name + '="' + String(value).replace(/\\/g, '\\\\').replace(/"/g, '\\"') + '"]';
  }

  const PREFERRED_DATA = [
    'data-testid', 'data-test', 'data-qa', 'data-cy',
    'data-id', 'data-key', 'data-name', 'data-type'
  ];

  function stableAttr(el) {
    const names = [];
    for (const name of PREFERRED_DATA) {
      if (el.hasAttribute(name)) names.push(name);
    }
    for (const attr of el.attributes) {
      if (attr.name.startsWith('data-') && attr.name !== ATTR &&
          !attr.name.startsWith('data-sop') && !names.includes(attr.name)) {
        names.push(attr.name);
      }
    }
    for (const name of names) {
      const value = collapse(el.getAttribute(name));
      if (!value || value.length > 80 || isDynamicValue(value)) continue;
      const selector = el.tagName.toLowerCase() + attrSelector(name, value);
      try {
        if (document.querySelectorAll(selector).length === 1) return selector;
      } catch (error) {}
    }
    return null;
  }

  function inferRole(el) {
    const explicit = collapse(el.getAttribute('role'));
    if (explicit) return explicit;
    const tag = el.tagName.toLowerCase();
    if (tag === 'button') return 'button';
    if (tag === 'a' && el.hasAttribute('href')) return 'link';
    if (tag === 'select') return 'combobox';
    if (tag === 'textarea') return 'textbox';
    if (tag === 'input') {
      const type = (el.getAttribute('type') || 'text').toLowerCase();
      if (type === 'checkbox') return 'checkbox';
      if (type === 'radio') return 'radio';
      if (['submit', 'button', 'reset'].includes(type)) return 'button';
      if (type === 'search') return 'searchbox';
      return 'textbox';
    }
    if (/^h[1-6]$/.test(tag)) return 'heading';
    if (tag === 'img') return 'img';
    if (tag === 'li') return 'listitem';
    if (tag === 'ul' || tag === 'ol') return 'list';
    if (tag === 'table') return 'table';
    if (tag === 'nav') return 'navigation';
    if (tag === 'main') return 'main';
    return null;
  }

  function accessibleName(el, role) {
    const aria = collapse(el.getAttribute('aria-label'));
    if (aria) return aria.slice(0, 80);
    const labelled = el.getAttribute('aria-labelledby');
    if (labelled) {
      const text = labelled.split(/\s+/).map((id) => {
        const node = document.getElementById(id);
        return node ? collapse(node.innerText) : '';
      }).join(' ');
      if (text) return text.slice(0, 80);
    }
    if (el.labels && el.labels.length) {
      const text = collapse(el.labels[0].innerText);
      if (text) return text.slice(0, 80);
    }
    if (el.tagName === 'IMG') {
      const alt = collapse(el.getAttribute('alt'));
      if (alt) return alt.slice(0, 80);
    }
    if (['textbox', 'searchbox', 'combobox'].includes(role)) {
      const placeholder = collapse(el.getAttribute('placeholder'));
      if (placeholder) return placeholder.slice(0, 80);
    }
    const text = collapse(el.innerText);
    if (text && text.length <= 80) return text;
    const title = collapse(el.getAttribute('title'));
    return title.slice(0, 80);
  }

  function uniqueCss(el) {
    if (el.id) {
      const byId = '#' + cssEscape(el.id);
      try {
        if (document.querySelectorAll(byId).length === 1) return byId;
      } catch (error) {}
    }
    const own = stableAttr(el);
    if (own) return own;

    const parts = [];
    let node = el;
    while (node && node.nodeType === 1) {
      if (node.id) {
        const byId = '#' + cssEscape(node.id);
        try {
          if (document.querySelectorAll(byId).length === 1) {
            parts.unshift(byId);
            break;
          }
        } catch (error) {}
      }
      const stable = stableAttr(node);
      if (stable) {
        parts.unshift(stable);
        break;
      }
      let part = node.tagName.toLowerCase();
      const parent = node.parentElement;
      if (parent) {
        const same = Array.from(parent.children).filter(
          (item) => item.tagName === node.tagName
        );
        if (same.length > 1) part += ':nth-of-type(' + (same.indexOf(node) + 1) + ')';
      }
      parts.unshift(part);
      const candidate = parts.join(' > ');
      try {
        if (document.querySelectorAll(candidate).length === 1) return candidate;
      } catch (error) {}
      node = parent;
    }
    return parts.join(' > ');
  }

  function stableScope(node) {
    const testid = collapse(node.getAttribute(ATTR));
    if (testid) {
      try {
        if (document.querySelectorAll(attrSelector(ATTR, testid)).length === 1) {
          return { testid };
        }
      } catch (error) {}
    }
    if (node.id) {
      const byId = '#' + cssEscape(node.id);
      try {
        if (document.querySelectorAll(byId).length === 1) return { css: byId };
      } catch (error) {}
    }
    const stable = stableAttr(node);
    if (stable) return { css: stable };
    return null;
  }

  function ancestorScopes(el, role, name, text) {
    const scopes = [];
    let node = el.parentElement;
    let depth = 0;
    while (node && node !== document.body && depth < 3) {
      const scope = stableScope(node);
      if (scope) {
        const counts = {};
        if (role && name) counts.role = countRoleName(role, name, node);
        if (text) counts.text = countText(text, node);
        scopes.push({ target: scope, counts });
      }
      node = node.parentElement;
      depth += 1;
    }
    return scopes;
  }

  function countText(text, root) {
    let count = 0;
    const nodes = (root || document).querySelectorAll('*');
    for (const node of nodes) {
      if (collapse(node.innerText) === text) count += 1;
    }
    return count;
  }

  function countRoleName(role, name, root) {
    let count = 0;
    const nodes = (root || document).querySelectorAll('*');
    for (const node of nodes) {
      if (inferRole(node) !== role) continue;
      if (accessibleName(node, role) === name) count += 1;
    }
    return count;
  }

  function describe(el) {
    const testid = collapse(el.getAttribute(ATTR));
    const role = inferRole(el);
    const name = accessibleName(el, role);
    const rawText = collapse(el.innerText);
    const text = rawText && rawText.length <= 200 && !isDynamicValue(rawText) ? rawText : '';
    const css = uniqueCss(el);
    const counts = {};
    if (testid) {
      try { counts.testid = document.querySelectorAll(attrSelector(ATTR, testid)).length; } catch (error) {}
    }
    if (role && name && !isDynamicValue(name)) counts.role = countRoleName(role, name);
    if (text) counts.text = countText(text);
    if (css) counts.css = 1;
    return {
      testid: testid || null,
      role: role || null,
      name: name || null,
      text: text || null,
      css: css || null,
      fieldName: el.id || el.getAttribute('name') || null,
      inputType: (el.getAttribute('type') || '').toLowerCase() || null,
      form: ['INPUT', 'TEXTAREA', 'SELECT'].includes(el.tagName),
      counts: counts,
      scopes: ancestorScopes(el, role, name, text)
    };
  }

  function findValueSource(value, currentEl) {
    const wanted = String(value || '');
    if (wanted.length < 8) return null;
    const candidates = [];
    for (const node of document.querySelectorAll('input,textarea,pre,code,[id]')) {
      if (node === currentEl) continue;
      const current = (node.tagName === 'INPUT' || node.tagName === 'TEXTAREA')
        ? node.value
        : collapse(node.innerText);
      if (current !== wanted) continue;
      if (!node.id && !stableAttr(node) && !node.getAttribute(ATTR)) continue;
      candidates.push(node);
    }
    if (!candidates.length) return null;
    candidates.sort((left, right) => (right.id ? 1 : 0) - (left.id ? 1 : 0));
    return describe(candidates[0]);
  }

  function actionable(node) {
    if (!(node instanceof Element)) return null;
    return node.closest(
      'a,button,input,select,textarea,label,[role="button"],[role="link"],' +
      '[role="menuitem"],[role="tab"],[role="checkbox"],[role="radio"]'
    );
  }

  function toast(message) {
    if (!isTop || !document.body) return;
    const node = document.createElement('div');
    node.setAttribute(OVERLAY, '1');
    node.textContent = message;
    node.style.cssText = 'position:fixed;right:16px;bottom:270px;z-index:2147483647;' +
      'background:#111827;color:#fff;padding:6px 10px;border-radius:6px;' +
      'font:13px/1.4 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;opacity:.95';
    document.body.appendChild(node);
    setTimeout(() => node.remove(), 1600);
  }

  function setMode(next) {
    mode = next;
    const labels = {
      assert: '下一次点击：断言文本',
      wait: '下一次点击：等待出现',
      extract: '下一次点击：提取变量'
    };
    const hints = {
      assert: '请点击要断言的元素',
      wait: '请点击要等待的元素',
      extract: '请点击要提取文本/值的元素'
    };
    if (overlayStatus) overlayStatus.textContent = labels[next] || '';
    toast(hints[next] || '');
  }

  function takeMode() {
    const current = mode;
    mode = null;
    if (overlayStatus) overlayStatus.textContent = '已记录 ' + recorded + ' 个动作';
    return current;
  }

  function recordShot() {
    emit('screenshot');
    if (Date.now() - lastClickAt < 1200) {
      toast('截图已记录；刚点击过异步操作时，建议先用「等待出现」再截图');
    } else {
      toast('已记录截图');
    }
  }

  function watchDisabled(el, target) {
    let sawDisabled = false;
    let elapsed = 0;
    const timer = setInterval(() => {
      elapsed += 50;
      if (el.disabled) {
        sawDisabled = true;
      } else if (sawDisabled) {
        clearInterval(timer);
        emit('async_ready', target, {}, true);
      } else if (elapsed > 500) {
        clearInterval(timer);
      }
    }, 50);
  }

  function installOverlay() {
    if (!isTop || !document.body) return;
    const box = document.createElement('div');
    box.setAttribute(OVERLAY, '1');
    box.style.cssText = 'position:fixed;right:16px;bottom:16px;z-index:2147483647;' +
      'display:flex;flex-direction:column;gap:6px;padding:10px;border-radius:10px;' +
      'background:rgba(17,24,39,.92);color:#fff;width:190px;' +
      'font:13px/1.4 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;' +
      'box-shadow:0 8px 24px rgba(0,0,0,.35)';
    const title = document.createElement('div');
    title.setAttribute(OVERLAY, '1');
    title.textContent = 'sop 录制中';
    title.style.cssText = 'font-weight:600';
    box.appendChild(title);
    const status = document.createElement('div');
    status.setAttribute(OVERLAY, '1');
    status.textContent = '点击页面开始录制';
    status.style.cssText = 'opacity:.75;margin-bottom:4px';
    box.appendChild(status);
    overlayStatus = status;

    const buttons = [
      ['shot', '截图 (Alt+S)'],
      ['wait', '等待出现 (Alt+W)'],
      ['assert', '断言文本 (Alt+A)'],
      ['extract', '提取变量 (Alt+X)'],
      ['stop', '结束录制 (Alt+E)']
    ];
    buttons.forEach(([action, label]) => {
      const button = document.createElement('button');
      button.setAttribute(OVERLAY, '1');
      button.setAttribute('data-sop-act', action);
      button.type = 'button';
      button.textContent = label;
      button.style.cssText = 'cursor:pointer;border:0;border-radius:6px;padding:6px 8px;' +
        'color:#fff;font-size:13px;background:' + (action === 'stop' ? '#dc2626' : '#2563eb');
      button.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        if (action === 'shot') recordShot();
        else if (action === 'stop') {
          status.textContent = '正在保存…';
          emit('stop');
        } else {
          setMode(action);
        }
      }, true);
      box.appendChild(button);
    });
    document.body.appendChild(box);
  }

  document.addEventListener('click', (event) => {
    if (event.button !== 0 || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    const raw = event.target;
    if (!(raw instanceof Element) || raw.closest('[' + OVERLAY + ']')) return;

    const pending = mode;
    const interactive = actionable(raw);
    if (!interactive && !pending) return;
    let el = interactive || raw;

    if (!pending && el.tagName === 'LABEL' && el.control) {
      const control = el.control;
      const controlType = (control.getAttribute('type') || '').toLowerCase();
      if (controlType === 'checkbox' || controlType === 'radio') el = control;
    }
    const tag = el.tagName;
    const inputType = (el.getAttribute('type') || '').toLowerCase();
    if (!pending) {
      if (tag === 'SELECT' || tag === 'LABEL') return;
      if ((tag === 'INPUT' || tag === 'TEXTAREA') &&
          !['checkbox', 'radio', 'submit', 'button', 'reset'].includes(inputType)) return;
    }

    const target = describe(el);
    const current = takeMode();
    const isForm = ['INPUT', 'TEXTAREA', 'SELECT'].includes(tag);
    if (current === 'assert') {
      if (isForm) {
        emit('assert', target, { value: el.value || '', form: true });
      } else {
        emit('assert', target, {
          text: collapse(el.innerText).slice(0, 200),
          form: false
        });
      }
    } else if (current === 'wait') {
      emit('wait_for', target);
    } else if (current === 'extract') {
      emit('extract', target, {
        value: isForm ? (el.value || '') : collapse(el.innerText).slice(0, 4000),
        form: isForm
      });
    } else {
      lastClickAt = Date.now();
      emit('click', target);
      watchDisabled(el, target);
    }
  }, true);

  document.addEventListener('input', (event) => {
    const el = event.target;
    if (!(el instanceof Element) || el.closest('[' + OVERLAY + ']')) return;
    if (el.tagName !== 'INPUT' && el.tagName !== 'TEXTAREA') return;
    const type = (el.getAttribute('type') || 'text').toLowerCase();
    if (['checkbox', 'radio', 'file', 'submit', 'button', 'reset'].includes(type)) return;
    clearTimeout(inputTimers.get(el));
    inputTimers.set(el, setTimeout(() => {
      emit('fill', describe(el), { value: el.value });
    }, 300));
  }, true);

  document.addEventListener('change', (event) => {
    const el = event.target;
    if (!(el instanceof Element) || el.closest('[' + OVERLAY + ']')) return;
    if (el.tagName === 'SELECT') {
      const option = el.selectedOptions && el.selectedOptions[0];
      emit('select', describe(el), {
        label: option ? collapse(option.text) : '',
        value: el.value
      });
      return;
    }
    if (el.tagName !== 'INPUT' && el.tagName !== 'TEXTAREA') return;
    const type = (el.getAttribute('type') || 'text').toLowerCase();
    if (['checkbox', 'radio', 'file', 'submit', 'button', 'reset'].includes(type)) return;
    clearTimeout(inputTimers.get(el));
    emit('fill', describe(el), {
      value: el.value,
      source: findValueSource(el.value, el)
    });
  }, true);

  window.addEventListener('keydown', (event) => {
    if (!event.altKey || event.ctrlKey || event.metaKey) return;
    if (event.code === 'KeyS') {
      event.preventDefault();
      recordShot();
    } else if (event.code === 'KeyW') {
      event.preventDefault();
      setMode('wait');
    } else if (event.code === 'KeyA') {
      event.preventDefault();
      setMode('assert');
    } else if (event.code === 'KeyX') {
      event.preventDefault();
      setMode('extract');
    } else if (event.code === 'KeyE') {
      event.preventDefault();
      emit('stop');
    }
  }, true);

  window.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && event.target && event.target.tagName === 'INPUT') {
      toast('Enter 提交不会被录制，请点击提交按钮');
    }
  }, true);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', installOverlay, { once: true });
  } else {
    installOverlay();
  }
})();
"""


def default_output(project_root: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return project_root / "flows" / f"recorded_{stamp}.yaml"
