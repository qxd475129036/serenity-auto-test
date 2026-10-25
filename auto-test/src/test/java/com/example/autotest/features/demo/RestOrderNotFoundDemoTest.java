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
@Story("查询不存在订单")
@Tag("demo")
class RestOrderNotFoundDemoTest {

    @Steps
    OrderRestSteps orders;

    @Test
    @Title("REST 负向场景：订单不存在")
    void should_return_404_for_unknown_order() {
        orders.orderShouldNotExist(999);

        orders.lastResponseShouldHaveStatus(404);
    }
}
