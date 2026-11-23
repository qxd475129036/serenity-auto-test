from __future__ import annotations

import pytest
from playwright.sync_api import Page
from pydantic import ValidationError

from core.errors import LocatorInvalid, StepAmbiguity
from core.locator import FrameSpec, Target, resolve, wait_absent


def test_target_requires_a_strategy() -> None:
    with pytest.raises(ValidationError):
        Target()


def test_first_and_index_are_exclusive() -> None:
    with pytest.raises(ValidationError):
        Target(testid="delete", first=True, index=2)


def test_priority_testid_first(page: Page) -> None:
    target = Target(
        testid="save",
        role="button",
        name="Does Not Exist",
        css="#does-not-exist",
    )
    resolved = resolve(page, target, 1000)
    assert resolved.strategy == "testid"
    assert resolved.first.inner_text() == "Save"


def test_fallback_to_css(page: Page) -> None:
    resolved = resolve(page, Target(testid="missing", css="#save-btn"), 1000)
    assert resolved.strategy == "css"


def test_role_and_name(page: Page) -> None:
    resolved = resolve(page, Target(role="button", name="Login"), 1000)
    assert resolved.strategy == "role"
    assert resolved.first.get_attribute("id") == "login-btn"


def test_text_strategy(page: Page) -> None:
    resolved = resolve(page, Target(text="Hello World"), 1000)
    assert resolved.strategy == "text"


def test_ambiguity_fails_by_default(page: Page) -> None:
    with pytest.raises(StepAmbiguity) as info:
        resolve(page, Target(testid="delete"), 1000)
    assert "3 个元素" in str(info.value)


def test_first_resolves_ambiguity(page: Page) -> None:
    resolved = resolve(page, Target(testid="delete", first=True), 1000)
    assert resolved.first.inner_text() == "Delete A"


def test_index_resolves_ambiguity(page: Page) -> None:
    resolved = resolve(page, Target(testid="delete", index=2), 1000)
    assert resolved.first.inner_text() == "Delete B"


def test_multiple_allows_all(page: Page) -> None:
    resolved = resolve(
        page, Target(testid="delete"), 1000, state="attached", multiple=True
    )
    assert resolved.locator.count() == 3


def test_wait_absent(page: Page) -> None:
    wait_absent(page, Target(testid="missing"), 500, state="detached")
    wait_absent(page, Target(testid="hidden"), 500, state="hidden")


def test_frame_by_css(page: Page) -> None:
    resolved = resolve(page, Target(frame="#editor-frame", testid="frame-save"), 1000)
    assert resolved.strategy == "frame(css=#editor-frame) > testid"
    assert resolved.first.inner_text() == "Frame Save"


def test_frame_by_name(page: Page) -> None:
    resolved = resolve(page, Target(frame={"name": "editor"}, testid="frame-save"), 2000)
    assert resolved.strategy == 'frame(name="editor") > testid'
    assert resolved.first.inner_text() == "Frame Save"


def test_frame_by_url(page: Page) -> None:
    resolved = resolve(
        page, Target(frame={"url": "*frame.html"}, testid="frame-save"), 2000
    )
    assert resolved.first.inner_text() == "Frame Save"


def test_frame_wait_absent(page: Page) -> None:
    wait_absent(
        page,
        Target(frame="#editor-frame", testid="missing"),
        500,
        state="detached",
    )


def test_within_container(page: Page) -> None:
    target = Target(within=Target(testid="row", index=2), testid="row-delete")
    resolved = resolve(page, target, 1000)
    assert resolved.strategy.startswith("within(")
    assert resolved.first.inner_text() == "Delete Row B"


def test_frame_spec_requires_exactly_one_selector() -> None:
    with pytest.raises(ValidationError):
        FrameSpec()
    with pytest.raises(ValidationError):
        FrameSpec(css="#frame", name="editor")


@pytest.mark.parametrize(
    "kwargs",
    [
        {"css": "##save-btn"},
        {"css": "div["},
        {"css": "div, "},
        {"xpath": "[//div]"},
    ],
)
def test_invalid_selector_rejected_at_load(kwargs: dict) -> None:
    with pytest.raises(ValidationError):
        Target(**kwargs)


def test_runtime_invalid_selector_raises_locator_invalid(page: Page) -> None:
    with pytest.raises(LocatorInvalid):
        resolve(page, Target(css="div[foo=]"), 1000)
