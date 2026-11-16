package com.example.autotest.reconciliation;

import cn.hutool.core.io.FileUtil;
import cn.hutool.core.util.StrUtil;
import com.example.autotest.config.TestSettings;
import com.example.autotest.support.BatchFileValidationSupport;
import net.serenitybdd.annotations.Step;
import org.apache.commons.exec.CommandLine;
import org.apache.commons.exec.DefaultExecutor;
import org.apache.commons.exec.ExecuteException;
import org.apache.commons.exec.ExecuteWatchdog;
import org.apache.commons.exec.PumpStreamHandler;
import org.springframework.core.io.ClassPathResource;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.jdbc.datasource.init.ResourceDatabasePopulator;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.LongStream;

import static org.assertj.core.api.Assertions.assertThat;

public class ReconciliationSupport {

    private static final AtomicInteger RUN_SEQUENCE = new AtomicInteger();
    private static final DateTimeFormatter LOG_TIMESTAMP =
            DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss-SSS");

    private final TestSettings settings;
    private final JdbcTemplate jdbcTemplate;
    private final BatchFileValidationSupport fileValidation = new BatchFileValidationSupport();

    private BatchResult result;

    public ReconciliationSupport() {
        this(new TestSettings());
    }

    ReconciliationSupport(TestSettings settings) {
        this.settings = settings;
        DriverManagerDataSource dataSource = new DriverManagerDataSource(
                settings.dbUrl(),
                settings.dbUser(),
                settings.dbPassword());
        dataSource.setDriverClassName(
                "h2".equalsIgnoreCase(settings.dbKind())
                        ? "org.h2.Driver"
                        : "oracle.jdbc.OracleDriver");
        this.jdbcTemplate = new JdbcTemplate(dataSource);
        if (settings.initializeDatabase()) {
            new ResourceDatabasePopulator(
                    new ClassPathResource("db/reconciliation-schema.sql"))
                    .execute(dataSource);
        }
    }

    @Step("清空上一场景生成的对账测试数据")
    public void reset() {
        jdbcTemplate.update("DELETE FROM reconciliation_summary");
        jdbcTemplate.update("DELETE FROM transactions");
    }

    @Step("向 TRANSACTIONS 预置 {0} 笔待对账交易")
    public void insertPendingTransactions(int count) {
        String sql = "INSERT INTO transactions(id, status, amount) VALUES(?, 'PENDING', ?)";
        List<Long> transactionIds = LongStream.rangeClosed(1, count).boxed().toList();
        jdbcTemplate.batchUpdate(
                sql,
                transactionIds,
                count,
                (statement, transactionId) -> {
                    statement.setLong(1, transactionId);
                    statement.setBigDecimal(2, new BigDecimal("100.00"));
                });
    }

    @Step("执行配置业务日期的批处理")
    public void runConfiguredBatch() throws IOException {
        runBatch(settings.batchDate());
    }

    @Step("执行业务日期为 {0} 的批处理")
    public void runBatch(String businessDate) throws IOException {
        Path shellPath = Path.of(settings.batchShellPath()).toAbsolutePath().normalize();
        Path logFile = newLogFile();
        CommandLine commandLine = new CommandLine("bash");
        commandLine.addArgument(shellPath.toString(), false);
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
        executor.setExitValues(new int[0]);

        try {
            int exitCode = executor.execute(commandLine, batchEnvironment(logFile));
            result = new BatchResult(
                    exitCode,
                    stdout.toString(StandardCharsets.UTF_8),
                    stderr.toString(StandardCharsets.UTF_8),
                    false,
                    logFile);
        } catch (ExecuteException exception) {
            result = new BatchResult(
                    exception.getExitValue(),
                    stdout.toString(StandardCharsets.UTF_8),
                    stderr.toString(StandardCharsets.UTF_8),
                    watchdog.killedProcess(),
                    logFile);
        }
    }

    @Step("批处理应未超时且退出码为 {0}")
    public void batchShouldFinishWithExitCode(int expectedExitCode) {
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
        fileValidation.logShouldContain(currentLogFile(), expected);
    }

    @Step("日志不应包含: {0}")
    public void logShouldNotContain(String unexpected) throws IOException {
        fileValidation.logShouldNotContain(currentLogFile(), unexpected);
    }

    @Step("汇总表中应有 {0} 条对账记录")
    public void summaryShouldHaveCount(int expected) {
        Integer actual = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM reconciliation_summary",
                Integer.class);
        assertThat(actual).isEqualTo(expected);
    }

    @Step("应存在 {1} 笔状态为 {0} 的交易")
    public void transactionsShouldHaveStatus(String status, int expected) {
        Integer actual = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM transactions WHERE status = ?",
                Integer.class,
                status);
        assertThat(actual).isEqualTo(expected);
    }

    private Path newLogFile() {
        FileUtil.mkdir(settings.batchLogDirectory().toFile());
        String fileName = StrUtil.format("reconciliation-{}-{}.log",
                LocalDateTime.now().format(LOG_TIMESTAMP),
                StrUtil.padPre(String.valueOf(RUN_SEQUENCE.incrementAndGet()), 2, '0'));
        return settings.batchLogFile(fileName);
    }

    private Path currentLogFile() {
        assertThat(result)
                .as("批处理尚未执行，无法校验日志")
                .isNotNull();
        return result.logFile();
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

    private record BatchResult(
            int exitCode,
            String stdout,
            String stderr,
            boolean timedOut,
            Path logFile) {

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
