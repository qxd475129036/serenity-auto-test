# sop 架构优化建议

> 评审对象：`/Users/quxd/git/serenity-auto-test/sop` 当前实现（2026-11-23 版本）
> 评审方式：通读 `core/`、`cli.py`、示例流程与报告模板，并用 `flows/` 与临时失败流程实跑验证。
> 本文只做分析和建议，不包含代码改动。

## 结论先行

当前骨架已经能跑通「登录 → 列表 → 断言 → 截图 → 报告」的闭环，动作注册、定位兜底、证据目录和报告分层也基本成立。真正需要优先处理的不是样式或性能，而是几个会影响正确性和后续返工的点：

| 顺序 | 问题 | 位置 | 为什么现在要改 |
| --- | --- | --- | --- |
| 1 | 所有超时都会重试，包括有副作用的 `click / upload / download / run` | `core/engine.py` `_classify`、`_run_step` | 一次点击超时可能已经生效，重试会重复下单、重复上传 |
| 2 | 重试和 `assert` 多条件会绕开整场超时预算 | `core/engine.py:139-189`、`core/steps/assertion.py:44-95` | 实测 3s 预算跑了 3.9s；多条件断言可跑到 3 倍 step timeout |
| 3 | 页面对象没有进入流程 DSL，登录步骤在流程间复制 | `pages/saucedemo.py`、`flows/01_login.yaml`、`flows/02_add_to_cart.yaml` | 现在改登录定位要改多个文件；这是最容易返工的抽象 |
| 4 | 多个元素命中时静默取 `.first` | `core/locator.py:158-165` | 表格里点“删除”会点到第一行，属于静默错误，比失败更危险 |
| 5 | 没有任何自动化测试 | 仓库无 `tests/` | 上面 1-4 的修改没有回归保护，后续动作扩展也不敢动内核 |

**可以先不动**：报告视觉精修、深色模式、多浏览器、并行执行、完整条件/循环 DSL、插件市场、GUI 录制器。这些不是当前主要矛盾。

---

## 事实基线

先记录本次评审的实际运行数据，后面的判断都以这些事实为依据：

- `sop run flows/ --env dev --trace`：3 个流程、26 步全部通过，总耗时 6.6s。
- 批量报告 `runs/20261123-115243_batch/report.html`：7 张截图内嵌后的 HTML 为 **1.9MB**，整个运行目录 4.7MB（含 3 个 trace）。
- 整场预算实验：`timeout: 3` 的流程实际运行 **3.9s** 才结束，预算是被超出的。
- 断言实验：`retries: 3` 下故意让 `assert` 失败，实际只执行一次（2.07s），说明「断言不重试」的语义是对的。
- 定位超时实验：`default_step_timeout: 2`、`retries: 1` 时，click 等待了 4.18s（2 次尝试），重试生效。

---

## P0：现在就该改

### P0-1 重试语义对有副作用的动作不安全

**现状**
`core/engine.py` 的 `_classify()`（104-112 行）把所有 `StepTimeout` 和 `PlaywrightTimeoutError` 都判为可重试，`_run_step()`（160-189 行）对任何动作统一循环重试。动作模块没有地方声明自己是否可安全重试。

**会疼的场景**
- 点击「提交订单」后页面跳转很慢，Playwright 抛超时，但点击其实已经生效；第二次点击可能提交两次。
- `upload` 在文件已经开始上传后超时，重试会重复上传。
- `download` 的 `expect_download` 超时后重试点击，可能生成两个下载任务。
- `run` 自定义脚本内部已经产生了外部副作用，超时后重试等于执行两遍。

这类问题在演示站点上不会暴露，一上真实后台就是数据问题。

**建议**
1. 在动作模块增加一个声明，例如 `RETRY_SAFE = True/False`。`goto`、`wait_for`、`assert`（虽然本来就不重试）可以安全；`click`、`fill` 默认不安全；`upload`、`download`、`run` 必须显式声明才允许重试。
2. 步骤级提供 `retry_on_timeout: true` 作为人工确认的逃生口，默认跟随动作声明。
3. 重试前记录「该动作是否有副作用」，并在报告中显示重试原因；不要只写“超时”。
4. 对 `click` 这类动作，重试时至少要求重新导航或重新定位，不能在原页面状态上盲目再点一次。

