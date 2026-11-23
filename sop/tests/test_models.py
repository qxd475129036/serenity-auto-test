from __future__ import annotations

from pathlib import Path

import pytest

from core.errors import FlowError
from core.models import load_flow, validate_flow

REPO_ROOT = Path(__file__).resolve().parents[1]
FLOWS = REPO_ROOT / "flows"


def test_load_example_login_with_page_objects() -> None:
    flow = load_flow(FLOWS / "01_login.yaml", REPO_ROOT)
    assert flow.version == 1
    assert flow.name == "01_login"
    assert len(flow.steps) == 12
    assert flow.locators["login.submit"].testid == "login-button"
    # include_steps 把共享登录片段放在前面
    assert flow.steps[0].action == "goto"
    assert flow.steps[1].action == "assert"
    assert flow.steps[1].params.target.testid == "login-button"  # type: ignore[attr-defined]
    assert validate_flow(flow, REPO_ROOT) == []


def test_include_steps_merges_fragment() -> None:
    flow = load_flow(FLOWS / "02_add_to_cart.yaml", REPO_ROOT)
    assert len(flow.steps) == 10
    assert flow.steps[6].action == "click"
    assert flow.steps[6].key is True


def test_requires_and_storage_state() -> None:
    flow = load_flow(FLOWS / "03_reuse_login.yaml", REPO_ROOT)
    assert flow.requires == ["01_login"]
    assert flow.storage_state == ".auth/saucedemo.json"
    assert flow.steps[1].params.target.testid == "inventory-container"  # type: ignore[attr-defined]


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "flow.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_unknown_locator_ref(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        """
name: broken
locators:
  known: {testid: save}
steps:
  - action: click
    target: {ref: missing}
""",
    )
    with pytest.raises(FlowError, match="locators.missing"):
        load_flow(path, tmp_path)


def test_unknown_action(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        """
name: broken
steps:
  - action: not-an-action
""",
    )
    with pytest.raises(FlowError, match="未知动作"):
        load_flow(path, tmp_path)


def test_unsupported_version(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        """
version: 99
name: future
steps:
  - action: goto
    url: https://example.com
""",
    )
    with pytest.raises(FlowError, match="不支持的流程版本"):
        load_flow(path, tmp_path)


def test_retry_on_timeout_parsed(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        """
name: retry
steps:
  - action: click
    target: {testid: save}
    retry_on_timeout: true
""",
    )
    flow = load_flow(path, tmp_path)
    assert flow.steps[0].retry_on_timeout is True


def test_missing_page_module(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        """
name: broken
locators:
  submit: pages.nope.BUTTON
steps:
  - action: click
    target: submit
""",
    )
    with pytest.raises(FlowError, match="页面对象模块不存在"):
        load_flow(path, tmp_path)
