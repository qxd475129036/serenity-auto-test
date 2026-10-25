package com.example.autotest.order;

import io.restassured.response.Response;
import net.serenitybdd.annotations.Epic;
import net.serenitybdd.annotations.Feature;
import net.serenitybdd.annotations.Story;
import net.serenitybdd.annotations.Title;
import net.serenitybdd.core.Serenity;
import net.serenitybdd.junit5.SerenityJUnit5Extension;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.api.parallel.Execution;
import org.junit.jupiter.api.parallel.ExecutionMode;

import static org.assertj.core.api.Assertions.assertThat;

@ExtendWith(SerenityJUnit5Extension.class)
@Epic("订单服务")
@Feature("订单查询")
@Story("并行查询订单")
@Tag("demo")
class OrderParallelStoryTest {

    @Test
    @Title("并行查询订单 1")
    @Tag("parallel")
    @Execution(ExecutionMode.CONCURRENT)
    void shouldQueryOrderOneInParallel() {
        queryOrderInParallel(1);
    }

    @Test
    @Title("并行查询订单 2")
    @Tag("parallel")
    @Execution(ExecutionMode.CONCURRENT)
    void shouldQueryOrderTwoInParallel() {
        queryOrderInParallel(2);
    }

    @Test
    @Title("并行查询订单 3")
    @Tag("parallel")
    @Execution(ExecutionMode.CONCURRENT)
    void shouldQueryOrderThreeInParallel() {
        queryOrderInParallel(3);
    }

    @Test
    @Title("并行查询订单 4")
    @Tag("parallel")
    @Execution(ExecutionMode.CONCURRENT)
    void shouldQueryOrderFourInParallel() {
        queryOrderInParallel(4);
    }

    private void queryOrderInParallel(long orderId) {
        Response response = OrderQuerySupport.queryOrder(orderId);

        assertThat(response.statusCode()).isEqualTo(200);
        assertThat(response.jsonPath().getLong("id")).isEqualTo(orderId);
        Serenity.recordReportData()
                .withTitle("执行线程")
                .andContents(Thread.currentThread().getName());
    }
}
