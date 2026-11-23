from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from core.config import BrowserConfig, EnvConfig
from core.console import Console
from core.locator import Target
from core.models import load_flow, validate_flow
from core.recorder import (
    Descriptor,
    PageObjectIndex,
    RecordOptions,
    Recorder,
    StepBuilder,
    ValuePolicy,
    choose_target,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "page.html"


def test_choose_testid_when_unique() -> None:
    descriptor = Descriptor(
        testid="save",
        role="button",
        name="Save",
        text="Save",
        css="#save-btn",
        counts={"testid": 1, "role": 1, "text": 1, "css": 1},
    )
    target = choose_target(descriptor)
    assert target.testid == "save"
    assert target.css is None


def test_fall_back_to_role_then_text_then_css() -> None:
    role = choose_target(
        Descriptor(
            testid="delete",
            role="button",
            name="Delete",
            text="Delete",
            css="button:nth-of-type(2)",
            counts={"testid": 3, "role": 1, "text": 3, "css": 1},
        )
    )
    assert role.role == "button" and role.name == "Delete"

    text = choose_target(
        Descriptor(
            testid="delete",
            role="button",
            name="Delete",
            text="Delete",
            css="button:nth-of-type(2)",
            counts={"testid": 3, "role": 2, "text": 1, "css": 1},
        )
    )
    assert text.text == "Delete" and text.exact is True

    css = choose_target(
        Descriptor(
            testid="delete",
            role="button",
            name="Delete",
            text="Delete",
            css="button:nth-of-type(2)",
            counts={"testid": 3, "role": 2, "text": 2, "css": 1},
        )
    )
    assert css.css == "button:nth-of-type(2)"


def test_frame_scope_is_attached() -> None:
    target = choose_target(
        Descriptor(
            testid="frame-save",
            is_top=False,
            frame_name="editor",
            counts={"testid": 1},
        )
    )
    assert target.testid == "frame-save"
    assert target.frame is not None
    assert target.frame.name == "editor"


def test_consecutive_fill_is_merged() -> None:
    builder = StepBuilder()
    target = Target(testid="username")
    builder.add_fill(target, "a", "输入用户名")
    builder.add_fill(target, "ab", "输入用户名")
    assert len(builder.steps) == 1
    assert builder.steps[0]["value"] == "ab"

    builder.add("click", name="点击登录", target=Target(testid="login-button"))
    builder.add_fill(target, "abc", "输入用户名")
    assert len(builder.steps) == 3


def test_sensitive_values_become_env_placeholders() -> None:
    env = EnvConfig(
        name="dev",
        vars={"username": "standard_user", "password": "secret_sauce"},
    )
    warnings: list[str] = []
    policy = ValuePolicy(env, warnings.append)

    assert policy.for_input("secret_sauce", "password", "password") == "{{env.password}}"
    # 非敏感字段保持字面量，不再按值反查
    assert policy.for_input("standard_user", "user-name", "text") == "standard_user"
    assert policy.for_input("literal", "q", "text") == "literal"
    assert warnings == []


def test_sensitive_field_gets_field_specific_placeholder() -> None:
    warnings: list[str] = []
    policy = ValuePolicy(
        EnvConfig(name="dev", vars={"password": "secret_sauce"}), warnings.append
    )
    value = policy.for_input("generated-key", "decrypt-password", "password")
    assert value == "{{env.decrypt_password}}"
    assert warnings and "decrypt_password" in warnings[0]


def test_dynamic_text_is_rejected_for_locators() -> None:
    cipher = "6Qn29UnXhpcFKW7qx+sD7c39WGdQyi62UXaXrIrWKeSb6XDICGQZ21swqdxCLMr8"
    target = choose_target(
        Descriptor(text=cipher, css="#encrypt-output", counts={"text": 1, "css": 1})
    )
    assert target.css == "#encrypt-output"
    assert target.text is None

    numeric = choose_target(
        Descriptor(text="123456", css="#decrypt-output", counts={"text": 1, "css": 1})
    )
    assert numeric.css == "#decrypt-output"
    assert numeric.text is None


def test_within_is_preferred_over_css_when_role_is_ambiguous() -> None:
    descriptor = Descriptor(
        role="button",
        name="随机生成 32 位",
        text="随机生成 32 位",
        css='button[data-generate="encrypt-password"]',
        counts={"role": 3, "text": 3, "css": 1},
        scopes=[
            {
                "target": {"css": "#encrypt-form"},
                "counts": {"role": 1, "text": 1},
            }
        ],
    )
    target = choose_target(descriptor)
    assert target.role == "button"
    assert target.name == "随机生成 32 位"
    assert target.within is not None
    assert target.within.css == "#encrypt-form"


def test_locator_names_are_readable() -> None:
    builder = StepBuilder()
    assert builder.register(Target(css="#encrypt-output")) == "encrypt-output"
    assert (
        builder.register(Target(role="button", name="复制", within=Target(css="#encrypt-result-box")))
        == "encrypt-result-box-button-复制"
    )
    assert (
        builder.register(Target(css='button[data-copy-key="encrypt-password"]'))
        == "encrypt-password"
    )


def test_extract_then_paste_references_variable() -> None:
    recorder = Recorder(REPO_ROOT, EnvConfig(name="dev"))
    recorder.builder = StepBuilder()
    recorder.values = ValuePolicy(recorder.env, recorder._warn)
    key = "a" * 32

    recorder._handle(
        {
            "type": "extract",
            "target": {
                "css": "#encrypt-password",
                "fieldName": "encrypt-password",
                "inputType": "password",
                "form": True,
                "counts": {"css": 1},
            },
            "value": key,
            "form": True,
        }
    )
    recorder._handle(
        {
            "type": "fill",
            "target": {
                "css": "#decrypt-password",
                "fieldName": "decrypt-password",
                "inputType": "password",
                "form": True,
                "counts": {"css": 1},
            },
            "value": key,
        }
    )

    assert recorder.builder.steps[0]["action"] == "extract"
    assert recorder.builder.steps[0]["as"] == "encrypt_password"
    assert recorder.builder.steps[0]["attr"] == "value"
    assert recorder.builder.steps[1]["value"] == "{{encrypt_password}}"


def test_assert_input_value_is_generated() -> None:
    recorder = Recorder(REPO_ROOT, EnvConfig(name="dev"))
    recorder.builder = StepBuilder()
    recorder.values = ValuePolicy(recorder.env, recorder._warn)

    recorder._handle(
        {
            "type": "assert",
            "target": {
                "css": "#encrypt-text",
                "fieldName": "encrypt-text",
                "form": True,
                "counts": {"css": 1},
            },
            "value": "123456",
            "form": True,
        }
    )
    step = recorder.builder.steps[0]
    assert step["action"] == "assert"
    assert step["value"] == "123456"
    assert "text" not in step


def test_async_ready_inserts_assert_after_click() -> None:
    recorder = Recorder(REPO_ROOT, EnvConfig(name="dev"))
    recorder.builder = StepBuilder()
    recorder.values = ValuePolicy(recorder.env, recorder._warn)
    target = {
        "css": 'button[data-generate="encrypt-password"]',
        "counts": {"css": 1},
    }

    recorder._handle({"type": "click", "target": target})
    recorder._handle({"type": "async_ready", "target": target})

    actions = [step["action"] for step in recorder.builder.steps]
    assert actions == ["click", "assert"]
    assert recorder.builder.steps[1]["state"] == "enabled"


def test_password_without_env_uses_placeholder_and_warns() -> None:
    warnings: list[str] = []
    policy = ValuePolicy(EnvConfig(name="dev"), warnings.append)
    value = policy.for_input("top-secret", "password", "password")
    assert value == "{{env.password}}"
    assert warnings


def test_page_object_constants_are_reused() -> None:
    index = PageObjectIndex(REPO_ROOT, ["saucedemo"], Console())
    matched = index.match(Target(testid="login-button"))
    assert matched == ("LOGIN_BUTTON", "pages.saucedemo.LOGIN_BUTTON")

    builder = StepBuilder(index)
    ref = builder.register(Target(testid="login-button"))
    assert ref == "LOGIN_BUTTON"
    assert builder.locators["LOGIN_BUTTON"] == "pages.saucedemo.LOGIN_BUTTON"


def test_generated_yaml_can_be_loaded(tmp_path: Path) -> None:
    builder = StepBuilder()
    builder.add("goto", name="打开页面", url="https://example.com")
    builder.add("click", name="点击登录", target=Target(testid="login-button"))
    builder.add_fill(Target(testid="username"), "{{env.username}}", "输入用户名")

    data = builder.flow_data(
        name="demo", env_name="dev", include_steps=[], description="录制测试"
    )
    out = tmp_path / "demo.yaml"
    out.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )

    flow = load_flow(out, tmp_path)
    assert [step.action for step in flow.steps] == ["goto", "click", "fill"]
    assert flow.steps[1].params.target.testid == "login-button"  # type: ignore[attr-defined]
    assert flow.steps[2].params.value == "{{env.username}}"  # type: ignore[attr-defined]
    assert validate_flow(flow, tmp_path) == []


