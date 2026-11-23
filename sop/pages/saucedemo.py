"""SauceDemo 页面对象示例。

YAML 流程里直接写内联定位描述即可；当 `run` 自定义脚本需要复用定位时，
可以像 scripts/check_products.py 这样 import 本模块。

这里的定位描述结构与 YAML 中 target 字段完全一致。
"""

LOGIN_USERNAME = {"testid": "username", "css": "#user-name"}
LOGIN_PASSWORD = {"testid": "password", "css": "#password"}
LOGIN_BUTTON = {"testid": "login-button", "role": "button", "name": "Login"}
INVENTORY_CONTAINER = {"testid": "inventory-container", "css": ".inventory_list"}
INVENTORY_ITEM = {"testid": "inventory-item", "css": ".inventory_item"}
CART_BADGE = {"testid": "shopping-cart-badge", "css": ".shopping_cart_badge"}

PAGES = {
    "login.username": LOGIN_USERNAME,
    "login.password": LOGIN_PASSWORD,
    "login.submit": LOGIN_BUTTON,
    "inventory.container": INVENTORY_CONTAINER,
    "inventory.item": INVENTORY_ITEM,
    "inventory.cart_badge": CART_BADGE,
}


def target(name: str) -> dict:
    """按名字取定位描述，便于在自定义脚本里集中维护。"""
    return PAGES[name]
