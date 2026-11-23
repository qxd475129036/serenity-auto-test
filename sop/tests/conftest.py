from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Browser, Page, sync_playwright

FIXTURE = Path(__file__).parent / "fixtures" / "page.html"


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as playwright:
        playwright.selectors.set_test_id_attribute("data-test")
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance) -> Browser:  # type: ignore[no-untyped-def]
    browser = playwright_instance.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture
def page(browser: Browser) -> Page:
    context = browser.new_context(viewport={"width": 800, "height": 600})
    page = context.new_page()
    page.goto(FIXTURE.as_uri())
    yield page
    context.close()
