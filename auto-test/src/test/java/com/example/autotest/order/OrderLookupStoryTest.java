package com.example.autotest.order;

import com.example.autotest.config.TestSettings;
import io.restassured.response.Response;
import net.serenitybdd.annotations.Epic;
import net.serenitybdd.annotations.Feature;
import net.serenitybdd.annotations.Story;
import net.serenitybdd.annotations.Title;
import net.serenitybdd.junit5.SerenityJUnit5Extension;
import net.serenitybdd.rest.SerenityRest;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfSystemProperty;
import org.junit.jupiter.api.extension.ExtendWith;

import static org.assertj.core.api.Assertions.assertThat;

@ExtendWith(SerenityJUnit5Extension.class)
@Epic("订单服务")
@Feature("订单查询")
@Story("按订单号查询订单")
@Tag("demo")
class OrderLookupStoryTest {

    private final TestSettings settings = new TestSettings();

    @Test
    @Title("查询订单 1")
    @Tag("smoke")
    void shouldQueryOrderOne() {
        assertExistingOrder(1);
    }

    @Test
    @Title("查询订单 2")
    @Tag("smoke")
    void shouldQueryOrderTwo() {
        assertExistingOrder(2);
    }

    @Test
    @Title("查询不存在的订单返回 404")
    @Tag("negative")
    void shouldReturnNotFoundForUnknownOrder() {
        Response response = OrderQuerySupport.queryOrder(999);

        assertThat(response.statusCode()).isEqualTo(404);
        assertThat(response.jsonPath().getString("error")).isEqualTo("ORDER_NOT_FOUND");
    }

    @Test
    @Title("查询配置的外部订单")
    @Tag("api")
    @EnabledIfSystemProperty(named = "api.enabled", matches = "true")
    void shouldQueryConfiguredExternalOrder() {
        Response response = SerenityRest.given()
                .baseUri(settings.apiBaseUrl())
                .accept("application/json")
                .when()
                .get("/api/orders/{orderId}", settings.apiOrderId());

        assertThat(response.statusCode())
                .as("订单 API 响应状态码异常: %s", response.asPrettyString())
                .isEqualTo(200);
        assertThat(response.jsonPath().getLong("id"))
                .as("订单 API 返回了错误的订单")
                .isEqualTo(settings.apiOrderId());
    }

    private void assertExistingOrder(long orderId) {
        Response response = OrderQuerySupport.queryOrder(orderId);

        assertThat(response.statusCode()).isEqualTo(200);
        assertThat(response.jsonPath().getLong("id")).isEqualTo(orderId);
        assertThat(response.jsonPath().getString("status")).isEqualTo("PAID");
    }
}
