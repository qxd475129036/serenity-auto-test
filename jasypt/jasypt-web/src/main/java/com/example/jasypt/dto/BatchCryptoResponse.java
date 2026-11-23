package com.example.jasypt.dto;

import java.util.List;

/**
 * 批量加解密响应体。
 *
 * @param results 与请求 texts 顺序、数量一一对应的结果列表
 */
public record BatchCryptoResponse(List<BatchItemResult> results) {
}
