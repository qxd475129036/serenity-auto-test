# 项目: auto-test (batch-api-test-suite)

基于 Serenity BDD 5、JUnit Jupiter 和 Spring JDBC 的测试套件。测试按业务域组织，需求层级通过
`@Epic` / `@Feature` / `@Story` 描述，构建后自动生成 HTML 报告。本文件是 AI 入口：先读本文件，
再按需读 `docs/` 中的规则文档。

## 技术栈（摘要）

JDK 25 · Spring Boot 4.0.9（parent）· JUnit Jupiter（org.junit.jupiter，版本由 Spring Boot parent 管理）
· Serenity BDD 5.3.3（serenity-junit5 / rest-assured / screenplay-rest）· Spring JdbcTemplate
· H2（Oracle 模式）/ Oracle ojdbc17 · Apache Commons Exec

构建入口统一用 `./mvnw`（Maven wrapper，无需全局 Maven）。详见 [docs/tech-stack.md](docs/tech-stack.md)。

## 目录地图

```text
src/test/java/com/example/autotest/
├── config/         TestSettings 统一配置（系统属性 → 环境变量 → 默认值）
├── support/        跨域共享设施（LocalOrderApi 本地 HTTP stub）
├── order/          订单服务 域：3 个 Story（查询 / Screenplay / 并行）+ 步骤设施
├── reconciliation/ 交易对账 域：1 个 Story（日终对账）+ 步骤设施
└── documentation/  测试工程能力 域：1 个 Story（活文档）+ 证据步骤
src/test/resources/db/    H2 schema SQL
src/test/resources/       serenity.properties · junit-platform.properties
scripts/                 本地批处理脚本（run_local_reconciliation.sh）
docs/                    AI 规则文档（本目录）
```

本工程是纯测试工程（无 `src/main`）。业务域包与 `@Epic` 语义一一对应。

## 必读文档（AI 入口索引）

- 需求层级规则（Epic / Feature / Story / Title 命名与拆分决策）: [docs/requirements-hierarchy.md](docs/requirements-hierarchy.md)
- 步骤与断言规范（Support / @Step / 证据 / Session Variable / REST / 批处理 / 数据库）: [docs/step-conventions.md](docs/step-conventions.md)
- 代码模板（可直接套用的骨架 + 新业务域检查清单）: [docs/code-templates.md](docs/code-templates.md)
- 构建、验证、标签过滤、staging 环境与批处理契约: [docs/verification.md](docs/verification.md)
- 技术栈、依赖、profile 与配置优先级: [docs/tech-stack.md](docs/tech-stack.md)

## 硬性禁令

- 报告文案（`@Epic` / `@Feature` / `@Story` / `@Title` / `@Step` 字符串与 Screenplay 中文文案）必须使用中文业务语言；Java 方法名保持英文 camelCase（`should...`）
- 一个 Story 对应且仅对应一个测试类（class-level `@Story`）；两个测试类不得共用同一个 `@Story` 字符串
- 测试类只表达业务场景；SQL、HTTP 调用、shell 执行细节一律收敛进同包的 `*Support` 步骤类，通过 `@Steps` 注入
- `@Epic` / `@Feature` 是报告聚合键：先用 `rg -n '@Epic\("' src` / `rg -n '@Feature\("' src` 匹配仓库已有值，再决定是否新建；同一含义写成不同文案会在报告中劈裂出两个 Feature
- 不引入 [docs/tech-stack.md](docs/tech-stack.md) 清单之外的 Maven 依赖
- 优先使用真实 H2（Oracle 模式）+ `com.sun.net.httpserver` 本地 stub，不引入新的 mock 框架
- 提交前必跑 `./mvnw clean verify`，并按 [docs/verification.md](docs/verification.md) 的“报告验证标准”确认报告

## 任务流程

接到新需求（新增需求 / 场景 / 业务域）时：

1. 定层级：按 [docs/requirements-hierarchy.md](docs/requirements-hierarchy.md) 的决策树确定 `@Epic` / `@Feature` / `@Story` 与场景拆分
2. 选模板：按测试模式（REST 直调 / Screenplay / 批处理+DB / 活文档）从 [docs/code-templates.md](docs/code-templates.md) 选模板
3. 写代码：遵循 [docs/step-conventions.md](docs/step-conventions.md)；新业务域走其中“新业务域检查清单”
4. 验证：`./mvnw clean verify` 并按 [docs/verification.md](docs/verification.md) 核对报告
5. 按以下格式汇报：

```text
需求层级: Epic「...」 > Feature「...」 > Story「...」
新增文件: 文件路径列表
场景: 共 N 个（smoke x / negative x / api x / ...）
构建: 通过 | 失败（附失败原因）
报告: target/site/serenity/index.html
```

## 任务指令模板

> 读 AGENTS.md → docs/requirements-hierarchy.md → docs/code-templates.md，在 {域} 新增「{需求名}」：
> （业务行为、输入、预期结果）。按上述规则生成 Story 测试类与步骤设施，跑 `./mvnw clean verify` 并按格式汇报。
