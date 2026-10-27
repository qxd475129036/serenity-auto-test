# 技术栈与配置

## 版本

| 组件 | 版本 | 说明 |
| --- | --- | --- |
| JDK | 25 | pom `<java.version>` |
| Spring Boot（parent） | 4.0.9 | spring-boot-starter-parent |
| JUnit Jupiter（org.junit.jupiter） | 6.0.3 | 由 Spring Boot parent 管理，包名仍为 org.junit.jupiter |
| Serenity BDD（core / junit5 / rest-assured / screenplay / screenplay-rest） | 5.3.3 | 属性 `serenity.version` |
| serenity-maven-plugin | 5.3.10 | `aggregate` 绑定 `post-integration-test`，生成报告 |
| Oracle ojdbc17 | 23.8.0.25.04 | test scope |
| H2 | Spring Boot parent 管理 | test scope |
| Apache Commons Exec | 1.4.0 | test scope，执行批处理 shell |

全部依赖为 `test` scope，本工程是纯测试工程。

## 依赖 → 测试模式对照

| 依赖 | 支撑的模式 |
| --- | --- |
| serenity-core + serenity-junit5 | `@Epic/@Feature/@Story/@Title/@Steps/@Step/@Pending`、`@ExtendWith(SerenityJUnit5Extension.class)`、Session Variable、`recordReportData` |
| serenity-rest-assured | `SerenityRest` REST 直调，自动记录请求/响应证据 |
| serenity-screenplay + serenity-screenplay-rest | `Actor` / `Task` / `Question` / `Get` / `Ensure` |
| spring-boot-starter-jdbc | `JdbcTemplate` + `DriverManagerDataSource` + `ResourceDatabasePopulator` |
| h2 / ojdbc17 | 本地 H2（Oracle 模式）/ staging Oracle |
| commons-exec | `CommandLine` + `ExecuteWatchdog` 执行批处理 shell |

## 构建与运行

- 默认构建：`./mvnw clean verify`（test profile 默认激活，H2 本地闭环）
- 标签过滤：`./mvnw clean verify -Dtags=smoke`（surefire `<groups>${tags}</groups>`，serenity-maven-plugin 报告使用同一 tags）
- surefire：`forkCount=1`、`reuseForks=true`、`testFailureIgnore=false`
- 报告：`target/site/serenity/index.html`

## Profile 对照

| 配置项 | test（默认） | staging |
| --- | --- | --- |
| db.kind | h2 | oracle |
| db.url | `jdbc:h2:file:target/test-db/reconciliation;MODE=Oracle;DATABASE_TO_UPPER=TRUE` | `-Ddb.url` 或环境变量 `ORACLE_URL` |
| db.user / db.password | sa / 空 | 环境变量 `ORACLE_USER` / `ORACLE_PASSWORD` |
| db.init | true（自动加载 schema） | false |
| batch.shell.path | `scripts/run_local_reconciliation.sh` | 环境变量 `BATCH_SHELL_PATH` |
| batch.log.dir | `target/batch-logs` | 环境变量 `BATCH_LOG_DIR` |
| batch.date | 2026-10-31 | 环境变量 `BATCH_DATE` |
| batch.timeout.seconds | 30 | 600 |
| api.enabled | false | true |
| api.base.url / api.order.id | `http://localhost:8080` / 1 | 环境变量 `API_BASE_URL` / `API_ORDER_ID` |

均可用 `-D` 直接覆盖（如 `-Ddb.url=...`、`-Dapi.enabled=true`）。

## 配置优先级（TestSettings）

`TestSettings` 按「JVM 系统属性 → 环境变量 → 默认值」读取每个配置项：

1. `-D` 系统属性（由 surefire `<systemPropertyVariables>` 注入）
2. 环境变量（名称 = 属性名去点转大写，如 `db.url` → `DB_URL`；兼容 `ORACLE_URL` / `ORACLE_USER` 等历史名称）
3. 默认值（H2 文件库、`batch.date=2026-10-31`、`api.enabled=false` 等）

缺失必填配置（如 `batch.shell.path`）直接抛 `IllegalStateException`，信息中带属性名与环境变量提示。

## 运行配置文件

- `serenity.properties`：`serenity.project.name=Batch API Test Suite`
- `junit-platform.properties`：JUnit 并行已启用（`parallel.enabled=true`），默认同线程内串行（`same_thread`），策略 `dynamic`；具体场景用 `@Execution(ExecutionMode.CONCURRENT)` 切换并发

## 报告生成

`serenity-maven-plugin` 在 `post-integration-test` 阶段执行 `aggregate`，输出 `target/site/serenity/index.html`。
