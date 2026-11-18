package com.example.jasypt.dto;

/**
 * 加解密响应体。
 *
 * @param result 加密时为密文，解密时为明文
 */
public record CryptoResponse(String result) {
}
