# sop — 配置驱动的浏览器 RPA 骨架

用 YAML 描述浏览器操作流程，Playwright 负责执行，自动采集截图 / 失败现场，
最后生成一份可转发的单文件 HTML 报告。适合做登录、下单、后台巡检这类重复操作。

- 流程是纯数据，可读、可手改、可进 Git
- 定位用「定位描述」多策略兜底，不写裸选择器
- 只对超时重试；断言失败立即停
- 每次执行独立目录，截图带序号和步骤名
- 报告图片内嵌 base64，单文件即可分享
- 密码只从环境变量读取，日志和报告自动脱敏

## 目录结构

```
sop/
├── cli.py                 # 命令行入口（sop run ...）
├── core/
│   ├── engine.py          # 执行内核：浏览器、预算、重试、截图
│   ├── recorder.py        # 录制器：浏览器事件 → 流程 YAML
│   ├── models.py          # Pydantic 流程/步骤校验
│   ├── locator.py         # 定位描述与多策略兜底
│   ├── evidence.py        # 截图、失败现场
│   ├── report.py          # HTML 报告渲染
│   ├── config.py          # env 配置与 ${环境变量}
│   ├── template.py        # {{变量}} 插值
│   └── steps/             # 每个动作一个模块，自动注册
├── flows/                 # 流程 YAML
├── pages/                 # 页面对象（可选，供自定义脚本复用）
├── scripts/               # run 动作的自定义脚本
├── data/                  # 测试数据（按需使用）
├── configs/               # env.<name>.yaml
├── templates/report.html  # 报告模板
├── runs/                  # 每次执行的产物
└── pyproject.toml
```

## 安装

需要 Python 3.11+。

```bash
cd sop
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m playwright install chromium
```

安装后命令行入口为 `sop`（未激活虚拟环境时用 `.venv/bin/sop`）。

## 配置密码与环境

`configs/env.dev.yaml`：

```yaml
name: dev
base_url: https://www.saucedemo.com

vars:
  username: standard_user
  password: ${SAUCEDEMO_PASSWORD}

browser:
  viewport: [1440, 900]
  locale: en-US
  test_id_attribute: data-test   # SauceDemo 使用 data-test
```

`${SAUCEDEMO_PASSWORD}` 会在加载配置时从进程环境变量读取；变量名含
`PASS / SECRET / TOKEN / KEY / CREDENTIAL` 的值会自动登记为敏感值，
在终端日志、报告、DOM 快照中统一替换成 `***`。

运行示例前先设置密码：

```bash
export SAUCEDEMO_PASSWORD=secret_sauce
```

## 跑示例流程

```bash
# 单条流程
sop run flows/01_login.yaml --env dev

# 批量执行 flows/ 下所有 YAML，汇总成一份报告
sop run flows/ --env dev

# 看到浏览器窗口 + 每步都截图 + 记录 trace
sop run flows/01_login.yaml --env dev --headed --shots every --trace

# 只校验语法、定位描述、脚本/上传文件引用，不启动浏览器
sop run flows/ --env dev --dry-run
```

终端会输出每一步结果，最后给出结论和报告路径：

```
✔ 01_login 12 步全过 用时 2.4s
报告: /.../runs/20261123-114904_01_login/report.html
```

`flows/` 里的三个示例按文件名顺序执行：

| 流程 | 内容 |
| --- | --- |
| `01_login.yaml` | 登录 → 商品列表 → 断言 → 排序 → 截图 → 提取 → 自定义脚本校验，并保存登录态 |
| `02_add_to_cart.yaml` | 独立登录 → 加入购物车 → 断言角标 → 截图 |
| `03_reuse_login.yaml` | 读取 `01` 保存的 `storage_state`，不登录直接进商品页 |

单独运行 `03` 前需要先跑过一次 `01`（或在批量执行时由 `01` 自动满足）。

### 命令行参数

