# 代码模板

可直接套用的骨架。`{...}` 为占位符，替换后须符合 requirements-hierarchy.md 的命名规范。
模板省略 import，写码时对照同类真实文件补齐。

## 模板 A：REST 查询 Story（SerenityRest 直调）

适用：接口可直连（真实服务或本地 stub），以查询/读取为主，需要对 `Response` 做细粒度断言。
结构：测试类持有 `TestSettings` 并直接断言；Support 只负责发请求，不写断言。
外部 API 场景用 `assumeTrue(settings.apiEnabled(), "...")` 门控（静态导入 `Assumptions.assumeTrue`），不要用 `@EnabledIfSystemProperty`。

```java
package com.example.autotest.{域};

@ExtendWith(SerenityJUnit5Extension.class)
@Epic("{业务服务}")
@Feature("{功能域}")
@Story("{业务行为}")
@Tag("demo")
class {域}StoryTest {

    private final TestSettings settings = new TestSettings();

    @Test
    @Title("{正常场景}")
    @Tag("smoke")
    void shouldQuery{Xxx}() {
        assertExisting{Xxx}(1);
    }

    @Test
    @Title("查询不存在的{业务对象}返回 404")
    @Tag("negative")
    void shouldReturnNotFoundForUnknown{Xxx}() {
        Response response = {域}QuerySupport.query{Xxx}(999);

        assertThat(response.statusCode())
                .as("{业务对象}查询应返回 404，实际响应:\n%s", response.asPrettyString())
                .isEqualTo(404);
        assertThat(response.jsonPath().getString("error"))
                .as("404 响应应带业务错误码")
                .isEqualTo("{ERROR_CODE}");
        assertThat(response.jsonPath().getMap("$"))
                .as("失败响应不应返回业务数据")
                .doesNotContainKey("id");
    }

    @Test
    @Title("查询参数非法的{业务对象}返回 400")
    @Tag("negative")
    void shouldRejectInvalid{Xxx}() {
        Response response = {域}QuerySupport.query{Xxx}(-1);

        assertThat(response.statusCode())
                .as("非法入参应被拒绝，实际响应:\n%s", response.asPrettyString())
                .isEqualTo(400);
        assertThat(response.jsonPath().getString("error"))
                .isEqualTo("{INVALID_ARGUMENT_CODE}");
    }

    @Test
    @Title("查询配置的外部{业务对象}")
    @Tag("api")
    void shouldQueryConfiguredExternal{Xxx}() {
        assumeTrue(settings.apiEnabled(), "api.enabled=false，跳过外部{业务对象}场景");

        Response response = SerenityRest.given()
                .baseUri(settings.apiBaseUrl())
                .accept("application/json")
                .get("/api/{资源}/{id}", settings.apiOrderId());

        assertThat(response.statusCode())
                .as("外部{业务对象} API 响应状态码异常:\n%s", response.asPrettyString())
                .isEqualTo(200);
        assertThat(response.jsonPath().getLong("id"))
                .as("外部 API 返回了错误的{业务对象}")
                .isEqualTo(settings.apiOrderId());
    }

    private void assertExisting{Xxx}(long id) {
        Response response = {域}QuerySupport.query{Xxx}(id);

        assertThat(response.statusCode()).isEqualTo(200);
        assertThat(response.jsonPath().getLong("id")).isEqualTo(id);
        assertThat(response.jsonPath().getString("status")).isEqualTo("{正常状态}");
    }
}
```

Support 骨架（参考 `OrderQuerySupport`，package-private 静态工具类）：

```java
final class {域}QuerySupport {

    private {域}QuerySupport() {
    }

    static Response query{Xxx}(long id) {
        return SerenityRest.given()
                .baseUri({Stub}.shared().baseUrl())   // 换真实环境时改成 settings.apiBaseUrl()
                .accept("application/json")
                .pathParam("id", id)
                .get("/api/{资源}/{id}");
    }
}
```

套用要点：

- Support 只发请求并返回 `Response`，断言全部留在测试类，这样 200 / 400 / 404 能各自独立成场景。
- `SerenityRest` 会自动把 URL、Header、响应体写入报告，因此 Support 不需要 `@Step`；这是它与模板 B 最大的结构差异。
- 断言统一用 `.as(...)` 并附 `response.getBody().asString()`，失败时报告里能直接看到响应体（`asPrettyString()` 在部分响应上会触发 RestAssured 解析异常）。
- 外部依赖场景用 `@Tag("api")` + `assumeTrue(settings.apiEnabled(), ...)` 门控，不要用 `@Disabled`。
- 失败分支按接口真实契约补充（400 参数校验、401/403 权限等）；接口没有对应契约就删掉该场景，不要为凑模板保留。

