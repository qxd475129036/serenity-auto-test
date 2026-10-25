package com.example.autotest.order;

import com.example.autotest.support.LocalOrderApi;
import io.restassured.response.Response;
import net.serenitybdd.rest.SerenityRest;
import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.rest.abilities.CallAnApi;

final class OrderQuerySupport {

    private OrderQuerySupport() {
    }

    static Response queryOrder(long orderId) {
        return SerenityRest.given()
                .baseUri(LocalOrderApi.shared().baseUrl())
                .accept("application/json")
                .get("/api/orders/{orderId}", orderId);
    }

    static Actor actor() {
        return Actor.named("测试工程师")
                .describedAs("负责订单接口验证")
                .whoCan(CallAnApi.at(LocalOrderApi.shared().baseUrl()));
    }
}
