package com.example.autotest.features.demo;

import com.example.autotest.screenplay.questions.OrderStatus;
import com.example.autotest.screenplay.questions.OrderStatusCode;
import com.example.autotest.screenplay.tasks.QueryOrder;
import com.example.autotest.support.LocalOrderApi;
import net.serenitybdd.annotations.Epic;
import net.serenitybdd.annotations.Feature;
import net.serenitybdd.annotations.Story;
import net.serenitybdd.annotations.Title;
import net.serenitybdd.junit5.SerenityJUnit5Extension;
import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.rest.abilities.CallAnApi;
import net.serenitybdd.screenplay.rest.interactions.Ensure;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.equalTo;

@ExtendWith(SerenityJUnit5Extension.class)
@Epic("订单服务")
@Feature("按订单号查询")
@Story("查询已存在订单")
@Tag("demo")
class ScreenplayRestDemoTest {

    @Test
    @Title("Actor 执行 REST Task 并回答 Question")
    void should_query_order_through_actor() {
        Actor tester = Actor.named("测试工程师")
                .describedAs("负责订单接口验证")
                .whoCan(CallAnApi.at(LocalOrderApi.shared().baseUrl()));

        tester.attemptsTo(QueryOrder.withId(1));

        assertThat(tester.asksFor(OrderStatusCode.value())).isEqualTo(200);
        assertThat(tester.asksFor(OrderStatus.value())).isEqualTo("PAID");
    }

    @Test
    @Title("Screenplay Ensure 交互断言")
    void should_verify_response_with_ensure_interaction() {
        Actor tester = Actor.named("测试工程师")
                .describedAs("负责订单接口验证")
                .whoCan(CallAnApi.at(LocalOrderApi.shared().baseUrl()));

        tester.attemptsTo(
                QueryOrder.withId(1),
                Ensure.that("订单 1 状态为 PAID", response ->
                        response.statusCode(200).body("status", equalTo("PAID")))
        );
    }
}
