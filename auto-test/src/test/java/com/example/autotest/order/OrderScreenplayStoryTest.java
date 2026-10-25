package com.example.autotest.order;

import net.serenitybdd.annotations.Epic;
import net.serenitybdd.annotations.Feature;
import net.serenitybdd.annotations.Story;
import net.serenitybdd.annotations.Title;
import net.serenitybdd.junit5.SerenityJUnit5Extension;
import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.rest.interactions.Ensure;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.equalTo;

@ExtendWith(SerenityJUnit5Extension.class)
@Epic("订单服务")
@Feature("订单查询")
@Story("使用 Screenplay 查询订单")
@Tag("demo")
class OrderScreenplayStoryTest {

    @Test
    @Title("Actor 执行 REST Task 并回答 Question")
    @Tag("screenplay")
    void shouldQueryOrderThroughActor() {
        Actor tester = OrderQuerySupport.actor();

        tester.attemptsTo(OrderScreenplay.QueryOrder.withId(1));

        assertThat(tester.asksFor(OrderScreenplay.OrderStatusCode.value())).isEqualTo(200);
        assertThat(tester.asksFor(OrderScreenplay.OrderStatus.value())).isEqualTo("PAID");
    }

    @Test
    @Title("Screenplay Ensure 交互断言")
    @Tag("screenplay")
    void shouldVerifyOrderWithEnsure() {
        OrderQuerySupport.actor().attemptsTo(
                OrderScreenplay.QueryOrder.withId(1),
                Ensure.that("订单 1 状态为 PAID", response ->
                        response.statusCode(200).body("status", equalTo("PAID")))
        );
    }
}
