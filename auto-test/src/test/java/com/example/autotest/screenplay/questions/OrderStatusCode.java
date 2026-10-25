package com.example.autotest.screenplay.questions;

import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.Question;

public class OrderStatusCode implements Question<Integer> {

    public static OrderStatusCode value() {
        return new OrderStatusCode();
    }

    @Override
    public Integer answeredBy(Actor actor) {
        return actor.recall("httpStatus");
    }
}
