package com.example.jasypt.core;

import java.security.SecureRandom;

/**
 * 基于 {@link SecureRandom} 的安全随机密钥生成器。
 *
 * <p>仅使用 Java 8 API，不依赖 Spring，可同时供 Web 层和其他引用方复用。</p>
 */
public final class SecureKeyGenerator {

    /** 生成的密钥长度（字符数）。 */
    public static final int KEY_LENGTH = 32;

    private static final char[] ALPHABET =
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789".toCharArray();

    /** 拒绝采样上限，保证每个字符等概率，避免取模偏差。 */
    private static final int MAX_VALID_BYTE = 256 - (256 % ALPHABET.length);

    private static final SecureRandom SECURE_RANDOM = new SecureRandom();

    private SecureKeyGenerator() {
    }

    /**
     * 生成 32 位、仅包含字母和数字的安全随机密钥。
     *
     * @return 长度为 {@value #KEY_LENGTH} 的随机密钥
     */
    public static String generate() {
        char[] key = new char[KEY_LENGTH];
        byte[] buffer = new byte[KEY_LENGTH * 2];
        int index = 0;
        while (index < KEY_LENGTH) {
            SECURE_RANDOM.nextBytes(buffer);
            for (byte value : buffer) {
                int unsigned = value & 0xFF;
                if (unsigned < MAX_VALID_BYTE) {
                    key[index++] = ALPHABET[unsigned % ALPHABET.length];
                    if (index == KEY_LENGTH) {
                        break;
                    }
                }
            }
        }
        return new String(key);
    }
}