**优先级**
P0。属于正确性风险，应该在写更多真实流程之前解决。

---

### P0-2 超时预算会被重试与多条件断言穿透

**现状**
- `_run_step()` 在 139-141 行用 `min(step.timeout, remaining_s)` 算出 `timeout_ms`，但这个值在后续每次重试中复用（160-189 行），不会因为整场剩余时间变少而收缩。
- `assertion.run()` 在 50-95 行对 `url_contains`、`target`、`text` 每个条件分别传入完整的 `ctx.timeout_ms`，一个 assert 步骤最多可以消耗 3 倍 step timeout。
- `locator.resolve()` 的轮询粒度和单候选 300ms 等待也会让实际结束时间略超预算。

**会疼的场景**
- 预算 3s 的流程实测跑了 3.9s；如果有 `retries: 1`、step timeout 12s，一步就可能跑 24s，整场超时形同虚设。
- 一个 `assert` 同时断言 URL、容器可见、页面文本，实际可能等 36s，而报告里只显示 step timeout 12s，用户无法理解为什么这么慢。

**建议**
1. 为每一步建立独立的 `step_deadline = now + min(step_timeout, overall_remaining)`，每次重试前重新计算剩余时间；剩余不足时直接停止重试并标记原因。
2. 把同一个 deadline 传给 `assert` 内部的每个 `expect(..., timeout=remaining)`，而不是每个条件都用全量 timeout。
3. `locator.resolve`、`wait_absent` 也接收绝对 deadline，避免“每次循环重新给 300ms”。
4. 报告中增加 `budget` 与 `overrun` 字段，直接显示超时是否发生。

**优先级**
P0。和 P0-1 同批修改，并补上预算测试。

---

### P0-3 页面对象没有进入流程 DSL，登录步骤在复制

**现状**
- `pages/saucedemo.py` 定义了 `LOGIN_USERNAME`、`PAGES`、`target()`，但引擎和 YAML 都不认识这些引用；目前只有 `scripts/check_products.py` 导入了 `INVENTORY_ITEM` 一个常量。
- `flows/01_login.yaml` 和 `flows/02_add_to_cart.yaml` 各自重复了 goto、填用户名、填密码、点击登录、等待列表这 5 步。
- `flows/03_reuse_login.yaml` 依赖 `01_login` 保存的 `.auth/saucedemo.json`，但没有显式依赖声明，只靠文件名顺序。
- `Flow` 模型没有 `version`、`defaults`、`includes` 或片段复用能力。

**会疼的场景**
- 登录页改了一个 testid，需要改所有流程；漏改一个就出现线上流程通过、另一个流程失败的漂移。
- 页面对象文件看似存在，但写 YAML 的同事完全用不上，最后大家仍然复制粘贴。
- 流程数量一多，登录、侧边栏、弹窗这些公共步骤会变成几十份副本。

**建议**
1. 让 YAML 能引用页面对象，而不是只能从 Python 脚本里 import。最小方案是在流程级增加 `locators:` 字典，`target: {ref: login.username}`，加载时解析成 `Target`；这样 dry-run 也能校验引用是否存在。
2. 增加流程片段复用，例如 `include: pages/login.yaml` 或 `extends`，并支持 YAML anchor 作为文件内复用。不要一上来做复杂继承，先解决“登录只写一次”。
3. 给流程增加 `requires: [01_login]` 或 `setup` 声明，把隐式的 storageState 依赖显式化；批量执行时按依赖排序，单跑 03 时给出明确提示。
4. 增加 `version: 1` 字段，给后续格式演进留迁移入口。

**优先级**
P0。这是当前最明显的架构返工点：页面对象层已经存在，但没有接进 DSL，继续写流程只会扩大重复。

---

### P0-4 多个元素命中时静默取 `.first`

**现状**
`Resolved.first`（`core/locator.py:158-165`）直接返回 `locator.first`；`click / fill / select / extract` 等动作都默认使用它，没有任何数量检查。`resolve()` 只判断 `locator.count() > 0`，不关心是不是多于 1 个。

**会疼的场景**
- 商品列表每行都有 `text: "Add to cart"`，`click` 会点第一行，而不是目标行。
- 后台表格每行都有「删除」，流程“通过”了，但删错了数据。
- `text` 策略通常比 testid 更容易多命中，兜底越往后，误点风险越高。

