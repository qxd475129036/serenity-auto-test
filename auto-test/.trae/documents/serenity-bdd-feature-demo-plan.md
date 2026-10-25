# Serenity BDD 特性演示方案（扩展版）

## 1. 摘要

在当前 `batch-api-test-suite` 工程内新增一组可运行、可在 Serenity HTML 报告中直接观察效果的演示，按 5 个独立模块组织：

- **模块 A：核心注解与报告** — `@Epic` / `@Feature` / `@Story` / `@Title` / `@Narrative`、`@Tag`、`@Steps`、嵌套 `@Step`、Session Variable、`recordReportData`、文件证据、`@Pending`
- **模块 B：数据驱动与 REST** — `@ParameterizedTest` + `@CsvSource`、`@TestFactory`、`SerenityRest` 请求/响应记录、`lastResponse()`
- **模块 C：Screenplay** — `Actor` / `Ability` / `Task` / `Interaction` / `Question`，基于 `serenity-screenplay-rest`，不需要浏览器
- **模块 D：Gherkin / Cucumber** — `.feature` 文件、Step Definitions、Scenario Outline、`@Suite` + Cucumber JUnit Platform Engine、Serenity Cucumber 报告
- **模块 E：并行执行** — JUnit 5 并行配置 + `@Execution(CONCURRENT)` 的隔离 REST 演示；Cucumber 侧使用 `SerenityReporterParallel` 并行执行场景

本次需要新增 Maven 依赖：`serenity-screenplay`、`serenity-screenplay-rest`、`serenity-cucumber`、`cucumber-junit-platform-engine`、`junit-platform-suite`。

## 2. 现状分析

### 2.1 工程与依赖

