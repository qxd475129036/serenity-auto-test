package com.example.autotest.screenplay.questions;

import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.Question;

public class OrderStatus implements Question<String> {

    public static OrderStatus value() {
        return new OrderStatus();
    }

    @Override
    public String answeredBy(Actor actor) {
        return actor.recall("orderStatus");
    }
}
