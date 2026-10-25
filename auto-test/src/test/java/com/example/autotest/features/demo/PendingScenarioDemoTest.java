package com.example.autotest.features.demo;

import com.example.autotest.steps.demo.DemoSteps;
import net.serenitybdd.annotations.Epic;
import net.serenitybdd.annotations.Feature;
import net.serenitybdd.annotations.Pending;
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
@Story("标记待实现场景")
@Tag("demo")
class PendingScenarioDemoTest {

    @Steps
    DemoSteps demo;

    @Test
    @Pending
    @Title("待实现的演示场景")
    void should_be_reported_as_pending() throws Exception {
        demo.prepareScenario("pending");
    }
}
