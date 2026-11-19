package com.example.jasypt.dto;

/**
 * 密钥生成响应体。
 *
 * @param key 32 位安全随机密钥
 */
public record KeyResponse(String key) {
}