| 参数 | 说明 |
| --- | --- |
| `target` | 流程 YAML 或目录；目录即批量模式 |
| `--env <name>` | 对应 `configs/env.<name>.yaml`，默认 `dev` |
| `--headed` | 显示浏览器窗口，默认无头 |
| `--shots every\|key\|fail` | 截图策略，默认 `key` |
| `--dry-run` | 只校验，不开浏览器 |
| `--trace` | 记录 Playwright trace 到运行目录 |
| `--browser chromium\|firefox\|webkit` | 覆盖流程里的浏览器 |
| `--timeout <秒>` | 覆盖整场超时预算 |
| `--stop-on-failure` | 批量时遇到第一个失败流程即停止 |

## 录制流程（sop record）

不想手写 YAML 时，可以直接在浏览器里操作一遍：

```bash
export SAUCEDEMO_PASSWORD=secret_sauce
sop record https://www.saucedemo.com --env dev \
  --out flows/04_recorded.yaml --name 录制登录
```

- 打开有头浏览器，正常点击、输入、选择即可。
- 页面右下角浮层：
  - `截图 (Alt+S)`：当前位置插入一条 `screenshot`；刚点过异步操作时会提示先等待再截图
  - `等待出现 (Alt+W)`：一次性模式，下一次点击生成 `wait_for`
  - `断言文本 (Alt+A)`：一次性模式，下一次点击生成 `assert`；输入框会生成 value 断言
  - `提取变量 (Alt+X)`：一次性模式，下一次点击把元素文本/输入值存成变量；之后把值粘贴到其他输入框时会写 `{{变量名}}`。不按 Alt+X 时，粘贴到另一个输入框也会自动识别相同值并补一条 `extract`。
  - `结束录制 (Alt+E)`：保存 YAML 并关闭浏览器
- 点击后按钮进入 disabled 再恢复的异步操作，录制器会自动补一条 `assert state: enabled`。
- 结束后自动写出流程、执行一次 load + validate（等同 dry-run），并打印可直接运行的
  `sop run <文件> --env <环境>` 命令；如果 goto 与 `env.base_url` 不一致，会提示应配置哪个 env 文件。

生成结果示例：

```yaml
version: 1
name: recorded
description: 由 sop record 录制
env: dev
locators:
  username: {testid: username}
  password: {testid: password}
  login-button: {testid: login-button}
  Hello-World: {text: Hello World, exact: true}
steps:
- action: goto
  name: 打开页面
  url: "{{env.base_url}}"
- action: fill
  name: 输入 username
  target: username
  value: standard_user
- action: fill
  name: 输入密码
  target: password
  value: "{{env.password}}"
- action: click
  name: 点击 login-button
  target: login-button
- action: assert
  name: 断言文本 Hello World
  target: Hello-World
  text: Hello World
- action: screenshot
  name: 截图 1
```

定位优先级为 `testid → role/name → within + role/name → text → within + text → css`：

- 多命中时先向上找最近 3 层内带 id / testid / 稳定 `data-*` 的容器，用 `within` 缩小范围，而不是直接掉到 `nth-of-type`。
- 高熵长串（密文、token、base64/hex）和 4 位以上纯数字不当作 text 定位；输出区域优先用稳定 id，例如 `#encrypt-output`。
- CSS 兜底优先 id，其次稳定 `data-*`（如 `data-generate`、`data-copy`），最后才拼 `nth-of-type`。
- locator 名用“容器-语义”（如 `encrypt-result-box-button-复制`），不再用截断的 CSS 路径。

iframe 内的元素会自动带 `frame`（优先用 iframe 的 `name`，没有 name 时用录制时的 URL）。
相同定位会收敛到顶部 `locators:`，后续手工修改只需改一处。

本地服务可以直接用仓库里的 `configs/env.local.yaml`：

```bash
sop record http://localhost:8080 --env local --out flows/05_recorded.yaml
```

这样 goto 会写成 `{{env.base_url}}`，`sop run flows/05_recorded.yaml --env local` 可直接运行。

复用已有片段与页面对象：

```bash
# 登录片段已经维护好，只录制登录之后的操作
sop record https://www.saucedemo.com/inventory.html --env dev \
  --include-steps flows/_partials/saucedemo_login.yaml \
  --page-object saucedemo \
  --out flows/04_recorded.yaml
```

