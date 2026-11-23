from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..errors import StepFailure
from ..locator import Locator, Target
from ._util import resolve_or_timeout, short
from .base import StepContext

ACTION = "extract"
LABEL = "提取数据"
RETRY_SAFE = True


class Params(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    target: Target
    as_: str = Field(alias="as", min_length=1)
    attr: Literal["inner_text", "text", "html", "value", "attribute"] = "inner_text"
    attribute: str | None = None
    all: bool = False

    @model_validator(mode="after")
    def _check(self) -> "Params":
        if self.attr == "attribute" and not self.attribute:
            raise ValueError("attr=attribute 时必须提供 attribute 名称")
        return self


def _read_one(locator, params: Params) -> Any:  # type: ignore[no-untyped-def]
    if params.attr == "inner_text":
        return locator.inner_text()
    if params.attr == "text":
        return locator.text_content()
    if params.attr == "html":
        return locator.inner_html()
    if params.attr == "value":
        return locator.input_value()
    return locator.get_attribute(params.attribute or "")


def _read_all(locator: Locator, params: Params) -> list[Any]:
    if params.attr == "inner_text":
        return locator.all_inner_texts()
    if params.attr == "text":
        return locator.all_text_contents()
    return [_read_one(locator.nth(i), params) for i in range(locator.count())]


def run(step, ctx: StepContext) -> None:  # type: ignore[no-untyped-def]
    params: Params = step.params
    resolved = resolve_or_timeout(
        ctx, params.target, state="attached", multiple=params.all
    )
    try:
        if params.all:
            value: Any = _read_all(resolved.locator, params)
        else:
            value = _read_one(resolved.first, params)
    except Exception as exc:
        raise StepFailure(f"提取失败: {exc}") from exc

    ctx.set_var(params.as_, value)
    preview = f"{len(value)} 项" if params.all else short(value)
    ctx.log(f"变量 {params.as_} = {preview}")
