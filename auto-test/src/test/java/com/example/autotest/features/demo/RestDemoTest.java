package com.example.autotest.features.demo;

import com.example.autotest.steps.demo.OrderRestSteps;
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
@Epic("订单服务")
@Feature("按订单号查询")
@Story("查询已存在订单")
@Tag("demo")
class RestDemoTest {

    @Steps
    OrderRestSteps orders;

    @Test
    @Title("REST 正向场景：读取订单")
    void should_read_existing_order() {
        orders.orderShouldHaveStatus(1, "PAID");

        orders.lastResponseShouldHaveStatus(200);
    }
}
