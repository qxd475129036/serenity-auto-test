package com.example.autotest.screenplay.tasks;

import io.restassured.response.Response;
import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.Task;
import net.serenitybdd.screenplay.rest.interactions.Get;
import net.serenitybdd.screenplay.rest.questions.LastResponse;

public class QueryOrder implements Task {

    private final long orderId;

    private QueryOrder(long orderId) {
        this.orderId = orderId;
    }

    public static QueryOrder withId(long orderId) {
        return new QueryOrder(orderId);
    }

    @Override
    public <T extends Actor> void performAs(T actor) {
        actor.attemptsTo(
                Get.resource("/api/orders/{orderId}")
                        .with(request -> request.pathParam("orderId", orderId))
        );
        Response response = LastResponse.received().answeredBy(actor);
        actor.remember("httpStatus", response.statusCode());
        actor.remember("orderStatus", response.jsonPath().getString("status"));
    }

    @Override
    public String toString() {
        return "查询订单 " + orderId;
    }
}
