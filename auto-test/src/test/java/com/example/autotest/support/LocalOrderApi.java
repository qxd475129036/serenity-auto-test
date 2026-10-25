package com.example.autotest.support;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Lightweight, thread-safe order API used by the Serenity feature demos.
 */
public final class LocalOrderApi {

    private static final String ORDERS_PATH = "/api/orders/";

    private static LocalOrderApi shared;

    private final HttpServer server;
    private final ExecutorService executor;
    private final AtomicBoolean stopped = new AtomicBoolean(false);

    private LocalOrderApi(HttpServer server, ExecutorService executor) {
        this.server = server;
        this.executor = executor;
    }

    public static synchronized LocalOrderApi shared() {
        if (shared == null) {
            try {
                shared = start();
            } catch (IOException exception) {
                throw new IllegalStateException("Cannot start the local order API", exception);
            }
            Runtime.getRuntime().addShutdownHook(new Thread(shared::stop));
        }
        return shared;
    }

    public String baseUrl() {
        return "http://127.0.0.1:" + server.getAddress().getPort();
    }

    public void stop() {
        if (stopped.compareAndSet(false, true)) {
            server.stop(0);
            executor.shutdownNow();
        }
    }

    private static LocalOrderApi start() throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        ExecutorService executor = Executors.newFixedThreadPool(2, runnable -> {
            Thread thread = new Thread(runnable, "local-order-api");
            thread.setDaemon(true);
            return thread;
        });
        server.setExecutor(executor);
        server.createContext(ORDERS_PATH, LocalOrderApi::handleOrder);
        server.start();
        return new LocalOrderApi(server, executor);
    }

    private static void handleOrder(HttpExchange exchange) throws IOException {
        try (exchange) {
            if (!"GET".equalsIgnoreCase(exchange.getRequestMethod())) {
                respond(exchange, 405, "{\"error\":\"METHOD_NOT_ALLOWED\"}");
                return;
            }

            String path = exchange.getRequestURI().getPath();
            String orderId = path.substring(ORDERS_PATH.length());
            if (orderId.matches("[1-4]")) {
                respond(exchange, 200,
                        "{\"id\":" + orderId + ",\"status\":\"PAID\",\"amount\":100.00}");
            } else {
                respond(exchange, 404, "{\"error\":\"ORDER_NOT_FOUND\"}");
            }
        }
    }

    private static void respond(HttpExchange exchange, int status, String body) throws IOException {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().add("Content-Type", "application/json; charset=utf-8");
        exchange.sendResponseHeaders(status, bytes.length);
        try (OutputStream output = exchange.getResponseBody()) {
            output.write(bytes);
        }
    }
}