**建议**
1. 默认严格：`count() > 1` 时抛 `StepAmbiguity`（不重试），错误信息带上命中数量、命中的策略和几个候选的简要文本。
2. 提供显式逃生口：`target: { ..., first: true}` 或 `index: 2`，让“取第一个/第 N 个”成为作者明确表达，而不是默认行为。
3. 过渡期可以先把歧义记录为警告并继续，但报告必须显著展示，避免静默成功。
4. 顺带补上 `within`（容器内查找）和 `nth`；没有容器作用域时，列表项操作只能靠 run 脚本，报告粒度会丢失。

**优先级**
P0。属于正确性问题，且改动集中在 `locator.py` 和少数动作模块。

---

### P0-5 建立最小测试基线，再动内核

**现状**
仓库没有 `tests/`，`scripts/check_products.py` 是业务示例，不是回归测试。当前验证依赖公开站点 `saucedemo.com`，而该站点的 `data-test` 属性、深链接 404 行为已经在本次开发中造成过一次误判。

**会疼的场景**
- 修 P0-1/P0-2 时无法证明“超时只重试一次”“预算不超”，只能靠人工跑演示站点。
- 新增动作时无法快速验证注册机制、参数校验、报告字段是否完整。
- 公开站点改版会让示例流程失败，但无法区分是工具回归还是站点变化。

**建议**
1. 增加 `tests/fixtures/page.html` 本地静态页，覆盖 testid、role/name、text、重复元素、隐藏元素、iframe 等场景，不依赖外网。
2. 用 fake action 模块测引擎语义：一个抛 `StepTimeout`、一个抛 `StepAssertion`，断言重试次数与最终状态；用 sleep 动作测预算，先锁住“3s 预算不能跑 3.9s”。
3. 加契约测试：遍历 `registry.actions()`，断言每个模块都有 `ACTION / LABEL / Params / run`，且 `Params` 使用 `extra="forbid"`。
4. 加报告测试：包含一个假密码，渲染后断言 HTML 中不出现明文；覆盖失败步骤的 DOM/截图字段。
5. CI 跑 `pytest` + 全量 `sop run flows/ --dry-run`（注入假的 `SAUCEDEMO_PASSWORD`）。

**优先级**
P0/P1 交界。建议和 P0-1、P0-2 同批做，否则改重试语义没有安全网。

---

## P1：近期值得做

### P1-1 定位能力补齐：frame / within / nth / 非法选择器

**现状**
`Target`（`core/locator.py:111-155`）只有 testid、role、name、text、css、xpath，`resolve()` 始终在 `page` 顶层查找。HTTP 4xx、iframe、非法 CSS 都没有专门处理；`resolve()` 的 `except (PlaywrightTimeoutError, PlaywrightError)` 会把非法选择器也吞掉，最后表现为“定位超时”。

**会疼的场景**
- 真实后台大量使用 iframe，当前所有定位都会超时，只能退化成 `run` 脚本。
- 表格行内的按钮没有作用域，只能靠 `text` 多命中后取 first，和 P0-4 叠加。
- CSS 写错（例如 `##id`）时用户等待 12s 后看到“定位失败”，而不是“选择器非法”。

**建议**
1. `Target` 增加 `frame`（name/url 或 locator）与 `within`（父级 Target），解析时先定位 frame/container，再查找子元素。
2. 增加 `index` / `first` 字段，配合 P0-4 的歧义策略。
3. `resolve()` 区分 `PlaywrightError` 中的选择器语法错误，直接抛 `StepFailure`（不重试），并在 dry-run 阶段做基础 CSS/XPath 语法检查。
4. 长期可记录每个目标实际命中的策略（testid/role/text…），在报告中展示“兜底使用率”，帮助清理过时策略。

**优先级**
P1。saucedemo 不需要，但接第一个真实后台之前必须补。

---

### P1-2 运行结果持久化，报告从结果文件生成

**现状**
`FlowResult` / `StepResult` 只存在内存里，`core/report.py` 的 `_flow_payload()` 直接消费 dataclass。运行目录只有截图和报告，没有结构化的 `result.json`。批量执行时 `cli._run()`（173-175 行）先加载所有流程，任何一条 YAML 错误都会让整批不执行；中途 `EnvLoader.get()` 抛 `ConfigError` 也会让已经跑完的流程没有报告。