## 模板 B：批处理 + 数据库 Story（四段式：清空 → 预置 → 执行 → 断言）

适用：本地批处理脚本 + 数据库落库，需要同时验证退出码、日志和最终数据状态。
结构：测试类只做编排；执行细节与断言全部收敛在 Support 的 `@Step` 方法里。

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
        {域}.{汇总}ShouldHaveCount(1);
    }

    @Test
    @Title("{失败场景}")
    @Tag("negative")
    void should{失败场景方法名}() throws Exception {
        {域}.reset();
        {域}.insert{预置数据}(3);
        {域}.run{作业}("FAIL");            // 显式业务参数触发模拟失败

        {域}.{作业}ShouldFinishWithExitCode(2);
        {域}.logShouldContain("{失败关键字}");
        {域}.{汇总}ShouldHaveCount(0);     // 失败时不得写入结果
        {域}.{记录}ShouldHaveStatus("{挂起状态}", 3);
    }

    @Test
    @Title("{非法入参场景}")
    @Tag("negative")
    void should{非法入参场景方法名}() throws Exception {
        {域}.reset();
        {域}.insert{预置数据}(3);
        {域}.run{作业}("{非法业务日期}");   // 如 "2026-13-01"

        {域}.{作业}ShouldFinishWithExitCode({参数错误退出码});   // 示例脚本为 64
        {域}.logShouldContain("{参数错误关键字}");
        {域}.{汇总}ShouldHaveCount(0);
        {域}.{记录}ShouldHaveStatus("{挂起状态}", 3);
    }
}
```

Support 骨架（参考 `ReconciliationSupport`）：

```java
public class {域}Support {

    private final TestSettings settings;
    private final JdbcTemplate jdbcTemplate;
    private final BatchFileValidationSupport fileValidation = new BatchFileValidationSupport();
    private final AtomicInteger runSequence = new AtomicInteger();

    private {作业}Result result;

    public {域}Support() {                 // 供 @Steps 注入
        this(new TestSettings());
    }

    {域}Support(TestSettings settings) {   // 供其他场景复用
        this.settings = settings;
        DriverManagerDataSource dataSource = new DriverManagerDataSource(
                settings.dbUrl(), settings.dbUser(), settings.dbPassword());
        dataSource.setDriverClassName("h2".equalsIgnoreCase(settings.dbKind())
                ? "org.h2.Driver" : "oracle.jdbc.OracleDriver");
        this.jdbcTemplate = new JdbcTemplate(dataSource);
        if (settings.initializeDatabase()) {
            new ResourceDatabasePopulator(
                    new ClassPathResource("db/{域}-schema.sql")).execute(dataSource);
        }
    }

    @Step("清空上一场景生成的{业务对象}测试数据")
    public void reset() {
        jdbcTemplate.update("DELETE FROM {子表}");
        jdbcTemplate.update("DELETE FROM {主表}");
    }

    @Step("向 {表名} 预置 {0} 笔待处理数据")
    public void insert{预置数据}(int count) {
        jdbcTemplate.batchUpdate(
                "INSERT INTO {表名}(id, status, amount) VALUES(?, '{待处理状态}', ?)",
                LongStream.rangeClosed(1, count).boxed().toList(),
                count,
                (statement, id) -> {
                    statement.setLong(1, id);
                    statement.setBigDecimal(2, new BigDecimal("100.00"));
                });
    }

    @Step("执行配置业务日期的批处理")
    public void runConfigured{作业}() throws IOException {
        run{作业}(settings.batchDate());
    }

    @Step("执行业务日期为 {0} 的批处理")
    public void run{作业}(String businessDate) throws IOException {
        Path logFile = newLogFile();       // 每次执行独立日志
        CommandLine commandLine = new CommandLine("bash");
        commandLine.addArgument(settings.batchShellPath(), false);
        commandLine.addArgument("--date", false);
        commandLine.addArgument(businessDate, false);

        ByteArrayOutputStream stdout = new ByteArrayOutputStream();
        ByteArrayOutputStream stderr = new ByteArrayOutputStream();
        ExecuteWatchdog watchdog = ExecuteWatchdog.builder()
                .setTimeout(Duration.ofSeconds(settings.batchTimeoutSeconds()))
                .get();
        DefaultExecutor executor = DefaultExecutor.builder()
                .setWorkingDirectory(settings.projectDir().toFile())
                .setExecuteStreamHandler(new PumpStreamHandler(stdout, stderr))
                .get();
        executor.setWatchdog(watchdog);
        executor.setExitValues(new int[0]);   // 非 0 退出码不抛异常，留给断言分支判断

        try {
            int exitCode = executor.execute(commandLine, batchEnvironment(logFile));
            result = new {作业}Result(exitCode, stdout.toString(StandardCharsets.UTF_8),
                    stderr.toString(StandardCharsets.UTF_8), watchdog.killedProcess(), logFile);
        } catch (ExecuteException exception) {
            result = new {作业}Result(exception.getExitValue(),
                    stdout.toString(StandardCharsets.UTF_8),
                    stderr.toString(StandardCharsets.UTF_8),
                    watchdog.killedProcess(), logFile);
        }
    }

