# Batch API Test Suite

基于 Obsidian「自动化测试架构」笔记实现的 Java 测试工程。默认使用 H2 文件数据库完成本地闭环，`staging` profile 通过环境变量连接真实批处理与 Oracle，不在仓库中保存任何凭据。

## 技术栈

- JDK 25
- Spring Boot 4.0.9 统一依赖版本
- JUnit 6 + Serenity BDD 5.3.3
- Apache Commons Exec 执行批处理并设置超时
- JdbcTemplate 执行数据库准备与断言
- Serenity REST Assured 提供可选 API 场景
- Jenkins 通过 `publishHTML` 发布 `target/site/serenity`

## 本地运行

```bash
./mvnw clean verify
```

本地 profile 会执行两个 Scenario：

1. 预置 3 笔待对账交易，执行本地 fixture 脚本，校验退出码、日志、汇总表和交易状态。
2. 模拟批处理失败，校验失败退出码、失败日志，以及数据未被错误修改。

运行指定标签：

```bash
./mvnw clean verify -Dtags=smoke
./mvnw clean verify -Dtags=negative
```

报告地址：`target/site/serenity/index.html`。

## Serenity 特性演示

演示按 5 个模块组织，全部使用本地 fixture 或本地 REST stub，不依赖外部服务：

| 模块 | 演示内容 | 报告观察位置 |
| --- | --- | --- |
| 核心注解与报告 | `@Epic`/`@Feature`/`@Story`/`@Narrative`/`@Title`/`@Tag`、`@Steps`、嵌套与带返回值 `@Step`、Session Variable、`recordReportData`、文件证据、`@Pending` | Requirements 层级、场景步骤树、场景中的“演示数据”和可下载证据文件 |
| 数据驱动与 REST | `@ParameterizedTest` + `@CsvSource`、`@TestFactory`、`SerenityRest` 请求响应记录、`lastResponse()` | 参数化示例表格、动态测试条目、请求 URL/Header/响应 JSON |
| Screenplay | `Actor`/`Ability`/`Task`/`Interaction`/`Question`，使用 `CallAnApi`，不启动浏览器 | Actor 名称、REST 交互步骤、Ensure 断言步骤 |
| Gherkin / Cucumber | `.feature`、Step Definitions、Scenario Outline、标签 | `订单服务 > 按订单号查询`，以及 Scenario 与 Examples |
| 并行执行 | JUnit 5 `@Execution(CONCURRENT)`、Cucumber 场景并行 | 并行场景中的“执行线程”报告数据 |

Cucumber 使用 `junit-platform-suite` + `cucumber-junit-platform-engine`，并通过 `SerenityReporterParallel` 写入 Serenity 报告。

运行命令：

```bash
./mvnw clean verify                                      # 全部测试
./mvnw clean verify -Dtags=demo                          # 仅演示（含 Cucumber、并行）
./mvnw clean verify -Dtags=cucumber                      # 仅 Cucumber
./mvnw clean verify -Dcucumber.filter.tags="@negative"   # Gherkin 仅跑负向场景（其他测试仍执行）
./mvnw clean verify -Dtags=parallel                      # JUnit 与 Cucumber 并行演示
./mvnw clean verify -Dtags=smoke                         # 冒烟场景（批处理 + Gherkin）
./mvnw clean verify -Dtags=negative                      # 失败场景（批处理 + Gherkin）
```

说明：

- `@Pending` 场景在报告中显示为 Pending，不会导致构建失败。
- REST、Screenplay、Cucumber 演示共用进程内 `LocalOrderApi` stub；外部 `OrderApiTest` 仍需 `-Dapi.enabled=true`。
- JUnit 5 默认 `same_thread`，只有 `ParallelRestDemoTest` 显式并发，H2 与批处理测试保持串行。

## 需求层级约定

Serenity 报告按 `Capability > Feature > Story > Scenario` 汇总测试结果：

- `@Epic` 表示业务能力，例如“订单服务”“交易对账”。
- `@Feature` 表示用户功能，例如“按订单号查询”“日终对账处理”。
- `@Story` 表示可验证的用户价值或行为。
- `@Test`、Cucumber Scenario 是最底层执行场景。
- `@Tag` 只用于测试筛选，不参与需求分层。

纯测试框架能力的演示统一归入“测试工程能力 > 活文档生成”。

Jenkins 使用仓库根目录的 `Jenkinsfile`。首次配置时需要确保 `maven-builder`
节点安装 JDK 25、支持 Maven Wrapper，并为 Serenity 报告配置 HTML Publisher。
Jenkins 的默认 CSP 可能阻止报告脚本和样式加载，需要在全局安全配置中按
Jenkins 版本允许 `target/site/serenity` 所需的脚本、样式和图片资源。

## 真实环境

`staging` profile 从环境和 Maven 参数读取配置：

```bash
export ORACLE_URL='jdbc:oracle:thin:@//staging-db:1521/ORCLPDB1'
export ORACLE_USER='test_user'
export ORACLE_PASSWORD='test_password'
export BATCH_SHELL_PATH='/opt/batch/run_reconciliation.sh'
export BATCH_LOG_DIR='/opt/batch/logs'
export BATCH_DATE='2026-10-31'
export API_BASE_URL='https://staging.example.com'
export API_ORDER_ID='10001'

./mvnw clean verify -Pstaging -Dtags=smoke
```

也可直接使用 Maven 参数覆盖：`-Ddb.url=... -Ddb.user=... -Ddb.password=... -Dbatch.shell.path=...`。

## 批处理脚本契约

外部批处理脚本至少需要：

- 接受 `--date <business-date>`。
- 成功时返回退出码 `0`，失败时返回非零退出码。
- 把日志写入 `BATCH_LOG_DIR/reconciliation.log`。
- 接收 `DB_KIND`、`JDBC_URL`、`JDBC_USER`、`JDBC_PASSWORD` 环境变量；真实 Oracle 脚本通常只使用自己的数据源配置，本地 fixture 使用这些变量。

`BatchShellSteps` 默认超时 600 秒，可通过 `-Dbatch.timeout.seconds=...` 覆盖。

## API 场景

API 测试默认关闭，避免本地没有服务时污染构建。配置 `-Dapi.enabled=true -Dapi.base.url=...` 后执行，或在 `staging` profile 中通过环境变量启用。

## Oracle 断言约定

`OracleSteps` 默认使用以下表：

```sql
transactions(id, status, amount)
reconciliation_summary(run_date, reconciled_count, status)
```

如果测试环境表名或字段不同，应调整 `OracleSteps`，不要把拼接 SQL 下沉到 Scenario。
