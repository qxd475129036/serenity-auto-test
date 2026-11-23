package com.example.autotest.config;

import org.springframework.core.env.MutablePropertySources;
import org.springframework.core.env.PropertiesPropertySource;
import org.springframework.core.env.StandardEnvironment;
import org.springframework.core.io.ClassPathResource;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Properties;

/**
 * 集中配置加载器：classpath 上的 application.properties 提供默认值，
 * application-{env}.properties 提供环境覆盖；系统属性与环境变量优先级更高。
 */
final class TestConfiguration {

    private static final String DEFAULT_ENVIRONMENT = "local";
    private static final TestConfiguration SHARED = new TestConfiguration();

    private final StandardEnvironment environment = new StandardEnvironment();

    private TestConfiguration() {
        String environmentName = firstNonBlank(
                System.getProperty("test.env"),
                System.getenv("TEST_ENV"),
                DEFAULT_ENVIRONMENT);
        MutablePropertySources sources = environment.getPropertySources();
        // 系统属性与环境变量已由 StandardEnvironment 预置在最前，
        // 这里按优先级从高到低追加环境覆盖和基础默认值。
        addClasspath(sources, "application-" + environmentName + ".properties");
        addClasspath(sources, "application.properties");
    }

    static TestConfiguration shared() {
        return SHARED;
    }

    String string(String key) {
        try {
            return usable(environment.getProperty(key));
        } catch (IllegalArgumentException exception) {
            throw new IllegalStateException(
                    "配置项 '" + key + "' 的占位符无法解析: " + exception.getMessage(), exception);
        }
    }

    String required(String key, String hint) {
        String configured = string(key);
        if (configured == null) {
            throw new IllegalStateException(
                    "Missing configuration '" + key + "'. Provide -D" + key
                            + "=<value> or environment " + hint);
        }
        return configured;
    }

    boolean bool(String key, boolean defaultValue) {
        String configured = string(key);
        return configured == null ? defaultValue : Boolean.parseBoolean(configured);
    }

    long number(String key, long defaultValue) {
        String configured = string(key);
        if (configured == null) {
            return defaultValue;
        }
        try {
            return Long.parseLong(configured);
        } catch (NumberFormatException exception) {
            throw new IllegalStateException(
                    "配置项 '" + key + "' 不是合法的整数: " + configured, exception);
        }
    }

    private void addClasspath(MutablePropertySources sources, String location) {
        ClassPathResource resource = new ClassPathResource(location);
        if (!resource.exists()) {
            return;
        }
        Properties properties = new Properties();
        try (InputStream input = resource.getInputStream()) {
            properties.load(new InputStreamReader(input, StandardCharsets.UTF_8));
        } catch (IOException exception) {
            throw new IllegalStateException("无法加载配置文件 " + location, exception);
        }
        sources.addLast(new PropertiesPropertySource(location, properties));
    }

    private static String firstNonBlank(String... values) {
        for (String value : values) {
            String usable = usable(value);
            if (usable != null) {
                return usable;
            }
        }
        return null;
    }

    private static String usable(String value) {
        if (value == null || value.isBlank() || value.startsWith("${")) {
            return null;
        }
        return value;
    }
}
