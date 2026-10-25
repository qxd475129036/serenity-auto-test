package com.example.autotest.steps;

import com.example.autotest.config.TestSettings;
import com.example.autotest.support.BatchCommandResult;
import net.serenitybdd.annotations.Step;
import org.apache.commons.exec.CommandLine;
import org.apache.commons.exec.DefaultExecutor;
import org.apache.commons.exec.ExecuteException;
import org.apache.commons.exec.ExecuteWatchdog;
import org.apache.commons.exec.PumpStreamHandler;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

public class BatchShellSteps {

    private final TestSettings settings = new TestSettings();

    @Step("执行本地批处理脚本，业务日期为 {0}")
    public BatchCommandResult runForDate(String businessDate) throws IOException {
        Path shellPath = Path.of(settings.batchShellPath()).toAbsolutePath().normalize();
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
            int exitCode = executor.execute(commandLine, batchEnvironment());
            return batchCommandResult(exitCode, stdout, stderr, false);
        } catch (ExecuteException exception) {
            return batchCommandResult(
                    exception.getExitValue(),
                    stdout,
                    stderr,
                    watchdog.killedProcess());
        }
    }

    @Step("批处理应以退出码 0 正常结束")
    public void shouldSucceed(BatchCommandResult result) {
        assertThat(result.timedOut())
                .as("批处理执行超时\n%s", result.diagnosticText())
                .isFalse();
        assertThat(result.exitCode())
                .as("批处理退出码非零\n%s", result.diagnosticText())
                .isZero();
    }

    @Step("批处理应以退出码 {1} 失败")
    public void shouldFailWith(BatchCommandResult result, int expectedExitCode) {
        assertThat(result.timedOut())
                .as("批处理应失败而不是超时\n%s", result.diagnosticText())
                .isFalse();
        assertThat(result.exitCode())
                .as("批处理退出码与预期不符\n%s", result.diagnosticText())
                .isEqualTo(expectedExitCode);
    }

    private Map<String, String> batchEnvironment() {
        Map<String, String> environment = new HashMap<>(System.getenv());
        environment.put("DB_KIND", settings.dbKind());
        environment.put("JDBC_URL", settings.dbUrl());
        environment.put("JDBC_USER", settings.dbUser());
        environment.put("JDBC_PASSWORD", settings.dbPassword());
        environment.put("JDBC_DRIVER_JAR", settings.jdbcDriverJar());
        environment.put("BATCH_LOG_FILE", settings.batchLogFile().toString());
        return environment;
    }

    private BatchCommandResult batchCommandResult(
            int exitCode,
            ByteArrayOutputStream stdout,
            ByteArrayOutputStream stderr,
            boolean timedOut) {
        return new BatchCommandResult(
                exitCode,
                stdout.toString(StandardCharsets.UTF_8),
                stderr.toString(StandardCharsets.UTF_8),
                timedOut);
    }
}
