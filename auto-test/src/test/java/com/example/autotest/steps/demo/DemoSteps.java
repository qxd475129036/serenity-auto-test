package com.example.autotest.steps.demo;

import net.serenitybdd.annotations.Step;
import net.serenitybdd.core.Serenity;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.assertj.core.api.Assertions.assertThat;

public class DemoSteps {

    @Step("准备演示场景: {0}")
    public void prepareScenario(String scenario) throws IOException {
        Path evidenceFile = Path.of(
                System.getProperty("user.dir"), "target", "serenity-demo", scenario + ".txt");
        Files.createDirectories(evidenceFile.getParent());
        Files.writeString(
                evidenceFile,
                "演示场景: " + scenario + System.lineSeparator(),
                StandardCharsets.UTF_8);

        Serenity.setSessionVariable("demo.scenario").to(scenario);
        Serenity.recordReportData()
                .withTitle("演示数据")
                .andContents("当前场景: " + scenario);
        Serenity.recordReportData()
                .withTitle("演示证据文件")
                .downloadable()
                .fromFile(evidenceFile);
    }

    @Step(value = "执行外层步骤: {0}", callNestedMethods = true)
    public String performNestedStep(String input) {
        String result = innerStep(input).toUpperCase();
        Serenity.setSessionVariable("demo.result").to(result);
        return result;
    }

    @Step("执行内层步骤: {0}")
    public String innerStep(String input) {
        Serenity.recordReportData()
                .withTitle("内层步骤数据")
                .andContents("输入: " + input);
        return input + "-processed";
    }

    @Step("应读取到上一步保存的结果: {0}")
    public void assertStoredResult(String expected) {
        assertThat(Serenity.<Object>sessionVariableCalled("demo.result"))
                .isEqualTo(expected);
    }
}
