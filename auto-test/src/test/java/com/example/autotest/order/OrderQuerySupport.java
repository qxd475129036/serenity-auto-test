package com.example.autotest.order;

import com.example.autotest.support.LocalOrderApi;
import io.restassured.response.Response;
import net.serenitybdd.rest.SerenityRest;

final class OrderQuerySupport {

    private OrderQuerySupport() {
    }

    static Response queryOrder(long orderId) {
        return SerenityRest.given()
                .baseUri(LocalOrderApi.shared().baseUrl())
                .accept("application/json")
                .get("/api/orders/{orderId}", orderId);
    }
}