- [pom.xml](file:///Users/quxd/git/auto-test/pom.xml) 使用 Spring Boot 4.0.9 parent、JDK 25、Serenity 5.3.3、Serenity Maven Plugin 5.3.10。
- 已有 `serenity-core`、`serenity-junit5`、`serenity-rest-assured`、H2、Oracle JDBC、Commons Exec。
- `spring-boot-starter-test` 传递引入 `junit-jupiter`，包含 `junit-jupiter-params`。
- `serenity-maven-plugin` 已绑定到 `post-integration-test` 的 `aggregate` goal。
- Surefire 通过 `<groups>${tags}</groups>` 按标签执行；`tags` 默认为空。

### 2.2 现有测试与步骤

- [ReconciliationBatchTest.java](file:///Users/quxd/git/auto-test/src/test/java/com/example/autotest/features/batch/ReconciliationBatchTest.java) 使用 `@Feature` / `@Story` / `@Steps` / `@Tag`。
- [OrderApiTest.java](file:///Users/quxd/git/auto-test/src/test/java/com/example/autotest/features/api/OrderApiTest.java) 默认通过 `@EnabledIfSystemProperty` 关闭，需要外部服务。
- [OracleSteps.java](file:///Users/quxd/git/auto-test/src/test/java/com/example/autotest/steps/OracleSteps.java)、[BatchShellSteps.java](file:///Users/quxd/git/auto-test/src/test/java/com/example/autotest/steps/BatchShellSteps.java)、[LogAssertionSteps.java](file:///Users/quxd/git/auto-test/src/test/java/com/example/autotest/steps/LogAssertionSteps.java) 可复用。
- 当前没有 Screenplay、Cucumber、并行配置、本地 REST stub、`serenity.properties`。

### 2.3 本地仓库与版本兼容性

已确认：

- 本地 `~/.m2` 已有 `serenity-screenplay:5.3.3`、`serenity-screenplay-rest:5.3.3`、`cucumber-java:7.34.2`。
- Maven Central 上存在 `serenity-cucumber:5.3.3`；其父 POM 定义 `cucumber.version=7.34.2`、`junit5.version=6.0.3`。
- 当前工程使用 JUnit 6.0.3，与 Serenity 5.3.3 父 POM 的 JUnit 版本一致。
- Serenity 官方文档的 Cucumber + JUnit 5 组合为 `serenity-cucumber` + `cucumber-junit-platform-engine:7.34.2` + `junit-platform-suite:6.0.3`。
- Serenity 5.x 的 Cucumber 报告插件为 `net.serenitybdd.cucumber.core.plugin.SerenityReporterParallel`（线程安全）。
- `@Pending` 在 JUnit 5 扩展中通过 `PendingTestException`（`TestAbortedException` 子类）处理，构建不会失败。

## 3. Maven 依赖变更

### 3.1 `pom.xml` 新增属性

```xml
<cucumber.version>7.34.2</cucumber.version>
<junit.platform.version>6.0.3</junit.platform.version>
```

### 3.2 `pom.xml` 新增测试依赖

```xml
<dependency>
    <groupId>net.serenity-bdd</groupId>
    <artifactId>serenity-screenplay</artifactId>
    <version>${serenity.version}</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>net.serenity-bdd</groupId>
    <artifactId>serenity-screenplay-rest</artifactId>
    <version>${serenity.version}</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>net.serenity-bdd</groupId>
    <artifactId>serenity-cucumber</artifactId>
    <version>${serenity.version}</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>io.cucumber</groupId>
    <artifactId>cucumber-junit-platform-engine</artifactId>
    <version>${cucumber.version}</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.junit.platform</groupId>
    <artifactId>junit-platform-suite</artifactId>
    <version>${junit.platform.version}</version>
    <scope>test</scope>
</dependency>
```

说明：

- `serenity-cucumber` 会传递引入 `serenity-screenplay-webdriver` 与 Selenium 相关 jar；本方案不启动浏览器，只使用 REST 能力。
- 首次构建需要联网下载 `serenity-cucumber`、`cucumber-junit-platform-engine`、`junit-platform-suite` 及其传递依赖。
- 实施第一步先执行依赖解析：

```bash
./mvnw -q dependency:resolve -DincludeScope=test
```

如果依赖解析失败，后续代码不写入，先解决版本/仓库问题。

## 4. 特性清单与演示矩阵

| 模块 | 特性 | 演示位置 | 报告中可观察的效果 |
| --- | --- | --- | --- |
| A 核心注解 | `@Epic` / `@Feature` / `@Story` | `LivingDocumentationDemoTest` | Requirements 页出现 Epic > Feature > Story 层级 |
| A 核心注解 | `@Narrative` | `LivingDocumentationDemoTest` | 需求页展示叙述文本 |
| A 核心注解 | `@Title` | 多个演示测试 | 场景标题覆盖默认方法名 |
| A 核心注解 | JUnit `@Tag` | 演示类 `@Tag("demo")` | 可用 `-Dtags=demo` 过滤，报告显示标签 |
| A Steps | `@Steps` 注入 | 所有基于步骤库的演示 | 步骤库被注入并记录 |
| A Steps | 嵌套 `@Step` + `{0}` 参数 | `DemoSteps` | 父子步骤树与参数值 |
| A Steps | 带返回值 `@Step` | `DemoSteps.performNestedStep` | 返回值步骤正常记录 |
| A 状态 | Session Variable | `DemoSteps` | 跨步骤共享状态 |
| A 证据 | `recordReportData().withTitle().andContents()` | `DemoSteps` | 场景中出现文本证据 |
| A 证据 | `recordReportData().withTitle().fromFile(Path)` | `DemoSteps` | 场景中出现可下载文件 |
| A 状态 | `@Pending` | `LivingDocumentationDemoTest` | 场景标记 Pending，构建不失败 |
| B 数据驱动 | `@ParameterizedTest` + `@CsvSource` | `DataDrivenDemoTest` | 单个场景聚合多组参数示例表格 |
| B 数据驱动 | `@TestFactory` | `DataDrivenDemoTest` | 多个动态测试聚合展示 |
| B REST | `SerenityRest` 请求/响应记录 | `OrderRestSteps` | 请求 URL、Header、响应体 |
| B REST | 状态码 / JSON Body 断言 | `OrderRestSteps` | 断言进入步骤报告 |
| B REST | `SerenityRest.lastResponse()` | `OrderRestSteps` | 复用最近一次响应 |
| C Screenplay | `Actor` / `Ability` | `ScreenplayRestDemoTest` | 报告显示 Actor 名称与描述 |
| C Screenplay | `Task` / `Interaction` | `QueryOrder` + `Get` / `Ensure` | 报告显示任务与交互步骤 |
| C Screenplay | `Question` | `OrderStatus` / `OrderStatusCode` | 报告显示提问与回答 |
| C Screenplay | `CallAnApi`（无浏览器） | `ScreenplayRestDemoTest` | Actor 持有 REST Ability |
| D Cucumber | Gherkin Feature / Scenario | `order_api.feature` | Requirements 页出现 Feature 与 Scenario |
| D Cucumber | Scenario Outline + Examples | `order_api.feature` | 报告中出现多组示例 |
| D Cucumber | Step Definitions | `OrderApiStepDefinitions` | 每个 Gherkin 步骤映射到 Java 步骤 |
| D Cucumber | Cucumber 标签 | `@demo` / `@smoke` / `@negative` | 可用 `-Dcucumber.filter.tags` 过滤 |
| D Cucumber | Serenity Cucumber 报告 | `SerenityReporterParallel` | Cucumber 场景进入 Serenity 报告 |
| E 并行 | JUnit 5 并行配置 | `junit-platform.properties` | 允许并行基础设施 |
| E 并行 | `@Execution(CONCURRENT)` | `ParallelRestDemoTest` | 4 个场景在不同线程并发执行 |
| E 并行 | Cucumber 场景并行 | Cucumber suite 配置 | 多个 Gherkin 场景并行执行 |
| 报告配置 | `serenity.project.name` | `serenity.properties` | 报告页显示项目名 |
| 报告聚合 | `serenity-maven-plugin` | 现有 `pom.xml` | `verify` 生成 `target/site/serenity/index.html` |
| CI 发布 | Jenkins `publishHTML` | 现有 `Jenkinsfile` | Jenkins 页面发布报告 |

### 4.1 本次不实现

| 特性 | 原因 |
| --- | --- |
| UI / Selenium / Page Object / 截图 | 需要浏览器与 WebDriver 环境；Cucumber 的 Selenium 传递依赖仅存在，不使用 |
| REST JSON Schema 校验 | 需要额外依赖，演示价值有限 |
| `@Manual` / `@Issue` 外部链接 | JUnit 5 下报告行为与 issue tracker 配置未验证 |
| `@StepGroup` / `@Shared` | 可选进阶项，不纳入最小演示集 |
| 并行执行中的 H2 / 批处理场景 | 共用 H2 文件库与日志文件，明确保持串行 |

## 5. 具体改动

### 5.1 新增 `src/test/resources/serenity.properties`

```properties
serenity.project.name=Batch API Test Suite - Serenity Feature Demo
```

使用英文避免 `serenity.properties` 默认编码导致中文乱码；Java 注解与 feature 文件中的中文不受影响。

### 5.2 更新 `src/test/resources/junit-platform.properties`

```properties
junit.jupiter.execution.parallel.enabled=true
junit.jupiter.execution.parallel.mode.default=same_thread
junit.jupiter.execution.parallel.config.strategy=dynamic
```

决策：

- 打开并行基础设施，但默认 `same_thread`，不改变现有 H2 / 批处理测试的执行方式。
- 只有显式标注 `@Execution(ExecutionMode.CONCURRENT)` 的类并发执行。
- 不设置 `mode.classes.default=concurrent`，避免误伤现有测试。

### 5.3 新增共享 REST stub：`src/test/java/com/example/autotest/support/LocalOrderApi.java`

职责：为模块 B/C/D/E 提供离线、线程安全的订单服务。

实现要点：

- 使用 JDK 自带 `com.sun.net.httpserver.HttpServer`，无新增依赖。
- 绑定 `127.0.0.1:0` 随机端口，避免端口冲突。
- `GET /api/orders/1` ~ `GET /api/orders/4` 返回 `200`：
  ```json
  {"id":1,"status":"PAID","amount":100.00}
  ```
- 其他 id 返回 `404`：
  ```json
  {"error":"ORDER_NOT_FOUND"}
  ```
- 返回 `Content-Type: application/json; charset=utf-8`。
- 提供 `static synchronized LocalOrderApi shared()`：进程内单例，首次调用时启动；注册 JVM shutdown hook 关闭。
- 线程池使用 daemon 线程（`Executors.newFixedThreadPool(2, daemonFactory)`），避免测试 JVM 挂起。
- 提供 `baseUrl()` 与幂等的 `stop()`。

### 5.4 模块 A：核心注解与报告

#### 5.4.1 新增 `src/test/java/com/example/autotest/steps/demo/DemoSteps.java`

方法：

- `@Step("准备演示场景: {0}") prepareScenario(String scenario)`
  - 在 `target/serenity-demo/` 下生成 `{scenario}.txt`。
  - `Serenity.recordReportData().withTitle("演示数据").andContents(...)`。
  - `Serenity.recordReportData().withTitle("演示证据文件").fromFile(path)`。
  - `Serenity.setSessionVariable("demo.scenario").to(scenario)`。
- `@Step("执行外层步骤: {0}") String performNestedStep(String input)`
  - 调用 `innerStep(input)`，结果转大写并写入 `demo.result`。
- `@Step("执行内层步骤: {0}") String innerStep(String input)`
  - 记录内层 `recordReportData`，返回 `input + "-processed"`。
- `@Step("应读取到上一步保存的结果: {0}") assertStoredResult(String expected)`
  - 用 `Serenity.sessionVariableCalled("demo.result")` 断言。

实现要点：

- `public`、无参构造，供 `@Steps` 注入。
- 内层步骤必须非 private，确保 Serenity 能拦截。
- 不修改现有步骤类。

#### 5.4.2 新增 `src/test/java/com/example/autotest/features/demo/LivingDocumentationDemoTest.java`

类级注解：

```java
@ExtendWith(SerenityJUnit5Extension.class)
@Epic("Serenity BDD 特性演示")
@Feature("需求与活文档")
@Story("注解生成报告结构与证据")
@Narrative(
        title = "需求与活文档演示",
        text = {
                "通过 @Epic/@Feature/@Story 建立报告中的需求层级。",
                "通过 @Title 为场景提供业务化标题。",
                "通过 @Tag(\"demo\") 演示标签过滤。"
        })
@Tag("demo")
class LivingDocumentationDemoTest {
```

测试方法：

1. `@Title("自定义场景标题与嵌套步骤")`
   - `demo.prepareScenario("living-documentation")`
   - 断言 `demo.performNestedStep("serenity")` 等于 `SERENITY-PROCESSED`
2. `@Title("Session Variable 跨步骤共享状态")`
   - `prepareScenario("session-variable")` → `performNestedStep("shared")` → `assertStoredResult("SHARED-PROCESSED")`
3. `@Pending @Title("待实现的演示场景")`
   - 调用 `demo.prepareScenario("pending")`，预期 Pending，不失败。

注意：不使用 JUnit `@DisplayName`，统一使用 `@Title`，避免 Serenity JUnit 5 扩展用 displayName 匹配测试方法时产生歧义。

### 5.5 模块 B：数据驱动与 REST

#### 5.5.1 新增 `src/test/java/com/example/autotest/features/demo/DataDrivenDemoTest.java`

类级：`@ExtendWith(SerenityJUnit5Extension.class)`、`@Epic(...)`、`@Feature("数据驱动测试")`、`@Story("同一场景使用多组数据执行")`、`@Tag("demo")`。

参数化测试：

```java
@ParameterizedTest(name = "业务日期 {0} 期望退出码 {1}")
@CsvSource({"2026-10-31, 0", "FAIL, 2"})
void should_produce_expected_exit_code(String businessDate, int expectedExitCode) throws Exception {
    oracle.reset();
    oracle.insertPendingTransactions(3);

    BatchCommandResult result = batch.runForDate(businessDate);

    assertThat(result.timedOut()).isFalse();
    assertThat(result.exitCode()).isEqualTo(expectedExitCode);
    oracle.summaryShouldHaveCount(expectedExitCode == 0 ? 1 : 0);
    oracle.transactionsShouldHaveStatus(expectedExitCode == 0 ? "RECONCILED" : "PENDING", 3);
}
```

动态测试：

```java
@TestFactory
Stream<DynamicTest> should_report_dynamic_scenarios() {
    return Stream.of("dynamic-a", "dynamic-b")
            .map(name -> dynamicTest("动态场景 " + name, () -> demo.prepareScenario(name)));
}
```

说明：复用现有 `OracleSteps` / `BatchShellSteps`；参数集由 `ParameterizedTestsOutcomeAggregator` 聚合；该类不参与 JUnit 并行（默认 `same_thread`）。

#### 5.5.2 新增 `src/test/java/com/example/autotest/steps/demo/OrderRestSteps.java`

- `@Step("查询订单 {1}，并校验 HTTP 状态与业务字段")`
  ```java
  SerenityRest.given()
          .baseUri(baseUri)
          .accept("application/json")
          .header("X-Demo-Channel", "serenity")
          .pathParam("orderId", orderId)
          .when()
          .get("/api/orders/{orderId}")
          .then()
          .statusCode(200)
          .body("id", equalTo((int) orderId))
          .body("status", equalTo(expectedStatus));
  ```
- `@Step("查询订单 {1}，应返回 404 与错误码")`：断言 `404` 与 `error=ORDER_NOT_FOUND`。
- `@Step("最近一次 REST 响应状态码应为 {0}")`：`SerenityRest.lastResponse().statusCode()`。

#### 5.5.3 新增 `src/test/java/com/example/autotest/features/demo/RestDemoTest.java`

- `@Epic(...)`、`@Feature("REST API 测试")`、`@Story("SerenityRest 记录请求与响应")`、`@Tag("demo")`。
- 通过 `LocalOrderApi.shared()` 获取 `baseUrl`。
- 测试：
  1. `@Title("REST 正向场景：读取订单")` — 查询订单 1，断言 `PAID`，再用 `lastResponseShouldHaveStatus(200)`。
  2. `@Title("REST 负向场景：订单不存在")` — 查询订单 999，断言 404。

### 5.6 模块 C：Screenplay

#### 5.6.1 新增 `src/test/java/com/example/autotest/screenplay/tasks/QueryOrder.java`

```java
public class QueryOrder implements Task {
    private final long orderId;

    private QueryOrder(long orderId) { this.orderId = orderId; }

    public static QueryOrder withId(long orderId) { return new QueryOrder(orderId); }

    @Override
    public <T extends Actor> void performAs(T actor) {
        actor.attemptsTo(
                Get.resource("/api/orders/{orderId}")
                        .with(request -> request.pathParam("orderId", orderId))
        );
        Response response = LastResponse.received().answeredBy(actor);
        actor.remember("httpStatus", response.statusCode());
        actor.remember("orderStatus", response.jsonPath().getString("status"));
    }

    @Override
    public String toString() { return "查询订单 " + orderId; }
}
```

#### 5.6.2 新增 `src/test/java/com/example/autotest/screenplay/questions/OrderStatus.java`

```java
public class OrderStatus implements Question<String> {
    public static OrderStatus value() { return new OrderStatus(); }

    @Override
    public String answeredBy(Actor actor) { return actor.recall("orderStatus"); }
}
```

#### 5.6.3 新增 `src/test/java/com/example/autotest/screenplay/questions/OrderStatusCode.java`

```java
public class OrderStatusCode implements Question<Integer> {
    public static OrderStatusCode value() { return new OrderStatusCode(); }

    @Override
    public Integer answeredBy(Actor actor) { return actor.recall("httpStatus"); }
}
```

#### 5.6.4 新增 `src/test/java/com/example/autotest/features/demo/ScreenplayRestDemoTest.java`

- 注解：`@ExtendWith(SerenityJUnit5Extension.class)`、`@Epic(...)`、`@Feature("Screenplay 模式")`、`@Story("Actor 通过 Task 与 Question 查询订单")`、`@Tag("demo")`。
- 测试 1：`@Title("Actor 执行 REST Task 并回答 Question")`
  ```java
  Actor tester = Actor.named("测试工程师")
          .describedAs("负责订单接口验证")
          .whoCan(CallAnApi.at(orderApi.baseUrl()));
  tester.attemptsTo(QueryOrder.withId(1));
  assertThat(tester.asksFor(OrderStatusCode.value())).isEqualTo(200);
  assertThat(tester.asksFor(OrderStatus.value())).isEqualTo("PAID");
  ```
- 测试 2：`@Title("Screenplay Ensure 交互断言")`
  ```java
  tester.attemptsTo(
          QueryOrder.withId(1),
          Ensure.that("订单 1 状态为 PAID", response -> {
              response.statusCode(200).body("status", equalTo("PAID"));
          })
  );
  ```
- 说明：不使用 `OnStage` / `OnlineCast`（那是 UI 场景常用方式）；非 UI 场景直接 `Actor.named(...).whoCan(CallAnApi.at(...))`，避免引入 WebDriver 生命周期。

### 5.7 模块 D：Gherkin / Cucumber

#### 5.7.1 新增 `src/test/resources/features/demo/order_api.feature`

```gherkin
@demo
Feature: 订单查询 API
  作为调用方
  我希望按订单号查询订单
  以便确认订单状态

  Background:
    Given 本地订单服务已启动

  @smoke
  Scenario: 查询存在的订单
    When 我查询订单 1
    Then 订单状态应为 PAID

  @smoke
  Scenario Outline: 按不同订单号查询订单
    When 我查询订单 <id>
    Then 订单状态应为 <status>

    Examples:
      | id | status |
      | 1  | PAID   |
      | 2  | PAID   |

  @negative
  Scenario: 查询不存在的订单
    When 我查询订单 999
    Then 应返回 404 错误
```

#### 5.7.2 新增 `src/test/java/com/example/autotest/features/cucumber/OrderApiStepDefinitions.java`

```java
public class OrderApiStepDefinitions {
    private Response response;

    @Given("本地订单服务已启动")
    public void localOrderServiceIsUp() {
        assertThat(LocalOrderApi.shared().baseUrl()).isNotBlank();
    }

    @When("我查询订单 {long}")
    public void queryOrder(long orderId) {
        response = SerenityRest.given()
                .baseUri(LocalOrderApi.shared().baseUrl())
                .accept("application/json")
                .get("/api/orders/{orderId}", orderId);
    }

    @Then("订单状态应为 {word}")
    public void orderStatusShouldBe(String expected) {
        assertThat(response.statusCode()).isEqualTo(200);
        assertThat(response.jsonPath().getString("status")).isEqualTo(expected);
    }

    @Then("应返回 {int} 错误")
    public void shouldReturnError(int expectedStatus) {
        assertThat(response.statusCode()).isEqualTo(expectedStatus);
        assertThat(response.jsonPath().getString("error")).isEqualTo("ORDER_NOT_FOUND");
    }
}
```

说明：Cucumber 每个场景使用独立实例，`response` 字段在并行场景间不会共享。

#### 5.7.3 新增 `src/test/java/com/example/autotest/features/cucumber/CucumberOrderApiTest.java`

```java
@Suite
@IncludeEngines("cucumber")
@SelectClasspathResource("features")
@ConfigurationParameter(
        key = PLUGIN_PROPERTY_NAME,
        value = "net.serenitybdd.cucumber.core.plugin.SerenityReporterParallel"
)
@ConfigurationParameter(
        key = GLUE_PROPERTY_NAME,
        value = "com.example.autotest.features.cucumber"
)
@ConfigurationParameter(key = "cucumber.execution.parallel.enabled", value = "true")
@ConfigurationParameter(key = "cucumber.execution.parallel.config.strategy", value = "dynamic")
@Tag("demo")
@Tag("cucumber")
class CucumberOrderApiTest {
}
```

说明：

- `@Suite` + `@IncludeEngines("cucumber")` 是 Serenity 5 官方推荐的 JUnit 5 运行方式。
- `SerenityReporterParallel` 负责把 Cucumber 场景写入 Serenity 报告。
- 类名以 `Test` 结尾，确保 Surefire 默认包含规则能发现该 Suite。
- `@Tag("demo")` 让 `-Dtags=demo` 能包含 Cucumber；`@Tag("cucumber")` 支持单独运行。
- Cucumber 场景标签使用 `-Dcucumber.filter.tags="@negative"` 过滤。

### 5.8 模块 E：并行执行

#### 5.8.1 JUnit 5 并行

已通过 [5.2](#52-更新-srctestresourcesjunit-platformproperties) 打开并行基础设施，默认 `same_thread`，仅显式 `CONCURRENT` 的类并发。

新增 `src/test/java/com/example/autotest/features/demo/ParallelRestDemoTest.java`：

```java
@ExtendWith(SerenityJUnit5Extension.class)
@Epic("Serenity BDD 特性演示")
@Feature("并行执行")
@Story("JUnit 5 场景并发执行")
@Execution(ExecutionMode.CONCURRENT)
@Tag("demo")
@Tag("parallel")
class ParallelRestDemoTest {

    @Test
    @Title("并行场景 1：查询订单 1")
    void should_query_order_1() { assertOrder(1); }

    @Test
    @Title("并行场景 2：查询订单 2")
    void should_query_order_2() { assertOrder(2); }

    @Test
    @Title("并行场景 3：查询订单 3")
    void should_query_order_3() { assertOrder(3); }

    @Test
    @Title("并行场景 4：查询订单 4")
    void should_query_order_4() { assertOrder(4); }

    private void assertOrder(long orderId) {
        Response response = SerenityRest.given()
                .baseUri(LocalOrderApi.shared().baseUrl())
                .accept("application/json")
                .get("/api/orders/{orderId}", orderId);

        assertThat(response.statusCode()).isEqualTo(200);
        assertThat(response.jsonPath().getLong("id")).isEqualTo(orderId);

        Serenity.recordReportData()
                .withTitle("执行线程")
                .andContents(Thread.currentThread().getName());
    }
}
```

隔离设计：

- 不访问 H2、不执行批处理、不写共享日志文件。
- 每个测试方法使用独立 `Response` 对象，不依赖全局 `SerenityRest.lastResponse()`。
- 共享的 `LocalOrderApi` 是线程安全的 HttpServer。
- 通过报告数据记录执行线程名，便于确认并发。

#### 5.8.2 Cucumber 场景并行

模块 D 的 Suite 已配置：

- `cucumber.execution.parallel.enabled=true`
- `cucumber.execution.parallel.config.strategy=dynamic`
- `SerenityReporterParallel` 线程安全插件

Feature 中的 3 个 Scenario / Scenario Outline 示例会并行执行。

### 5.9 更新 `README.md`

新增“Serenity 特性演示”一节，包含：

- 5 个模块与报告观察位置。
- 新建依赖说明。
- 运行命令：

```bash
./mvnw clean verify                                      # 全部测试
./mvnw clean verify -Dtags=demo                          # 仅演示（含 Cucumber、并行）
./mvnw clean verify -Dtags=cucumber                      # 仅 Cucumber
./mvnw clean verify -Dcucumber.filter.tags="@negative"   # 只跑负向 Gherkin 场景
./mvnw clean verify -Dtags=parallel                      # 仅 JUnit 并行演示
./mvnw clean verify -Dtags=smoke                         # 原有冒烟场景
./mvnw clean verify -Dtags=negative                      # 原有失败场景
```

- 报告地址：`target/site/serenity/index.html`。
- `@Pending` 预期为 Pending，不是构建失败。
- REST/Screenplay/Cucumber 演示使用本地 stub；外部 `OrderApiTest` 仍需 `-Dapi.enabled=true`。

### 5.10 不改动

- `Jenkinsfile`：现有 `publishHTML` 已覆盖新报告。
- 现有批处理/API/步骤类：不改。
- `maven-surefire-plugin` 现有 `systemPropertyVariables`：不改。

## 6. 假设与决策

1. Cucumber 采用 JUnit Platform Suite 方式，不使用 JUnit 4 `@RunWith(CucumberWithSerenity.class)`。
2. Cucumber 版本固定 7.34.2、JUnit Platform 6.0.3，与 Serenity 5.3.3 父 POM 和当前工程一致。
3. Screenplay 使用 `CallAnApi` 的非 UI 形态，不启动 WebDriver。
4. 标签策略：
   - JUnit 演示：`@Tag("demo")`
   - 并行演示：`@Tag("demo")` + `@Tag("parallel")`
   - Cucumber Suite：`@Tag("demo")` + `@Tag("cucumber")`
   - 原有测试：`smoke` / `negative` / `api`
5. 并行策略：默认 `same_thread`，只有 `@Execution(CONCURRENT)` 的 REST 演示并发；H2/批处理测试保持串行。
6. `@Pending` 用于演示状态，预期不失败。
7. 所有 REST 演示共用一个线程安全的本地 HttpServer；不依赖外部网络。
8. 不使用 `@DisplayName`；场景标题统一用 `@Title` / Gherkin Scenario 名称。

## 7. 风险与回退

| 风险 | 处理 |
| --- | --- |
| 新增依赖首次下载失败 | 实施前先 `dependency:resolve`；失败则暂停并报告，不写后续代码 |
| `serenity-cucumber` 传递引入 Selenium，下载体积大 | 接受；不使用浏览器，仅作为传递依赖存在 |
| Cucumber 引擎与 JUnit 6.0.3 不兼容 | 文档组合为 Serenity 5.3.7 + Cucumber 7.34.2 + JUnit 6.0.3；若运行失败，先降到 Serenity 5.3.10 的同版本组合或只保留 Screenplay/并行 |
| Cucumber Suite 的 `@Tag` 未被 Surefire 过滤 | 验证时检查 `-Dtags=demo` 是否包含 Cucumber；若不含，改用 `-Dtags=cucumber` 或全量运行作为文档命令 |
| JUnit Jupiter 并行下 Serenity 报告异常 | 保留 Cucumber 并行；移除 `ParallelRestDemoTest` 的 `@Execution(CONCURRENT)`，JUnit 侧退化为串行，但 Cucumber 并行仍可演示 |
| H2 / 批处理并发冲突 | 默认 `same_thread`，这些测试不使用 `@Execution(CONCURRENT)` |
| `SerenityRest.lastResponse()` 在并行下串扰 | 并行演示不使用该 API；Screenplay 使用 `LastResponse.received().answeredBy(actor)` 隔离到 Actor |

## 8. 验证步骤

1. 依赖解析：

```bash
./mvnw -q dependency:resolve -DincludeScope=test
```

2. 全量构建：

```bash
./mvnw clean verify
```

预期：构建成功；`@Pending` 为 Pending；Cucumber、Screenplay、并行演示均执行。

3. 仅演示：

```bash
./mvnw clean verify -Dtags=demo
```

预期：核心注解、数据驱动、REST、Screenplay、Cucumber、并行演示执行；原有 `smoke` / `negative` 不执行。

4. 仅 Cucumber：

```bash
./mvnw clean verify -Dtags=cucumber
./mvnw clean verify -Dcucumber.filter.tags="@negative"
```

预期：Gherkin 场景执行；标签过滤生效。

5. 仅并行：

```bash
./mvnw clean verify -Dtags=parallel
```

预期：4 个 REST 场景并发执行；报告中“执行线程”出现多个线程名。

6. 回归原有场景：

```bash
./mvnw clean verify -Dtags=smoke
./mvnw clean verify -Dtags=negative
```

预期：原有行为不变。

7. 报告检查 `target/site/serenity/index.html`：

- Requirements：`Serenity BDD 特性演示`、`订单查询 API`、Gherkin Feature/Scenario。
- `@Title` 标题与 `@Narrative` 叙述。
- `DemoSteps` 父子步骤与参数值。
- “演示数据”文本与可下载证据文件。
- Pending 场景。
- 参数化示例表格（2 组业务日期）。
- 动态测试条目。
- REST 请求 URL、`X-Demo-Channel` Header、响应 JSON。
- Screenplay Actor/Task/Question 步骤。
- Cucumber 场景与 Scenario Outline 示例。
- 并行场景的“执行线程”报告数据。
- 标签 `demo`、`cucumber`、`parallel`。
- 项目名 `Batch API Test Suite - Serenity Feature Demo`。
