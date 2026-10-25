package com.example.autotest.documentation;

import net.serenitybdd.annotations.Epic;
import net.serenitybdd.annotations.Feature;
import net.serenitybdd.annotations.Pending;
import net.serenitybdd.annotations.Steps;
import net.serenitybdd.annotations.Story;
import net.serenitybdd.annotations.Title;
import net.serenitybdd.junit5.SerenityJUnit5Extension;
import org.junit.jupiter.api.DynamicTest;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestFactory;
import org.junit.jupiter.api.extension.ExtendWith;

import java.util.stream.Stream;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.DynamicTest.dynamicTest;

@ExtendWith(SerenityJUnit5Extension.class)
@Epic("测试工程能力")
@Feature("测试报告")
@Story("生成活文档")
@Tag("demo")
class LivingDocumentationStoryTest {

    @Steps
    ReportEvidence evidence;

    @Test
    @Title("自定义场景标题与嵌套步骤")
    void shouldBuildNestedStepTree() throws Exception {
        evidence.prepareScenario("living-documentation");

        assertThat(evidence.performNestedStep("serenity")).isEqualTo("SERENITY-PROCESSED");
    }

    @Test
    @Title("Session Variable 跨步骤共享状态")
    void shouldShareStateBetweenSteps() throws Exception {
        evidence.prepareScenario("session-variable");
        evidence.performNestedStep("shared");

        evidence.assertStoredResult("SHARED-PROCESSED");
    }

    @TestFactory
    Stream<DynamicTest> shouldReportDynamicScenarios() {
        return Stream.of("dynamic-a", "dynamic-b")
                .map(name -> dynamicTest(
                        "动态场景 " + name,
                        () -> evidence.prepareScenario(name)));
    }

    @Test
    @Pending
    @Title("待实现的演示场景")
    void shouldBeReportedAsPending() throws Exception {
        evidence.prepareScenario("pending");
    }
}
