from __future__ import annotations

import pytest

from core.errors import TemplateError
from core.template import TemplateContext


def test_env_and_vars_lookup() -> None:
    context = TemplateContext(
        {"env": {"base_url": "https://example.com", "user": "demo"}, "vars": {}}
    )
    context.set_var("count", 3)
    assert context.render("{{env.base_url}}/x") == "https://example.com/x"
    assert context.render("{{user}}") == "demo"
    assert context.render("{{count}}") == 3
    assert context.render("{{vars.count}}") == 3


def test_single_placeholder_preserves_type() -> None:
    context = TemplateContext()
    context.set_var("items", ["a", "b"])
    assert context.render("{{items}}") == ["a", "b"]


def test_embedded_complex_type_is_error() -> None:
    context = TemplateContext()
    context.set_var("items", ["a"])
    with pytest.raises(TemplateError):
        context.render("count: {{items}}")


def test_missing_variable_is_error() -> None:
    with pytest.raises(TemplateError, match="nope"):
        TemplateContext().render("{{nope}}")


def test_recursive_render() -> None:
    context = TemplateContext({"env": {"name": "dev"}})
    assert context.render({"a": ["{{env.name}}", {"b": "{{env.name}}!"}]}) == {
        "a": ["dev", {"b": "dev!"}]
    }
