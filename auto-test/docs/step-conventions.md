# 步骤与断言规范

本文档回答：`*Support` 步骤类怎么写、`@Step` 文案怎么写、REST / 数据库 / 批处理 / 证据怎么表达。

## 1. Support 步骤类结构

参考 `ReconciliationSupport` 与 `ReportEvidence`：

- 命名：`{域}Support`（证据类可叫 `{域}Evidence`），`public class`，与测试类同包
- 类内只用 Serenity 注解（如 `@Step`），无 JUnit 注解
- 构造器：`public` 无参（供 `@Steps` 注入）+ 包级构造器注入 `TestSettings`（供复用）
- 状态（批处理退出码、捕获的响应等）放 Support 的私有字段；测试类通过 `@Steps` 注入：

```java
@Steps
ReconciliationSupport reconciliation;
```

- 方法分工：动作步骤（清空 / 预置 / 执行）+ 断言步骤（`...Should...`）；同一业务逻辑写成一个方法，被多个场景复用
- 轻量变体：无状态的纯查询助手可用包私有静态工具类（order 包的 `OrderQuerySupport`）；有状态或需要证据时优先 `@Steps` 实例注入

## 2. @Step 文案规则

- 中文；动作步骤以动词开头：
  - 「清空上一场景生成的对账测试数据」
  - 「向 TRANSACTIONS 预置 {0} 笔待对账交易」
  - 「执行配置业务日期的批处理」
- 断言步骤用「应 / 不应」：
  - 「批处理应未超时且退出码为 {0}」
  - 「日志应包含: {0}」 / 「日志不应包含: {0}」
  - 「汇总表中应有 {0} 条对账记录」
- 参数占位符 `{0}` `{1}` 按顺序对应方法形参；文案把最关键的量放在最显眼位置
- 步骤文案描述业务含义：断言对象是表名、日志关键字时可以写入；不写 SQL 语句、HTTP 路径、Java 实现细节
- 断言失败用 AssertJ，并通过 `.as("批处理退出码与预期不符\n%s", 诊断文本)` 附加业务可读的失败原因

## 3. 嵌套步骤与返回值

- 「包装多个子步骤」的步骤：`@Step(value = "执行外层步骤: {0}", callNestedMethods = true)`，内部方法同样标 `@Step`（见 `ReportEvidence.performNestedStep` / `innerStep`）；报告显示父子步骤树
- 步骤可以带返回值（如 `String performNestedStep(String input)`），返回值在报告中可见，测试类也可直接断言返回值

## 4. Session Variable 与报告证据

- Session Variable（跨步骤共享状态）：
  - 写：`Serenity.setSessionVariable("demo.scenario").to(scenario)`
  - 读：`Serenity.<Object>sessionVariableCalled("demo.result")`
  - key 命名：`{域}.{含义}`
- 文本证据：`Serenity.recordReportData().withTitle("演示数据").andContents("当前场景: " + scenario)`
- 文件证据（报告生成可下载附件）：先写文件到 `target/` 下，再
  `Serenity.recordReportData().withTitle("演示证据文件").downloadable().fromFile(evidenceFile)`

## 5. REST 两种模式

**直调（默认选择）**：

```java
Response response = SerenityRest.given()
        .baseUri(LocalOrderApi.shared().baseUrl())
        .accept("application/json")
        .get("/api/orders/{orderId}", orderId);
assertThat(response.statusCode()).isEqualTo(200);
```

Serenity 自动把请求 URL、Header、响应体记录进报告；断言用 AssertJ 对 `Response`。

**Screenplay（需要在报告中体现 Actor / Task / Question 时使用）**：

- Actor：`Actor.named("测试工程师").describedAs("负责订单接口验证").whoCan(CallAnApi.at(baseUrl))`
- Task：`implements Task`，`performAs` 用 `Get.resource(...).with(...)` 发请求，结果存 `actor.remember(...)`；**必须重写 `toString()` 返回中文**（它就是报告中显示的步骤文案，如「查询订单 1」）
- Question：`implements Question<T>`，`answeredBy` 读 `actor.recall("key")`
- 交互断言：`Ensure.that("订单 1 状态为 PAID", response -> response.statusCode(200).body("status", equalTo("PAID")))`，第一参数为中文
- 测试类中：`tester.attemptsTo(task)` + `tester.asksFor(question)`

**本地 stub**：`com.sun.net.httpserver.HttpServer`，绑定端口 `0`（自动取空闲端口），路径处理器返回 JSON；单例 `shared()` + 注册 shutdown hook（`LocalOrderApi` 模式）。

## 6. 外部 API 门控

依赖真实外部服务的场景在方法上加 JUnit 条件：

```java
@EnabledIfSystemProperty(named = "api.enabled", matches = "true")
```

默认 profile `api.enabled=false`，本地构建自动跳过这些场景、不影响构建；staging 置 true。

## 7. 数据库模式

```java
DriverManagerDataSource dataSource = new DriverManagerDataSource(url, user, password);
dataSource.setDriverClassName("h2".equalsIgnoreCase(settings.dbKind())
        ? "org.h2.Driver" : "oracle.jdbc.OracleDriver");
this.jdbcTemplate = new JdbcTemplate(dataSource);
if (settings.initializeDatabase()) {
    new ResourceDatabasePopulator(new ClassPathResource("db/reconciliation-schema.sql")).execute(dataSource);
}
```

- 连接参数全部来自 `TestSettings`（优先级见 tech-stack.md），不硬编码 URL
- 断言 SQL 写进 Support 的 `@Step` 方法（如 `transactionsShouldHaveStatus`）
- schema 放 `src/test/resources/db/{域}-schema.sql`

## 8. 批处理 shell 模式

- commons-exec 执行：`CommandLine` + `DefaultExecutor` + `ExecuteWatchdog`（超时 `settings.batchTimeoutSeconds()`），工作目录为工程根
- 通过环境变量把数据库连接注入脚本：`DB_KIND` / `JDBC_URL` / `JDBC_USER` / `JDBC_PASSWORD` / `JDBC_DRIVER_JAR` / `BATCH_LOG_FILE`
- 业务参数用 `--date <业务日期>` 传递（本地脚本中 `FAIL` 触发模拟失败）
- 结果存私有 `BatchResult`（exitCode / stdout / stderr / 是否超时），断言步骤读取它做断言
- 批处理脚本契约（退出码、日志位置）见 [verification.md](verification.md)