**会疼的场景**
- 报告模板需要调整时，只能重跑流程，不能基于历史结果重渲染。
- CI 想接 JUnit/JSON，只能解析 HTML。
- 批量跑到一半配置出错，前几个流程的截图还在，但结果和报告丢失。
- 想实现“失败重跑”或“从失败步骤继续”，没有持久状态可用。

**建议**
1. 每个流程运行目录写 `result.json`（流程元信息、步骤、耗时、状态、截图相对路径、错误），每步结束就落盘，报告只从 JSON 渲染。
2. 增加 `sop report <run_dir>` 和 `sop report --latest`，支持重新生成 HTML。
3. 增加 JUnit XML 输出，方便 CI 展示步骤级失败。
4. 批量执行改为逐条加载/校验，坏流程生成一个失败结果而不是中止整批；`ConfigError` 也一样进入结果，而不是直接退出。

**优先级**
P1。越早做越省事，后续并发、重跑、历史报告都依赖它。

---

### P1-3 证据体积与产物治理

**现状**
- `Evidence.shot()`（`core/evidence.py:54-59`）固定输出 PNG；`capture_failure()` 每次失败都保存视口截图 + 全页截图 + DOM + 控制台。
- `_shot_payload()`（`core/report.py:37-50`）把每张原图直接 base64 内嵌，没有缩略图或尺寸限制。本次 7 张截图的批量报告已经是 1.9MB。
- `capture_failure()` 的 DOM 路径固定为 `failure.html`、控制台固定为 `console.log`（69、75 行）。多个 `optional` 步骤失败时，后一次会覆盖前一次的文件。
- `runs/` 没有清理策略，只有 `.gitignore`。

**会疼的场景**
- `--shots every` 跑 100 步，报告可能到 20-40MB，邮件/IM 发不出去，浏览器打开卡顿。
- 长页面全页截图可能是数万像素高，截图本身慢且占空间。
- 全页截图和完整 DOM 往往包含客户姓名、手机号等敏感信息，报告转发后面临数据泄露。
- 跑一周后 `runs/` 占满磁盘。

**建议**
1. 默认报告用 JPEG（Playwright 支持 `type="jpeg", quality=...`）或生成缩略图；原图留在目录中，报告可选择 `--embed=thumbnail|full|none`。
2. 给全页截图增加最大高度/宽度限制，超长页面改为“视口截图 + DOM”，避免极端尺寸。
3. 每个失败步骤独立命名，例如 `failure-06-进入商品列表.html` / `console-06.log`，不要共用固定文件名。
4. 增加 PII 开关：`capture_dom: false`、或对指定选择器做遮罩；至少 README 明确“报告含页面内容，转发前确认”。
5. 增加 `sop clean --keep 20` 或按天数清理，并在 `runs/index.html` 展示最近运行。

**优先级**
P1。体积和 PII 在第一次对外分享报告时就会成为问题。

---

### P1-4 批量执行的健壮性与依赖关系

**现状**
- `cli._run()` 开头的 173-175 行一次性加载所有流程；任意一个 YAML 有错，整批不跑。
- 每个流程的 `EnvLoader.get()` 在循环内调用，`ConfigError` 会冒泡到 CLI 最外层，已完成的流程结果丢失。
- 批量报告顶部环境信息取 `flows[0]`（`templates/report.html:308-309`），但不同流程可以使用不同 `env`；混合环境时顶部信息是错的。
- `03_reuse_login` 依赖 `01_login` 产出的 `.auth/saucedemo.json`，只靠文件名排序；在没有历史登录态时首次单独运行 03 会失败。

**会疼的场景**
- 50 条流程里有一条缩进错误，用户看到“校验失败”后一条都没跑。
- 前 10 条成功、第 11 条环境变量缺失，前 10 条没有报告。
- 混合 `dev`/`staging` 的批量报告顶部显示 dev 的地址，误导阅读者。
- 新同事在没有历史登录态时只跑 `03`，看到登录态失效，不知道要先跑 `01`。

**建议**
1. 批量模式逐条加载、逐条执行；加载失败生成一条失败记录并继续，最后统一出报告。
2. 环境配置错误同样转成失败结果，保留已完成流程的产物。
3. 报告顶部改成“环境：dev / staging”列表，或检测到多环境时明确显示“混合环境”。
4. 增加 `requires` / `setup` 声明，批量时自动排序；单独运行时给出“请先运行 01_login”的明确提示。
5. 保持 `--stop-on-failure` 作为可选项，默认继续。

