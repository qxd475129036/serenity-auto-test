package com.example.autotest.features.cucumber;

import com.example.autotest.support.LocalOrderApi;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import io.restassured.response.Response;
import net.serenitybdd.rest.SerenityRest;

import static org.assertj.core.api.Assertions.assertThat;

public class OrderApiStepDefinitions {

    private Response response;

    @Given("本地订单服务已启动")
    public void localOrderServiceIsUp() {
        assertThat(LocalOrderApi.shared().baseUrl()).isNotBlank();
    }

    @When("我查询订单 {long}")
    public void queryOrder(long orderId) {
        response = SerenityRest.given()
                .baseUri(LocalOrderApi.shared().baseUrl())
                .accept("application/json")
                .get("/api/orders/{orderId}", orderId);
    }

    @Then("订单状态应为 {word}")
    public void orderStatusShouldBe(String expected) {
        assertThat(response.statusCode()).isEqualTo(200);
        assertThat(response.jsonPath().getString("status")).isEqualTo(expected);
    }

    @Then("应返回 {int} 错误")
    public void shouldReturnError(int expectedStatus) {
        assertThat(response.statusCode()).isEqualTo(expectedStatus);
        assertThat(response.jsonPath().getString("error")).isEqualTo("ORDER_NOT_FOUND");
    }
}