def test_page_object_locator_can_be_loaded(tmp_path: Path) -> None:
    index = PageObjectIndex(REPO_ROOT, ["saucedemo"], Console())
    builder = StepBuilder(index)
    builder.add("click", name="点击登录", target=Target(testid="login-button"))

    data = builder.flow_data(
        name="demo", env_name="dev", include_steps=[], description="录制测试"
    )
    out = tmp_path / "demo.yaml"
    out.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )

    flow = load_flow(out, REPO_ROOT)
    assert flow.locators["LOGIN_BUTTON"].testid == "login-button"
    assert flow.steps[0].params.target.testid == "login-button"  # type: ignore[attr-defined]


def test_include_steps_is_emitted_and_loaded(tmp_path: Path) -> None:
    builder = StepBuilder()
    builder.add("click", name="点击登录", target=Target(testid="login-button"))

    data = builder.flow_data(
        name="demo",
        env_name="dev",
        include_steps=["flows/_partials/saucedemo_login.yaml"],
        description="录制测试",
    )
    out = tmp_path / "demo.yaml"
    out.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )

    flow = load_flow(out, REPO_ROOT)
    assert flow.include_steps == ["flows/_partials/saucedemo_login.yaml"]
    assert flow.steps[0].action == "goto"
    assert flow.steps[-1].action == "click"


