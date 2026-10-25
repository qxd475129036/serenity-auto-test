package com.example.autotest.features.api;

import com.example.autotest.config.TestSettings;
import com.example.autotest.steps.ApiSteps;
import net.serenitybdd.annotations.Epic;
import net.serenitybdd.annotations.Feature;
import net.serenitybdd.annotations.Steps;
import net.serenitybdd.annotations.Story;
import net.serenitybdd.junit5.SerenityJUnit5Extension;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfSystemProperty;
import org.junit.jupiter.api.extension.ExtendWith;

@ExtendWith(SerenityJUnit5Extension.class)
@Epic("订单服务")
@Feature("按订单号查询")
@Story("查询已存在订单")
@EnabledIfSystemProperty(named = "api.enabled", matches = "true")
class OrderApiTest {

    private final TestSettings settings = new TestSettings();

    @Steps
    ApiSteps api;

    @Test
    @Tag("api")
    void should_return_order_by_id() {
        api.orderShouldExist(settings.apiOrderId());
    }
}
