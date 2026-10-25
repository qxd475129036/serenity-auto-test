package com.example.autotest.features.demo;

import com.example.autotest.steps.demo.DemoSteps;
import net.serenitybdd.annotations.Epic;
import net.serenitybdd.annotations.Feature;
import net.serenitybdd.annotations.Narrative;
import net.serenitybdd.annotations.Steps;
import net.serenitybdd.annotations.Story;
import net.serenitybdd.annotations.Title;
import net.serenitybdd.junit5.SerenityJUnit5Extension;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;

import static org.assertj.core.api.Assertions.assertThat;

@ExtendWith(SerenityJUnit5Extension.class)
@Epic("测试工程能力")
@Feature("活文档生成")
@Story("生成嵌套步骤树")
@Narrative(
        title = "需求与活文档演示",
        text = {
                "通过 @Epic/@Feature/@Story 建立报告中的需求层级。",
                "通过 @Title 为场景提供业务化标题。",
                "通过 @Tag(\"demo\") 演示标签过滤。"
        })
@Tag("demo")
class LivingDocumentationDemoTest {

    @Steps
    DemoSteps demo;

    @Test
    @Title("自定义场景标题与嵌套步骤")
    void should_build_nested_step_tree() throws Exception {
        demo.prepareScenario("living-documentation");

        assertThat(demo.performNestedStep("serenity")).isEqualTo("SERENITY-PROCESSED");
    }
}