**优先级**
P1。批量是当前卖点之一，一条坏流程毁掉整批的体验很差。

---

### P1-5 配置与密钥：惰性解析、显式敏感标记

**现状**
- `core/config.py` 的 `_resolve_env_refs()`（59-81 行）在加载配置时替换所有 `${VAR}`，缺任何一个都直接抛 `ConfigError`。因此只执行 `03_reuse_login` 也会因为 `SAUCEDEMO_PASSWORD` 未设置而失败，尽管该流程根本不用密码。
- 敏感值靠变量名正则 `_SENSITIVE_NAME` 判断；命名为 `SAUCEDEMO_PWD` 或直接写进 YAML 的值不会被登记。
- `extract` 步骤会把提取到的值写进日志预览（`core/steps/extract.py:63-65`）；如果提取的是 token，而它不在配置 secrets 里，就会进入报告。
- `BrowserConfig.viewport` 没有长度校验，`viewport: [1440]` 会在 `viewport_dict()` 触发 `IndexError`，而不是配置校验错误。

**会疼的场景**
- 只想跑一个不需要账号的流程，却被迫设置无关密码。
- 企业环境里 token 变量叫 `AUTH_TOKEN_VALUE` 能被识别，叫 `SESSION` 就漏掉。
- 业务页面上的会员手机号被 `extract` 后写进日志和报告。
- 配置写错时得到 Python 异常栈，而不是可读的配置错误。

**建议**
1. 环境变量改为按引用惰性解析：模板查找时才读取 `${VAR}`；或支持 `${VAR:-}` / `required: false`。
2. 配置增加显式 `secrets: [password, token]` 或变量级 `secret: true`，不要只靠命名猜测。
3. `extract` 增加 `secret: true`，该变量在日志和报告中统一脱敏；`fill` 对密码类目标默认脱敏。
4. 给 `viewport` 加 `min_length=2, max_length=2`，`slow_mo` 加 `ge=0`。
5. 可选支持 `.env` 文件，降低非技术同事设置环境变量的门槛。

**优先级**
P1。惰性解析影响日常使用，显式脱敏影响安全边界。

---

### P1-6 错误可诊断性：保留完整错误与堆栈

**现状**
`FlowRunner._classify()`（104-112 行）把错误统一截断到 300 字符，`assertion._first_line()` 只保留第一行（220 字符）。`run_script.run()`（68-73 行）把自定义脚本异常重新包成 `StepFailure`，只保留类型和 message，没有 traceback。`goto` 对 4xx/5xx 只写日志（`core/steps/goto.py:37-42`），不提示终端用户。

**会疼的场景**
- 自定义脚本里 `KeyError` 的具体行号丢失，只能重跑加 print。
- Playwright 的 call log 被截断，无法判断是元素不可见、被遮挡还是页面没跳转。
- 页面返回 500，但 `goto` 继续执行，最后在某一步定位失败；用户以为是定位问题。

**建议**
1. 错误拆成 `error_short`（终端、报告摘要）和 `error_detail`（完整异常 + traceback，写进步骤日志）。
2. `run` 脚本捕获异常时保留 `traceback.format_exc()`，并经过 Redactor 脱敏。
3. `goto` 增加 `expect_status: 200` 或 `fail_on_http_error: true`；默认保持宽松，但终端至少输出黄色警告。
4. 报告中失败步骤默认显示短错误，完整日志可展开，避免一屏全是堆栈。

**优先级**
P1。不影响跑通，但直接影响排障效率。

---

### P1-7 `optional` 警告的可见性与流程状态

**现状**
`_run_step()` 在 191-192 行把失败但 `optional: true` 的步骤改成 `warn`；`FlowResult.ok` 只看 `status == "passed"`，因此有警告的流程仍然算“通过”。报告顶部只显示“全部通过 / 存在失败”，没有警告计数。

**会疼的场景**
- 关闭弹窗这种可选步骤连续失败，但流程显示“全部通过”，用户不会去点开日志。
- 批量报告顶部写“全部通过”，实际有一个流程的购物车角标没校验到。