    @Step("批处理应未超时且退出码为 {0}")
    public void {作业}ShouldFinishWithExitCode(int expectedExitCode) {
        assertThat(result)
                .as("批处理尚未执行")
                .isNotNull();
        assertThat(result.timedOut())
                .as("批处理执行超时\n%s", result.diagnosticText())
                .isFalse();
        assertThat(result.exitCode())
                .as("批处理退出码与预期不符\n%s", result.diagnosticText())
                .isEqualTo(expectedExitCode);
    }

    @Step("日志应包含: {0}")
    public void logShouldContain(String expected) throws IOException {
        fileValidation.logShouldContain(result.logFile(), expected);
    }

    @Step("日志不应包含: {0}")
    public void logShouldNotContain(String unexpected) throws IOException {
        fileValidation.logShouldNotContain(result.logFile(), unexpected);
    }

    @Step("应存在 {1} 笔状态为 {0} 的记录")
    public void {记录}ShouldHaveStatus(String status, int expected) {
        Integer actual = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM {表名} WHERE status = ?", Integer.class, status);
        assertThat(actual)
                .as("状态为 %s 的记录数不符", status)
                .isEqualTo(expected);
    }

    @Step("{汇总表}中应有 {0} 条{汇总对象}记录")
    public void {汇总}ShouldHaveCount(int expected) {
        Integer actual = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM {汇总表}", Integer.class);
        assertThat(actual).isEqualTo(expected);
    }

    private Path newLogFile() {
        FileUtil.mkdir(settings.batchLogDirectory().toFile());
        return settings.batchLogFile("{作业}-%s-%02d.log".formatted(
                LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss-SSS")),
                runSequence.incrementAndGet()));
    }

    private Map<String, String> batchEnvironment(Path logFile) {
        Map<String, String> environment = new HashMap<>(System.getenv());
        environment.put("DB_KIND", settings.dbKind());
        environment.put("JDBC_URL", settings.dbUrl());
        environment.put("JDBC_USER", settings.dbUser());
        environment.put("JDBC_PASSWORD", settings.dbPassword());
        environment.put("JDBC_DRIVER_JAR", settings.jdbcDriverJar());
        environment.put("BATCH_LOG_FILE", logFile.toString());
        return environment;
    }

    private record {作业}Result(int exitCode, String stdout, String stderr,
                                boolean timedOut, Path logFile) {

        private String diagnosticText() {
            return """
                    exitCode=%d, timedOut=%s, logFile=%s
                    stdout:
                    %s
                    stderr:
                    %s
                    """.formatted(exitCode, timedOut, logFile, stdout, stderr);
        }
    }
}
```

套用要点：

- 四段式顺序固定：`reset()` 必须在最前（H2 文件库跨用例共享），断言集中在最后，避免边执行边断言。
- 可复用的动作（清空 / 预置 / 执行）和断言各做成独立 `@Step`；测试类只按业务顺序调用，不出现 SQL 或 shell。
- `executor.setExitValues(new int[0])` 是关键：否则非 0 退出码会直接抛 `ExecuteException`，失败场景就无法断言"预期退出码"；捕获后仍要保存 stdout/stderr 供诊断。
- 断言失败一律 `.as(...)` 带 `diagnosticText()`（退出码、是否超时、日志路径、stdout/stderr），报告里可直接定位。
- 每次执行生成独立日志文件，`logShouldContain` / `logShouldNotContain` 只读本次运行的日志，避免上个用例残留污染。
- 失败/边界分支按脚本真实契约补：参数非法、超时、数据库不可用等各有独立退出码时分别建场景，不要合并成"任意非 0"。
- schema 放 `src/test/resources/db/{域}-schema.sql`，仅当 `db.init=true` 时由 `ResourceDatabasePopulator` 执行。

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
6. `./mvnw clean verify`，按 verification.md「报告验证标准」核对
