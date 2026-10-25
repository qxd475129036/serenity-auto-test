package com.example.autotest.features.demo;

import com.example.autotest.steps.demo.DemoSteps;
import net.serenitybdd.annotations.Epic;
import net.serenitybdd.annotations.Feature;
import net.serenitybdd.annotations.Steps;
import net.serenitybdd.annotations.Story;
import net.serenitybdd.annotations.Title;
import net.serenitybdd.junit5.SerenityJUnit5Extension;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;

@ExtendWith(SerenityJUnit5Extension.class)
@Epic("测试工程能力")
@Feature("活文档生成")
@Story("跨步骤共享场景状态")
@Tag("demo")
class SessionVariableDemoTest {

    @Steps
    DemoSteps demo;

    @Test
    @Title("Session Variable 跨步骤共享状态")
    void should_share_state_between_steps() throws Exception {
        demo.prepareScenario("session-variable");
        demo.performNestedStep("shared");

        demo.assertStoredResult("SHARED-PROCESSED");
    }
}
