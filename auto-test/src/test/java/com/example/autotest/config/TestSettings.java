package com.example.autotest.config;

import org.h2.Driver;

import java.net.URISyntaxException;
import java.nio.file.Path;

public final class TestSettings {

    public Path projectDir() {
        return Path.of(System.getProperty("user.dir")).toAbsolutePath().normalize();
    }

    public String dbKind() {
        return value("db.kind", "DB_KIND", "h2");
    }

    public String dbUrl() {
        String configured = firstNonBlank(
                property("db.url"),
                property("oracle.url"),
                environment("DB_URL"),
                environment("ORACLE_URL"));
        if (configured != null) {
            return configured;
        }
        if ("h2".equalsIgnoreCase(dbKind())) {
            return "jdbc:h2:file:"
                    + projectDir().resolve("target/test-db/reconciliation")
                    + ";MODE=Oracle;DATABASE_TO_UPPER=TRUE";
        }
        return required("db.url", "DB_URL or ORACLE_URL");
    }

    public String dbUser() {
        String configured = firstNonBlank(
                property("db.user"),
                property("oracle.user"),
                environment("DB_USER"),
                environment("ORACLE_USER"));
        return configured == null ? "sa" : configured;
    }

    public String dbPassword() {
        String configured = firstNonBlank(
                property("db.password"),
                property("oracle.password"),
                environment("DB_PASSWORD"),
                environment("ORACLE_PASSWORD"));
        return configured == null ? "" : configured;
    }

    public boolean initializeDatabase() {
        return Boolean.parseBoolean(value("db.init", "DB_INIT", "false"));
    }

    public String batchShellPath() {
        return required("batch.shell.path", "BATCH_SHELL_PATH");
    }

    public Path batchLogFile() {
        return Path.of(required("batch.log.dir", "BATCH_LOG_DIR"))
                .toAbsolutePath()
                .resolve("reconciliation.log");
    }

    public String batchDate() {
        return value("batch.date", "BATCH_DATE", "2026-10-31");
    }

    public long batchTimeoutSeconds() {
        return Long.parseLong(value("batch.timeout.seconds", "BATCH_TIMEOUT_SECONDS", "600"));
    }

    public boolean apiEnabled() {
        return Boolean.parseBoolean(value("api.enabled", "API_ENABLED", "false"));
    }

    public String apiBaseUrl() {
        return value("api.base.url", "API_BASE_URL", "http://localhost:8080");
    }

    public long apiOrderId() {
        return Long.parseLong(value("api.order.id", "API_ORDER_ID", "1"));
    }

    public String jdbcDriverJar() {
        String configured = property("jdbc.driver.jar");
        if (configured != null) {
            return configured;
        }
        try {
            return Path.of(Driver.class.getProtectionDomain().getCodeSource().getLocation().toURI())
                    .toString();
        } catch (URISyntaxException exception) {
            throw new IllegalStateException("Cannot resolve the H2 JDBC driver", exception);
        }
    }

    private String value(String propertyName, String environmentName, String defaultValue) {
        String configured = firstNonBlank(
                property(propertyName),
                environment(environmentName));
        return configured == null ? defaultValue : configured;
    }

    private String required(String propertyName, String hint) {
        String configured = firstNonBlank(
                property(propertyName),
                environment(environmentNameFor(propertyName)));
        if (configured == null) {
            throw new IllegalStateException(
                    "Missing configuration '" + propertyName + "'. Provide -D" + propertyName
                            + "=<value> or environment " + hint);
        }
        return configured;
    }

    private String environmentNameFor(String propertyName) {
        return propertyName.replace('.', '_').toUpperCase();
    }

    private String property(String name) {
        return usable(System.getProperty(name));
    }

    private String environment(String name) {
        return usable(System.getenv(name));
    }

    private String usable(String value) {
        if (value == null || value.isBlank() || value.startsWith("${")) {
            return null;
        }
        return value;
    }

    private String firstNonBlank(String... values) {
        for (String value : values) {
            if (value != null && !value.isBlank()) {
                return value;
            }
        }
        return null;
    }
}