**建议**
1. 顶部汇总增加“警告 N 步 / M 个流程”，橙色而不是绿色。
2. 流程状态区分 `passed` / `passed_with_warnings`，报告和终端用不同颜色。
3. 终端结论里明确输出“12 步通过，1 步警告”。
4. `optional` 步骤仍然采集失败证据，但不要掩盖。

**优先级**
P1。小改动，能避免“假绿”。

---

### P1-8 `run` 动作的边界与安全

**现状**
`core/steps/run_script.py` 通过 `importlib` 执行流程指定的任意 Python 文件，并把项目根目录加入 `sys.path`（52-53 行）。`upload` 和 `download` 接受相对/绝对路径，没有项目根目录限制。

**会疼的场景**
- 流程文件从别人那里拷来，`run` 步骤等同于在本机执行任意代码。
- `upload: ../../.ssh/id_rsa` 或 `download.save_as: /etc/...` 可以读写项目外文件。
- 脚本里直接 `print(password)` 会绕过 `ctx.log` 的脱敏。

**建议**
1. 明确信任边界：文档写清“流程文件等同可执行代码”，或增加 `--allow-scripts` 开关。
2. `upload/download` 默认限制在项目根目录内，允许显式绝对路径但需要开关。
3. 捕获脚本 stdout/stderr 并做脱敏，或者明确不支持脚本直接 print。
4. 给 `run` 脚本加超时（当前依赖外层 step timeout，脚本内部阻塞时只能等外层杀进程）。

**优先级**
P1（如果团队内部完全信任流程作者，可降为 P2）。

---

## P2：可以等等

### P2-1 报告规模化：折叠、筛选、历史索引

**现状**
`templates/report.html` 对所有流程都渲染完整时间线（333 行开始），没有按流程折叠；批量只会越来越长。没有筛选按钮，也没有最近运行列表。

**会疼的场景**
50 个流程的批量报告需要滚动很久才能找到失败项；每次都要去 `runs/` 目录里找最新 HTML。

**建议**
1. 每个流程包一层 `<details>`，失败流程默认展开、通过流程默认折叠。
2. 顶部增加“全部 / 失败 / 警告”筛选，保持现有锚点。
3. 生成 `runs/index.html`，列出最近运行的流程、状态、耗时、报告链接。
4. 失败步骤的 DOM 默认折叠，错误 + 截图默认展开，兼顾“失败现场可见”和“页面可读”。

**优先级**
P2。当前 3 个流程的规模还不需要，但流程数上到 20+ 时收益明显。

---

### P2-2 并发与浏览器复用

**现状**
`FlowRunner.run()`（`core/engine.py:258` 起）为每个流程启动一次 `sync_playwright()` 和 browser，批量严格串行；浏览器启动和关闭成本在每个流程都要付一次。

**会疼的场景**
50 条只读巡检流程，串行执行时间主要花在浏览器启动上；而某些有副作用的流程又不能简单并行。

**建议**
1. 保持默认串行（RPA 副作用优先），增加 `--workers N` 使用进程池；不要用线程跑 sync Playwright。
2. 抽出 `BrowserSession`，支持批量复用同一个 browser、每个流程新建 context；`storage_state` 仍按流程隔离。
3. 报告里记录 worker 和浏览器实例，便于排障。
4. 注意 `playwright.selectors.set_test_id_attribute()` 是 Playwright 实例级全局状态，复用时不能按流程切换属性；需要多属性时应在 `Target` 层解决。

**优先级**
P2。先把单流程语义和测试做稳，再谈吞吐。

---

### P2-3 面向非技术同事的工具链

**现状**
- 流程是 YAML，但定位描述、动作名、错误信息仍是开发者视角；Pydantic 的错误 message 多为英文。
- 校验错误只给到步骤序号，没有 YAML 行号/列号。
- 由于 `Step.params` 是动态 `BaseModel`（`core/models.py:28-62`），`Flow.model_json_schema()` 无法表达每个动作的具体字段，编辑器自动补全基本没有。
- 没有 `sop locate`、`sop new flow`、`sop report --open` 这类脚手架。
- 运行前还要手动 `export` 密码。

**会疼的场景**
不懂代码的同事写错缩进或字段名，只能看到英文 Pydantic 报错和步骤号，不知道改哪一行；想找一个按钮的定位描述，只能自己看 DOM。

