package com.example.jasypt.dto;

import java.util.List;

/**
 * 批量加解密请求体。
 *
 * @param texts    加密时为明文列表，解密时为密文列表，每项对应一条结果
 * @param password 用于加解密的密钥，由请求传入
 */
public record BatchCryptoRequest(List<String> texts, String password) {
}
