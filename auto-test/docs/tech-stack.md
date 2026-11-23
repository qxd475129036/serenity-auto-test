# 技术栈与配置

## 版本

| 组件 | 版本 | 说明 |
| --- | --- | --- |
| JDK | 25 | pom `<java.version>` |
| Spring Boot（parent） | 4.0.9 | spring-boot-starter-parent |
| Spring Framework（spring-core / spring-jdbc） | 7.0.10 | 版本由 parent 管理；spring-core 的 `StandardEnvironment` 负责配置加载 |
| JUnit Jupiter（org.junit.jupiter） | 6.0.3 | 由 Spring Boot parent 管理，包名仍为 org.junit.jupiter |
| Serenity BDD（core / junit5 / rest-assured） | 5.3.3 | 属性 `serenity.version` |
| AssertJ | Spring Boot parent 管理 | test scope，断言库 |
| serenity-maven-plugin | 5.3.10 | `aggregate` 绑定 `post-integration-test`，生成报告 |
| Oracle ojdbc17 | 23.8.0.25.04 | test scope |
| H2 | Spring Boot parent 管理 | test scope |
| Apache Commons Exec | 1.4.0 | test scope，执行批处理 shell |
| Apache POI | 5.4.1 | test scope，读取 XLSX 批处理产物 |
| Hutool | 5.8.48 | test scope，文件/字符串/CSV/Excel 工具 |

全部依赖为 `test` scope，本工程是纯测试工程。

## 依赖 → 测试模式对照

| 依赖 | 支撑的模式 |
| --- | --- |
| serenity-core + serenity-junit5 | `@Epic/@Feature/@Story/@Title/@Steps/@Step/@Pending`、`@ExtendWith(SerenityJUnit5Extension.class)`、Session Variable、`recordReportData` |
| serenity-rest-assured | `SerenityRest` REST 直调，自动记录请求/响应证据 |
| assertj-core | `assertThat` 断言与失败诊断 |
| spring-jdbc + spring-core | `JdbcTemplate` + `DriverManagerDataSource` + `ResourceDatabasePopulator`；`StandardEnvironment` 读取 application 配置 |
| h2 / ojdbc17 | 本地 H2（Oracle 模式）/ staging Oracle |
| commons-exec | `CommandLine` + `ExecuteWatchdog` 执行批处理 shell |
| poi-ooxml | XLSX 单元格与整表断言 |
| hutool-all | 日志与产物文件读取、CSV 解析、Excel 打开与工作表定位 |

## 构建与运行

- 默认构建：`./mvnw clean verify`（配置来自 `application.properties`，H2 本地闭环）
- 标签过滤：`./mvnw clean verify -Dtags=smoke`（surefire `<groups>${tags}</groups>`，serenity-maven-plugin 报告使用同一 tags）
- surefire：`forkCount=1`、`reuseForks=true`、`testFailureIgnore=true`（仅让生命周期继续到报告生成）；测试失败由 `serenity:aggregate` 在生成报告后抛出，构建仍为红
- 报告：`target/site/serenity/index.html`

## Profile 与配置文件

Maven profile 只负责选择环境，不再承载具体配置项：

| Profile | `test.env` | 加载的配置文件 |
| --- | --- | --- |
| test（默认） | 未设置 → `local` | `application.properties` |
| staging | staging | `application.properties` + `application-staging.properties` |

- 配置值集中在 `src/test/resources/application.properties`（本地默认）与 `application-staging.properties`（staging 覆盖）
- 新增配置项只需改 properties 文件，不需要改 `pom.xml` 或 `TestSettings`
- staging 的数据库、批处理、API 参数继续从环境变量读取（`ORACLE_URL` / `BATCH_SHELL_PATH` / `API_BASE_URL` 等）

## 配置优先级（TestConfiguration）

`TestSettings` 委托 `TestConfiguration`，按以下优先级读取（高 → 低）：

1. `-D` 系统属性（如 `-Ddb.url=...`、`-Dapi.enabled=true`；surefire 自动透传，无需逐键映射）
2. 操作系统环境变量（属性名去点转大写：`db.url` → `DB_URL`，`db.kind` → `DB_KIND`）
3. `classpath:application-{env}.properties`（如 staging）
4. `classpath:application.properties`（本地默认）

`-Pstaging`、`-Dtest.env=staging`、`TEST_ENV=staging` 三种方式等价。属性值支持 Spring 占位符：`${ORACLE_URL}`、`${BATCH_DATE:2026-10-31}`；未设置且没有默认值时按缺失处理。缺失必填配置（如 `batch.shell.path`、`db.url`）抛 `IllegalStateException`，信息中带属性名与环境变量提示。

新增配置项示例：在 `application.properties` 加 `report.retention.days=30`，业务代码用 `settings.number("report.retention.days", 7)` 读取即可。

## 运行配置文件

- `application.properties` / `application-staging.properties`：业务配置（见上）
- `serenity.properties`：Serenity 框架配置，`serenity.project.name=Batch API Test Suite`
- `junit-platform.properties`：JUnit 平台配置（并行）；只放 `junit.*` 键

## 报告生成

`serenity-maven-plugin` 在 `post-integration-test` 阶段执行 `aggregate`，输出 `target/site/serenity/index.html`。即使存在失败场景也会先生成报告，随后 `aggregate` 按测试结果让构建失败。
