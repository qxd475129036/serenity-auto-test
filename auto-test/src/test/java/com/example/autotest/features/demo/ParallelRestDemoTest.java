package com.example.autotest.features.demo;

import com.example.autotest.support.LocalOrderApi;
import io.restassured.response.Response;
import net.serenitybdd.annotations.Epic;
import net.serenitybdd.annotations.Feature;
import net.serenitybdd.annotations.Story;
import net.serenitybdd.annotations.Title;
import net.serenitybdd.core.Serenity;
import net.serenitybdd.junit5.SerenityJUnit5Extension;
import net.serenitybdd.rest.SerenityRest;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.api.parallel.Execution;
import org.junit.jupiter.api.parallel.ExecutionMode;

import static org.assertj.core.api.Assertions.assertThat;

@ExtendWith(SerenityJUnit5Extension.class)
@Epic("订单服务")
@Feature("按订单号查询")
@Story("查询已存在订单")
@Execution(ExecutionMode.CONCURRENT)
@Tag("demo")
@Tag("parallel")
class ParallelRestDemoTest {

    @Test
    @Title("并行场景 1：查询订单 1")
    void should_query_order_1() {
        assertOrder(1);
    }

    @Test
    @Title("并行场景 2：查询订单 2")
    void should_query_order_2() {
        assertOrder(2);
    }

    @Test
    @Title("并行场景 3：查询订单 3")
    void should_query_order_3() {
        assertOrder(3);
    }

    @Test
    @Title("并行场景 4：查询订单 4")
    void should_query_order_4() {
        assertOrder(4);
    }

    private void assertOrder(long orderId) {
        Response response = SerenityRest.given()
                .baseUri(LocalOrderApi.shared().baseUrl())
                .accept("application/json")
                .get("/api/orders/{orderId}", orderId);

        assertThat(response.statusCode()).isEqualTo(200);
        assertThat(response.jsonPath().getLong("id")).isEqualTo(orderId);

        Serenity.recordReportData()
                .withTitle("执行线程")
                .andContents(Thread.currentThread().getName());
    }
}
