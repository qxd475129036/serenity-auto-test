package com.example.jasypt.dto;

/**
 * 批量加解密中单条结果的响应体。
 *
 * @param index   对应请求 texts 中的下标
 * @param success 是否处理成功
 * @param result  成功时的结果，失败时为 null
 * @param error   失败原因，成功时为 null
 */
public record BatchItemResult(int index, boolean success, String result, String error) {
}
