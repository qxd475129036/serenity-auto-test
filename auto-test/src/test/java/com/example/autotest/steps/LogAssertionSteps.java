package com.example.autotest.steps;

import net.serenitybdd.annotations.Step;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.assertj.core.api.Assertions.assertThat;

public class LogAssertionSteps {

    @Step("日志 {0} 应包含: {1}")
    public void logShouldContain(Path logPath, String expected) throws IOException {
        String content = readLog(logPath);
        assertThat(content)
                .as("日志 %s 缺少预期内容", logPath)
                .contains(expected);
    }

    @Step("日志 {0} 不应包含: {1}")
    public void logShouldNotContain(Path logPath, String unexpected) throws IOException {
        String content = readLog(logPath);
        assertThat(content)
                .as("日志 %s 包含异常内容", logPath)
                .doesNotContain(unexpected);
    }

    private String readLog(Path logPath) throws IOException {
        assertThat(logPath).as("批处理日志不存在").exists();
        return Files.readString(logPath);
    }
}
