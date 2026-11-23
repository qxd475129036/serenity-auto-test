package com.example.autotest.config;

import org.h2.Driver;

import java.net.URISyntaxException;
import java.nio.file.Path;

public final class TestSettings {

    private final TestConfiguration configuration = TestConfiguration.shared();

    public Path projectDir() {
        return Path.of(System.getProperty("user.dir")).toAbsolutePath().normalize();
    }

    public String dbKind() {
        return required("db.kind");
    }

    public String dbUrl() {
        return configuration.required("db.url", "DB_URL or ORACLE_URL");
    }

    public String dbUser() {
        return configuration.required("db.user", "DB_USER or ORACLE_USER");
    }

    public String dbPassword() {
        return stringOr("db.password", "");
    }

    public boolean initializeDatabase() {
        return bool("db.init", false);
    }

    public String batchShellPath() {
        return required("batch.shell.path");
    }

    public Path batchLogDirectory() {
        return Path.of(required("batch.log.dir"))
                .toAbsolutePath()
                .normalize();
    }

    public Path batchLogFile(String fileName) {
        if (fileName == null || fileName.isBlank()
                || !Path.of(fileName).getFileName().toString().equals(fileName)) {
            throw new IllegalArgumentException("Invalid batch log file name: " + fileName);
        }
        return batchLogDirectory().resolve(fileName);
    }

    public String batchDate() {
        return required("batch.date");
    }

    public long batchTimeoutSeconds() {
        return number("batch.timeout.seconds", 600);
    }

    public boolean apiEnabled() {
        return bool("api.enabled", false);
    }

    public String apiBaseUrl() {
        return required("api.base.url");
    }

    public long apiOrderId() {
        return number("api.order.id", 1);
    }

    public String jdbcDriverJar() {
        String configured = string("jdbc.driver.jar");
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

    public String string(String key) {
        return configuration.string(key);
    }

    public String required(String key) {
        return configuration.required(key, environmentNameFor(key));
    }

    public boolean bool(String key, boolean defaultValue) {
        return configuration.bool(key, defaultValue);
    }

    public long number(String key, long defaultValue) {
        return configuration.number(key, defaultValue);
    }

    private String stringOr(String key, String defaultValue) {
        String configured = string(key);
        return configured == null ? defaultValue : configured;
    }

    private String environmentNameFor(String key) {
        return key.replace('.', '_').toUpperCase();
    }
}