def test_record_session_end_to_end(tmp_path: Path, playwright_instance) -> None:  # type: ignore[no-untyped-def]
    env = EnvConfig(
        name="dev",
        browser=BrowserConfig(test_id_attribute="data-test"),
    )
    options = RecordOptions(url=FIXTURE.as_uri(), out=tmp_path / "recorded.yaml", headless=True)
    recorder = Recorder(REPO_ROOT, env)

    autopilot = """
    setTimeout(() => document.querySelector('[data-test=save]').click(), 200);
    setTimeout(() => {
      const input = document.querySelector('[data-test=username]');
      input.value = 'typed-user';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
    }, 450);
    setTimeout(() => {
      document.querySelector('[data-sop-act=assert]').click();
      document.querySelector('#hello').click();
    }, 700);
    setTimeout(() => document.querySelector('#hello').click(), 850);
    setTimeout(() => document.querySelector('[data-sop-act=shot]').click(), 950);
    setTimeout(() => document.querySelector('[data-sop-act=stop]').click(), 1200);
    """

    out = recorder.run(
        options,
        on_ready=lambda page: page.evaluate(autopilot),
        playwright=playwright_instance,
    )
    flow = load_flow(out, REPO_ROOT)

    assert [step.action for step in flow.steps] == [
        "goto",
        "click",
        "fill",
        "assert",
        "screenshot",
    ]
    assert flow.steps[1].params.target.testid == "save"  # type: ignore[attr-defined]
    assert flow.steps[2].params.target.testid == "username"  # type: ignore[attr-defined]
    assert flow.steps[2].params.value == "typed-user"  # type: ignore[attr-defined]
    assert flow.steps[3].params.text == "Hello World"  # type: ignore[attr-defined]
    assert validate_flow(flow, REPO_ROOT) == []
    assert recorder.validation_ok is True