- `--include-steps` 会写进流程的 `include_steps`，片段里的步骤和 locators 一起加载。
- `--page-object <module>` 会把命中的定位写成
  `locators.<CONST>: pages.<module>.<CONST>`，和手写流程共用页面对象。
- `--storage-state <文件>` 可在录制前加载已有登录态。

敏感输入处理：

- 非敏感字段保持字面量，不再按值反查 env，避免把明文/用户名意外绑定到密码。
- password 类型或字段名含 `pass / secret / token / key / credential` 的输入才会模板化。
- 录制值正好等于某个 env 变量时，使用该变量（如 `{{env.password}}`）。
- 否则写字段级占位符（如 `decrypt-password` → `{{env.decrypt_password}}`）并提示补齐配置，
  不会回退成通用 `password`。
- 随机生成的密钥/密文建议用 `Alt+X` 提取成变量，再粘贴到其他输入框；录制器会写 `{{变量名}}`。

暂时录不到的操作：

- hover、拖拽、双击、右键、文件上传/下载
- 用 Enter 提交表单（页面会提示改为点击提交按钮）
- 多标签页、弹窗和浏览器原生对话框
- 剪贴板内容读取/校验（可以点击“复制”，但无法断言剪贴板）
- 循环和数据驱动；复杂的嵌套容器可以录制后手工调整 `within`
- 任意异步结果的自动等待（目前只对“按钮 disabled → 恢复”这种模式自动补等待，其余请用 `Alt+W` 标记）

## 写一条流程

```yaml
version: 1
name: 下单演示
description: 登录后把背包加入购物车
timeout: 90                 # 整场预算（秒）
default_step_timeout: 12    # 单步默认超时
retries: 1                  # 超时类错误重试次数（总尝试 2 次）
save_storage_state: .auth/demo.json   # 可选：结束后保存登录态

steps:
  - action: goto
    name: 打开登录页
    url: "{{env.base_url}}"

  - action: fill
    name: 输入用户名
    target:                 # 定位描述，按优先级兜底
      testid: username
      css: "#user-name"
    value: "{{env.username}}"

  - action: fill
    name: 输入密码
    target:
      testid: password
    value: "{{env.password}}"

  - action: click
    name: 点击登录
    target:
      testid: login-button
      role: button
      name: Login

  - action: wait_for
    name: 进入商品列表
    target:
      testid: inventory-container
    key: true               # shots=key 时这一步截图

  - action: assert
    name: URL 已跳转
    url_contains: /inventory.html

  - action: screenshot
    name: 商品列表

  - action: extract
    name: 提取商品名称
    target:
      testid: inventory-item
    all: true
    attr: inner_text
    as: products

  - action: run
    name: 校验商品数量
    file: scripts/check_products.py
    args:
      expected: 6
```

### 复用页面对象与步骤片段

流程文件支持把公共定位和公共步骤抽出来，避免每条流程复制登录逻辑：

```yaml
# flows/01_login.yaml
version: 1
name: 01_login
include_steps:
  - _partials/saucedemo_login.yaml   # 共享的登录步骤
requires:                            # 可选：声明依赖，批量执行时自动排序
  - 00_prepare
locators:
  inventory.container: pages.saucedemo.INVENTORY_CONTAINER
steps:
  - action: assert
    target: inventory.container      # 字符串简写等价于 {ref: inventory.container}
    state: visible
```

```yaml
# flows/_partials/saucedemo_login.yaml
locators:
  login.username: pages.saucedemo.LOGIN_USERNAME
  login.submit: pages.saucedemo.LOGIN_BUTTON
steps:
  - action: fill
    target: login.username
    value: "{{env.username}}"
  - action: click
    target: login.submit
```

- `locators` 可以写内联定位描述，也可以写 `pages.<module>.<CONST>`，从 `pages/` 下的 Python 页面对象读取字典。
- `target: login.username` 或 `target: {ref: login.username}` 都会在加载时解析成真正的定位描述。
- `include_steps` 支持相对当前流程文件的路径，片段里也可以继续 `include_steps`（会检测循环引用）。
- `requires` 用于声明流程依赖；批量执行会自动排序，单独执行时只给出提示。

