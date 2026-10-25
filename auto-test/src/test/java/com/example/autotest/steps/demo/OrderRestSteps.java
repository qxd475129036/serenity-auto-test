package com.example.autotest.steps.demo;

import com.example.autotest.support.LocalOrderApi;
import io.restassured.response.Response;
import net.serenitybdd.annotations.Step;
import net.serenitybdd.rest.SerenityRest;

import static org.hamcrest.Matchers.equalTo;

public class OrderRestSteps {

    private final String baseUri = LocalOrderApi.shared().baseUrl();

    @Step("查询订单 {0}，并校验 HTTP 状态与业务字段: {1}")
    public void orderShouldHaveStatus(long orderId, String expectedStatus) {
        SerenityRest.given()
                .baseUri(baseUri)
                .accept("application/json")
                .header("X-Demo-Channel", "serenity")
                .pathParam("orderId", orderId)
                .when()
                .get("/api/orders/{orderId}")
                .then()
                .statusCode(200)
                .body("id", equalTo((int) orderId))
                .body("status", equalTo(expectedStatus));
    }

    @Step("查询订单 {0}，应返回 404 与错误码")
    public void orderShouldNotExist(long orderId) {
        SerenityRest.given()
                .baseUri(baseUri)
                .accept("application/json")
                .pathParam("orderId", orderId)
                .when()
                .get("/api/orders/{orderId}")
                .then()
                .statusCode(404)
                .body("error", equalTo("ORDER_NOT_FOUND"));
    }

    @Step("最近一次 REST 响应状态码应为 {0}")
    public void lastResponseShouldHaveStatus(int expectedStatus) {
        Response response = SerenityRest.lastResponse();
        org.assertj.core.api.Assertions.assertThat(response.statusCode()).isEqualTo(expectedStatus);
    }
}
