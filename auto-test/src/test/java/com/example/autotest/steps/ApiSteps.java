package com.example.autotest.steps;

import com.example.autotest.config.TestSettings;
import io.restassured.response.Response;
import net.serenitybdd.annotations.Step;
import net.serenitybdd.rest.SerenityRest;

import static org.assertj.core.api.Assertions.assertThat;

public class ApiSteps {

    private final TestSettings settings = new TestSettings();

    @Step("查询订单 {0} 并校验响应")
    public void orderShouldExist(long orderId) {
        Response response = SerenityRest.given()
                .baseUri(settings.apiBaseUrl())
                .accept("application/json")
                .when()
                .get("/api/orders/{orderId}", orderId);

        assertThat(response.statusCode())
                .as("订单 API 响应状态码异常: %s", response.asPrettyString())
                .isEqualTo(200);
        assertThat(response.jsonPath().getLong("id"))
                .as("订单 API 返回了错误的订单")
                .isEqualTo(orderId);
    }
}