### 步骤公共字段

| 字段 | 说明 |
| --- | --- |
| `name` | 步骤名，也是截图文件名的一部分 |
| `timeout` | 本步超时（秒），默认取 `default_step_timeout` |
| `retries` | 本步超时重试次数，覆盖流程级 `retries` |
| `retry_on_timeout` | 是否允许超时重试；不写则跟随动作的安全声明 |
| `optional` | 失败不中断流程，报告里标记为警告 |
| `key` | 标记关键步骤，`--shots key` 时截图 |

重试只发生在超时类错误（定位等待超时、页面/操作超时）；断言失败和确定性错误不会重试。
并且只有声明为可安全重试的动作才会重试：`goto`、`wait_for`、`screenshot`、`extract` 默认可重试；
`click`、`fill`、`select`、`upload`、`download`、`run` 默认不重试，避免重复提交、重复上传等副作用。
确认某个点击没有副作用时，可以在该步骤显式写 `retry_on_timeout: true`。

整场 `timeout` 是硬预算：每次重试前都会重新计算剩余时间，单步和 `assert` 的多个条件共享同一个 deadline，不会因为重试或多条件断言大幅超出预算。

### 动作一览

| action | 主要参数 | 说明 |
| --- | --- | --- |
| `goto` | `url`、`wait_until` | 打开页面；`url` 支持 `/path` 拼接 `base_url` |
| `click` | `target`、`button`、`click_count` | 点击前会显式等待元素可见 |
| `fill` | `target`、`value`、`clear` | 默认覆盖输入，`clear: false` 为追加输入 |
| `select` | `target`、`value` 或 `label` | 下拉框选择 |
| `wait_for` | `target`、`state` | `visible / hidden / attached / detached` |
| `assert` | `target` / `text` / `url_contains`、`state` | 断言失败不重试 |
| `screenshot` | `name`、`full_page` | 显式截图，始终执行 |
| `extract` | `target`、`as`、`attr`、`all` | 结果写入模板变量 |
| `upload` | `target`、`files` | 文件路径相对项目根目录 |
| `download` | `target`、`save_as` | 点击触发下载并保存 |
| `run` | `file`、`function`、`args` | 自定义 Python 脚本兜底 |

## 定位描述

同一个 `target` 里可以同时写多个策略，运行时按固定优先级依次尝试，
命中哪个会记录在报告的执行日志里：

```
testid  →  role + name  →  text  →  css  →  xpath
```

```yaml
target:
  testid: login-button       # 1. get_by_test_id
  role: button               # 2. get_by_role + 可访问名称
  name: Login
  text: Login                # 3. 可见文本
  css: "#login-button"       # 4. CSS
  xpath: "//input[@id='login-button']"
```

`testid` 对应的 HTML 属性默认是 `data-testid`，可在 env 配置里用
`browser.test_id_attribute` 改成 `data-test` 等。

默认要求定位唯一命中。如果多个元素都匹配，会直接报“定位歧义”而不是静默点第一个；
确实需要取第一个/第 N 个时显式声明：

```yaml
target:
  text: Delete
  first: true        # 或 index: 2（从 1 开始）
```

`extract` 的 `all: true` 是明确的多元素读取，不受歧义检查影响。
注意：`first` / `index` 只作用于最终命中策略内部的多个元素；如果同一目标写了多个兜底策略，
仍然按 testid → role → text → css → xpath 的顺序选第一个命中的策略。

### iframe 与容器作用域

后台页面常用 iframe 或表格行，这时可以先把查找范围切到 frame / 容器内：

```yaml
target:
  frame: "#editor-frame"   # 或 {name: editor} / {url: "*editor.html"}
  within:                  # 先在当前作用域找到这一行，再找行内按钮
    testid: row
    index: 2
  testid: row-delete
```