def test_record_extract_and_paste_uses_variable(
    tmp_path: Path, playwright_instance
) -> None:  # type: ignore[no-untyped-def]
    env = EnvConfig(name="dev", browser=BrowserConfig(test_id_attribute="data-test"))
    options = RecordOptions(url=FIXTURE.as_uri(), out=tmp_path / "extract.yaml", headless=True)
    recorder = Recorder(REPO_ROOT, env)
    autopilot = """
    setTimeout(() => {
      document.querySelector('[data-sop-act=extract]').click();
      document.querySelector('#hello').click();
    }, 200);
    setTimeout(() => {
      const input = document.querySelector('[data-test=username]');
      input.value = 'Hello World';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
    }, 500);
    setTimeout(() => document.querySelector('[data-sop-act=stop]').click(), 800);
    """

    out = recorder.run(
        options,
        on_ready=lambda page: page.evaluate(autopilot),
        playwright=playwright_instance,
    )
    flow = load_flow(out, REPO_ROOT)
    assert [step.action for step in flow.steps] == ["goto", "extract", "fill"]
    assert flow.steps[1].params.as_ == "hello"  # type: ignore[attr-defined]
    assert flow.steps[2].params.value == "{{hello}}"  # type: ignore[attr-defined]


def test_paste_value_auto_adds_extract(
    tmp_path: Path, playwright_instance
) -> None:  # type: ignore[no-untyped-def]
    env = EnvConfig(name="dev", browser=BrowserConfig(test_id_attribute="data-test"))
    options = RecordOptions(url=FIXTURE.as_uri(), out=tmp_path / "paste.yaml", headless=True)
    recorder = Recorder(REPO_ROOT, env)
    autopilot = """
    setTimeout(() => {
      const input = document.querySelector('[data-test=username]');
      input.value = 'Hello World';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
    }, 250);
    setTimeout(() => document.querySelector('[data-sop-act=stop]').click(), 700);
    """

    out = recorder.run(
        options,
        on_ready=lambda page: page.evaluate(autopilot),
        playwright=playwright_instance,
    )
    flow = load_flow(out, REPO_ROOT)
    assert [step.action for step in flow.steps] == ["goto", "extract", "fill"]
    assert flow.steps[1].params.target.text == "Hello World"  # type: ignore[attr-defined]
    assert flow.steps[2].params.value == "{{hello}}"  # type: ignore[attr-defined]


def test_async_disabled_button_adds_enabled_assert(
    tmp_path: Path, playwright_instance
) -> None:  # type: ignore[no-untyped-def]
    env = EnvConfig(name="dev", browser=BrowserConfig(test_id_attribute="data-test"))
    options = RecordOptions(url=FIXTURE.as_uri(), out=tmp_path / "async.yaml", headless=True)
    recorder = Recorder(REPO_ROOT, env)
    autopilot = """
    setTimeout(() => document.querySelector('#async-save').click(), 200);
    setTimeout(() => document.querySelector('[data-sop-act=stop]').click(), 1000);
    """

    out = recorder.run(
        options,
        on_ready=lambda page: page.evaluate(autopilot),
        playwright=playwright_instance,
    )
    flow = load_flow(out, REPO_ROOT)
    assert [step.action for step in flow.steps] == ["goto", "click", "assert"]
    assert flow.steps[2].params.state == "enabled"  # type: ignore[attr-defined]


def test_template_url_uses_env_base() -> None:
    recorder = Recorder(REPO_ROOT, EnvConfig(name="dev", base_url="https://example.com"))
    assert (
        recorder._template_url("https://example.com/path?q=1")
        == "{{env.base_url}}/path?q=1"
    )
    assert recorder._template_url("https://other.example/x") == "https://other.example/x"
