package com.example.jasypt.dto;

/**
 * 加解密请求体。
 *
 * @param text     加密时为明文，解密时为密文
 * @param password 用于加解密的密钥，由请求传入
 */
public record CryptoRequest(String text, String password) {
}