**建议**
1. 提供 `sop locate <url>` 或集成 Playwright codegen，让用户点选元素后生成 `Target` 描述。
2. 提供 `sop new flow <name>` 脚手架，带注释和最小可用步骤。
3. 生成 JSON Schema 时按动作生成 discriminated union，或额外输出 `schemas/<action>.json`，让 VS Code 能补全。
4. 用 `ruamel.yaml` 等保留节点位置，把校验错误映射到行号/列号，并把常见 Pydantic 错误翻译成中文。
5. 支持 `.env`、`--open` 自动打开报告、`runs/index.html` 历史页。
6. 最终形态建议打包成单文件可执行程序，避免让非技术同事装 Python。

**优先级**
P2，但这是“给不懂代码的同事用”的真正门槛；如果这是产品目标，应尽早排期，而不是等 DSL 稳定。

---

### P2-4 流程 DSL 的下一步演进

**现状**
流程是扁平 `steps` 列表，没有条件、循环、数据驱动；`data/` 目录目前是空的。`run` 是唯一的分支兜底。

**会疼的场景**
- “如果出现优惠弹窗就关闭”只能写进 `run` 脚本，变成一个大步骤，失去截图、重试、报告粒度。
- 同一流程要跑 20 组账号/数据，只能复制 20 份 YAML。
- 一旦团队习惯用 `run` 写业务逻辑，内核就退化成“启动器 + 证据采集器”。

**建议**
1. 先加低风险能力：`defaults`、`version`、`when`（基于上一步变量/URL/元素可见性）、`foreach`（配合 `--data`）。
2. 保持 `run` 作为逃生口，但规定“超过 N 行的业务逻辑应该沉淀成动作或页面片段”。
3. 如果条件/循环引入，步骤结果需要树形结构（block → children），当前 `FlowResult.steps` 平铺模型需要提前设计。
4. 数据驱动优先于复杂控制流：`sop run flow.yaml --data data/users.csv` 能覆盖大量重复场景。

**优先级**
P2。当前演示流程不需要，但在接入第二个真实业务前应该确定方向。

---

### P2-5 动作插件化与多浏览器

**现状**
`core/steps/registry.py` 通过扫描包内模块自动发现动作，只能扩展 `core/steps/` 内部；`Flow.browser` 支持 chromium/firefox/webkit，但示例只验证了 chromium。

**建议**
- 如果只有内部团队使用，保持现状即可，不建议现在做插件系统。
- 如果未来要按业务线分发动作，再增加 `--actions-dir` 或 entry points；同时固定动作契约测试。
- 多浏览器等有真实兼容性需求再补测试矩阵。

**优先级**
P2，明确可以先不动。

---

## 建议的落地顺序

**第 1 批（正确性）**
1. 给 `_run_step` / `_classify` 增加动作级重试安全声明。
2. 用绝对 deadline 重写预算计算，覆盖重试和 assert 多条件。
3. 增加 `tests/`：fake action 测重试/预算，本地 HTML 测定位，报告测脱敏。
4. 歧义定位先告警、再改为默认失败。

**第 2 批（架构返工点）**
1. 流程级 `locators` / `include`，让 `pages/` 真正进入 YAML。
2. 增加 `requires` 或 `setup`，消除 `03` 对 `01` 的隐式依赖。
3. 运行结果写 `result.json`，报告从结果文件渲染；补 JUnit。
4. 证据默认降体积，失败文件按步骤命名，增加清理命令。

**第 3 批（批量与非技术用户）**
1. 批量逐条容错、混合环境汇总、失败继续。
2. 惰性环境变量、显式敏感标记、`extract secret`。
3. `sop locate` / `sop new` / 行号错误 / JSON Schema / `.env`。
4. 视规模再考虑并发和报告历史索引。

---

## 附：本次验证用到的命令

```bash
export SAUCEDEMO_PASSWORD=secret_sauce
sop run flows/ --dry-run
sop run flows/ --env dev --trace
sop run /tmp/sop_assert_no_retry.yaml   # retries=3，断言只执行一次
sop run /tmp/sop_timeout_budget.yaml    # timeout=3，实际 3.9s
sop run /tmp/sop_failure_demo.yaml --shots every  # 失败证据与重试
```

这些数据说明：重试和断言不重试的基本方向是对的，但预算和多条件断言需要修正；报告和证据在演示规模可用，放量前需要瘦身和持久化。