- `frame` 支持三种写法：CSS 字符串、`{name: editor}`、`{url: "*editor.html"}`（URL 通配符）。
- `within` 是父级定位描述，可以继续嵌套，同样受歧义检查约束（父容器多命中时要写 `first` / `index`）。
- 报告里的“定位命中”会显示完整作用域，例如 `frame(css=#editor-frame) > testid`。
- CSS/XPath 的括号、引号、`##` 等明显语法错误会在加载和 `--dry-run` 阶段直接报错；
  运行期才发现的非法选择器按确定性失败处理，不会重试。

## 模板变量

- `{{env.base_url}}`、`{{env.username}}`、`{{env.password}}`：来自 env 配置
- `{{products}}` 或 `{{vars.products}}`：`extract` 步骤产出的变量
- 整个值只有一个占位符时保留原始类型（列表 / 数字），否则按字符串拼接

```yaml
- action: goto
  url: "{{env.base_url}}/inventory.html"
```

## 截图、失败现场与报告

每次执行创建 `runs/<时间戳>_<流程名>/`：

```
runs/20261123-114904_01_login/
├── 01-打开登录页.png
├── 02-进入商品列表.png
├── 03-商品列表.png
├── console.log          # 失败时保存控制台错误
├── failure.html         # 失败时保存 DOM 快照
├── trace.zip            # --trace 时生成
└── report.html
```

- `--shots every`：每步成功后截图
- `--shots key`：只截 `key: true` 的步骤（`screenshot` 动作始终执行）
- `--shots fail`：只在失败时截图

任何失败都会额外保存：当前视口截图、全页截图、`failure.html`、`console.log`。
报告顶部是汇总（通过/失败步数、耗时、环境），中间是步骤时间线，
失败步骤的现场证据默认展开；所有图片已内嵌，单个 HTML 文件即可转发。

批量执行时，报告在 `runs/<时间戳>_batch/report.html`，每个流程各有子目录。

## 登录态复用

```yaml
# 流程 A：登录成功后保存
save_storage_state: .auth/demo.json

# 流程 B：启动时加载，跳过登录
storage_state: .auth/demo.json
```

`.auth/` 已加入 `.gitignore`。文件不存在时只会给出警告并忽略，不会中断执行。

## 自定义脚本（run）

脚本签名固定为 `run(ctx, **args)`：

```python
def run(ctx, expected=6):
    names = ctx.variables.get("products") or []
    if len(names) != expected:
        raise AssertionError(f"期望 {expected} 个商品，实际 {len(names)}")
    ctx.log(f"校验通过: {len(names)}")
```

可用对象：`ctx.page`、`ctx.variables`、`ctx.env`、`ctx.log(msg)`、
`ctx.set_var(name, value)`、`ctx.project_root`。项目根目录会自动加入
`sys.path`，因此可以 `from pages.saucedemo import ...` 复用页面对象。

## 扩展新动作

在 `core/steps/` 新建模块，提供四个名字即可被自动注册，不需要改内核：

```python
ACTION = "scroll"          # YAML 里的 action
LABEL = "滚动页面"          # 报告里的中文名
class Params(BaseModel):   # 参数校验（extra="forbid"）
    ...
def run(step, ctx):        # 执行逻辑，返回 None
    ...
```

如果需要在 `--dry-run` 时检查文件等前置条件，可选实现
`validate(step, project_root) -> list[str]`。

## 测试

```bash
.venv/bin/python -m pytest -q
```

测试使用本地 `tests/fixtures/page.html`，不依赖外网；覆盖定位优先级/歧义/frame/within、
模板插值、流程加载与片段复用、重试安全与预算、报告内嵌图片、动作注册契约，以及录制器的
定位挑选（动态文本/within/data-*）、输入合并、敏感值处理、提取变量、异步等待、YAML 生成与无头端到端录制。

## 已知边界

- 录制器覆盖 `click / fill / select / wait_for / extract / assert / screenshot`；更复杂的操作仍需手写流程或 `run` 脚本
- 批量执行是串行；暂不支持并行
- 页面返回 4xx 不会被 `goto` 直接判失败（部分 SPA 深链接会返回 404），
  页面是否正确请用 `assert` 明确表达
- 定位兜底只在超时预算内轮询，动态加载很慢的页面请调大 `default_step_timeout`
