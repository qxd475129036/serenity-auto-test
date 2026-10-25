package com.example.autotest.features.demo;

import com.example.autotest.steps.demo.DemoSteps;
import net.serenitybdd.annotations.Epic;
import net.serenitybdd.annotations.Feature;
import net.serenitybdd.annotations.Steps;
import net.serenitybdd.annotations.Story;
import net.serenitybdd.junit5.SerenityJUnit5Extension;
import org.junit.jupiter.api.DynamicTest;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.TestFactory;
import org.junit.jupiter.api.extension.ExtendWith;

import java.util.stream.Stream;

import static org.junit.jupiter.api.DynamicTest.dynamicTest;

@ExtendWith(SerenityJUnit5Extension.class)
@Epic("测试工程能力")
@Feature("活文档生成")
@Story("动态场景报告")
@Tag("demo")
class DynamicScenarioDemoTest {

    @Steps
    DemoSteps demo;

    @TestFactory
    Stream<DynamicTest> should_report_dynamic_scenarios() {
        return Stream.of("dynamic-a", "dynamic-b")
                .map(name -> dynamicTest("动态场景 " + name, () -> demo.prepareScenario(name)));
    }
}
