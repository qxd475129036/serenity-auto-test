# 代码模板

可直接套用的骨架。`{...}` 为占位符，替换后须符合 requirements-hierarchy.md 的命名规范。
模板省略 import，写码时对照同类真实文件补齐。

## 模板 A：REST 查询 Story（SerenityRest 直调）

```java
package com.example.autotest.{域};

@ExtendWith(SerenityJUnit5Extension.class)
@Epic("{业务服务}")
@Feature("{功能域}")
@Story("{业务行为}")
@Tag("demo")
class {域}StoryTest {

    @Test
    @Title("{正常场景}")
    @Tag("smoke")
    void shouldQuery{Xxx}() {
        Response response = {域}QuerySupport.query{Xxx}(1);
        assertThat(response.statusCode()).isEqualTo(200);
        assertThat(response.jsonPath().getLong("id")).isEqualTo(1);
    }

    @Test
    @Title("查询不存在的{业务对象}返回 404")
    @Tag("negative")
    void shouldReturnNotFoundForUnknown{Xxx}() {
        Response response = {域}QuerySupport.query{Xxx}(999);
        assertThat(response.statusCode()).isEqualTo(404);
        assertThat(response.jsonPath().getString("error")).isEqualTo("{ERROR_CODE}");
    }

    @Test
    @Title("查询配置的外部{业务对象}")
    @Tag("api")
    @EnabledIfSystemProperty(named = "api.enabled", matches = "true")
    void shouldQueryConfiguredExternal{Xxx}() {
        // baseUri 用 settings.apiBaseUrl()，对象 id 用 settings.apiOrderId()
    }
}
```

## 模板 B：批处理 + 数据库 Story（四段式：清空 → 预置 → 执行 → 断言）

测试类（参考 `ReconciliationStoryTest`）：

```java
@ExtendWith(SerenityJUnit5Extension.class)
@Epic("{业务服务}")
@Feature("{功能域}")
@Story("{业务行为}")
@Tag("demo")
class {域}StoryTest {

    @Steps
    {域}Support {域};

    @Test
    @Title("{成功场景}")
    @Tag("smoke")
    void should{成功场景方法名}() throws Exception {
        {域}.reset();                      // 清空
        {域}.insert{预置数据}(3);          // 预置
        {域}.runConfigured{作业}();        // 执行

        {域}.{作业}ShouldFinishWithExitCode(0);
        {域}.logShouldContain("{成功关键字}");
        {域}.logShouldNotContain("ERROR");
        {域}.{记录}ShouldHaveStatus("{成功状态}", 3);
    }

    @Test
    @Title("{失败场景}")
    @Tag("negative")
    void should{失败场景方法名}() throws Exception {
        {域}.reset();
        {域}.insert{预置数据}(3);
        {域}.run{作业}("FAIL");

        {域}.{作业}ShouldFinishWithExitCode(2);
        {域}.logShouldContain("{失败关键字}");
        {域}.{记录}ShouldHaveStatus("{挂起状态}", 3);
    }
}
```

Support 类（参考 `ReconciliationSupport`）：

```java
public class {域}Support {

    private final TestSettings settings;
    private final JdbcTemplate jdbcTemplate;
    private {作业}Result result;

    public {域}Support() {
        this(new TestSettings());
    }

    {域}Support(TestSettings settings) {
        // DriverManagerDataSource + 驱动选择 + ResourceDatabasePopulator（见 step-conventions.md 第 7 节）
    }

    @Step("清空上一场景生成的{业务对象}测试数据")
    public void reset() { }

    @Step("向 {表名} 预置 {0} 笔待处理数据")
    public void insert{预置数据}(int count) { }

    @Step("执行配置业务日期的批处理")
    public void runConfigured{作业}() throws IOException {
        run{作业}(settings.batchDate());
    }

    @Step("执行业务日期为 {0} 的批处理")
    public void run{作业}(String businessDate) throws IOException {
        // commons-exec: CommandLine + ExecuteWatchdog + 环境变量注入（见 step-conventions.md 第 8 节）
    }

    @Step("批处理应未超时且退出码为 {0}")
    public void {作业}ShouldFinishWithExitCode(int expectedExitCode) { }

    @Step("日志应包含: {0}")
    public void logShouldContain(String expected) { }

    @Step("日志不应包含: {0}")
    public void logShouldNotContain(String unexpected) { }

    @Step("应存在 {1} 笔状态为 {0} 的记录")
    public void {记录}ShouldHaveStatus(String status, int expected) { }
}
```

## 模板 C：Screenplay（Task / Question / Ensure）

```java
public final class {域}Screenplay {

    private {域}Screenplay() {
    }

    public static final class Query{Xxx} implements Task {

        private final long id;

        private Query{Xxx}(long id) {
            this.id = id;
        }

        public static Query{Xxx} withId(long id) {
            return new Query{Xxx}(id);
        }

        @Override
        public <T extends Actor> void performAs(T actor) {
            actor.attemptsTo(Get.resource("/{路径}/{id}")
                    .with(request -> request.pathParam("id", id)));
            Response response = LastResponse.received().answeredBy(actor);
            actor.remember("httpStatus", response.statusCode());
        }

        @Override
        public String toString() {
            return "查询{业务对象} " + id;   // 中文 = 报告中的步骤文案
        }
    }

    public static final class {Xxx}StatusCode implements Question<Integer> {

        public static {Xxx}StatusCode value() {
            return new {Xxx}StatusCode();
        }

        @Override
        public Integer answeredBy(Actor actor) {
            return actor.recall("httpStatus");
        }
    }
}
```

测试类中的用法：

```java
Actor tester = {域}QuerySupport.actor();
tester.attemptsTo({域}Screenplay.Query{Xxx}.withId(1),
        Ensure.that("{业务对象} 1 状态为 PAID", response ->
                response.statusCode(200).body("status", equalTo("PAID"))));
assertThat(tester.asksFor({域}Screenplay.{Xxx}StatusCode.value())).isEqualTo(200);
```

## 模板 D：并行场景

```java
@Test
@Title("并行查询{业务对象} 1")
@Tag("parallel")
@Execution(ExecutionMode.CONCURRENT)
void shouldQuery{Xxx}OneInParallel() {
    // 查询逻辑；可记录执行线程作为证据：
    // Serenity.recordReportData().withTitle("执行线程").andContents(Thread.currentThread().getName());
}
```

## 模板 E：动态场景 + Pending

```java
@TestFactory
Stream<DynamicTest> shouldReportDynamic{场景族}() {
    return Stream.of("dynamic-a", "dynamic-b")
            .map(name -> dynamicTest("动态场景 " + name, () -> {域}.prepareScenario(name)));
}

@Test
@Pending
@Title("待实现的演示场景")
void shouldBeReportedAsPending() {
    // 场景已确认为需求但未实现
}
```

## 新业务域检查清单

1. 新建包 `com.example.autotest.{域}`
2. `{域}StoryTest.java`：层级注解按 requirements-hierarchy.md 决策树 + 场景按上面模板
3. `{域}Support.java`：步骤类按 step-conventions.md（`@Steps` 注入）
4. 涉及数据库：schema 放 `src/test/resources/db/{域}-schema.sql`，Support 构造器中初始化（`db.init=true` 时）
5. 涉及 REST 且无真实服务：在 `support/` 或同包加本地 stub（`LocalOrderApi` 模式）
6. 涉及 Screenplay：加 `{域}Screenplay` 类（模板 C）
7. `./mvnw clean verify`，按 verification.md「报告验证标准」核对
