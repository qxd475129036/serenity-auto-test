"""示例：run 动作的自定义脚本兜底。

引擎会以 `run(ctx, **args)` 调用；ctx 提供 page / variables / env / log / set_var。
页面对象 pages/saucedemo.py 里的定位描述可以直接复用。
"""

from pages.saucedemo import INVENTORY_ITEM


def run(ctx, expected=6):
    names = ctx.variables.get("products") or []
    dom_count = ctx.page.get_by_test_id(INVENTORY_ITEM["testid"]).count()

    if len(names) != expected:
        raise AssertionError(f"extract 得到 {len(names)} 个商品，期望 {expected}")
    if dom_count != expected:
        raise AssertionError(f"页面实际有 {dom_count} 个商品，期望 {expected}")

    first_line = names[0].splitlines()[0] if names else ""
    ctx.log(f"商品数量校验通过: {dom_count} 个；首个商品: {first_line}")
