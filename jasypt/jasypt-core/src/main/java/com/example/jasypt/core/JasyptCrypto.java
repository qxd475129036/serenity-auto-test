package com.example.jasypt.core;

import org.jasypt.encryption.pbe.StandardPBEStringEncryptor;
import org.jasypt.exceptions.EncryptionOperationNotPossibleException;
import org.jasypt.iv.RandomIvGenerator;
import org.jasypt.salt.RandomSaltGenerator;

import java.util.ArrayList;
import java.util.List;

/**
 * jasypt 加解密共通方法。
 *
 * <p>该工具类不依赖 Spring，可被任意 Java 项目直接调用。每次加密都会使用随机盐和随机 IV，
 * 因此同一明文每次加密得到的密文不同；解密时必须使用加密时的同一密钥。</p>
 *
 * <p>密钥错误或密文无效时，{@link #decrypt(String, String)} 会抛出
 * {@link org.jasypt.exceptions.EncryptionOperationNotPossibleException}。</p>
 */
public final class JasyptCrypto {

    public static final String DEFAULT_ALGORITHM = "PBEWITHHMACSHA512ANDAES_256";

    private JasyptCrypto() {
    }

    /**
     * 加密。
     *
     * @param plainText 明文
     * @param password  密钥
     * @return 密文（Base64 字符串）
     */
    public static String encrypt(String plainText, String password) {
        if (plainText == null) {
            throw new IllegalArgumentException("plainText 不能为 null");
        }
        return newEncryptor(password).encrypt(plainText);
    }

    /**
     * 解密。
     *
     * @param cipherText 密文
     * @param password   加密时使用的密钥
     * @return 明文
     */
    public static String decrypt(String cipherText, String password) {
        if (cipherText == null) {
            throw new IllegalArgumentException("cipherText 不能为 null");
        }
        return newEncryptor(password).decrypt(cipherText);
    }

    /**
     * 批量加密。
     *
     * <p>返回结果的数量与顺序和输入完全一致。单条明文为 {@code null} 时仅该条标记失败，
     * 不影响其他条目；{@code password} 为空或 {@code plainTexts} 为 {@code null} 时整批抛出
     * {@link IllegalArgumentException}。</p>
     *
     * @param plainTexts 明文列表
     * @param password   密钥
     * @return 与输入一一对应的批量结果
     */
    public static List<BatchResult> encryptAll(List<String> plainTexts, String password) {
        if (plainTexts == null) {
            throw new IllegalArgumentException("plainTexts 不能为 null");
        }
        StandardPBEStringEncryptor encryptor = newEncryptor(password);
        List<BatchResult> results = new ArrayList<BatchResult>(plainTexts.size());
        for (int i = 0; i < plainTexts.size(); i++) {
            String plainText = plainTexts.get(i);
            if (plainText == null) {
                results.add(BatchResult.failure(i, "明文不能为 null"));
                continue;
            }
            try {
                results.add(BatchResult.success(i, encryptor.encrypt(plainText)));
            } catch (EncryptionOperationNotPossibleException e) {
                results.add(BatchResult.failure(i, "加密失败：" + e.getMessage()));
            }
        }
        return results;
    }

    /**
     * 批量解密。
     *
     * <p>返回结果的数量与顺序和输入完全一致。单条密文无效或为 {@code null} 时仅该条标记失败，
     * 不影响其他条目；{@code password} 为空或 {@code cipherTexts} 为 {@code null} 时整批抛出
     * {@link IllegalArgumentException}。</p>
     *
     * @param cipherTexts 密文列表
     * @param password    加密时使用的密钥
     * @return 与输入一一对应的批量结果
     */
    public static List<BatchResult> decryptAll(List<String> cipherTexts, String password) {
        if (cipherTexts == null) {
            throw new IllegalArgumentException("cipherTexts 不能为 null");
        }
        StandardPBEStringEncryptor encryptor = newEncryptor(password);
        List<BatchResult> results = new ArrayList<BatchResult>(cipherTexts.size());
        for (int i = 0; i < cipherTexts.size(); i++) {
            String cipherText = cipherTexts.get(i);
            if (cipherText == null) {
                results.add(BatchResult.failure(i, "密文不能为 null"));
                continue;
            }
            try {
                results.add(BatchResult.success(i, encryptor.decrypt(cipherText)));
            } catch (EncryptionOperationNotPossibleException e) {
                results.add(BatchResult.failure(i, "解密失败：密钥错误或密文无效"));
            }
        }
        return results;
    }

    private static StandardPBEStringEncryptor newEncryptor(String password) {
        if (password == null || password.trim().isEmpty()) {
            throw new IllegalArgumentException("password 不能为空");
        }
        StandardPBEStringEncryptor encryptor = new StandardPBEStringEncryptor();
        encryptor.setAlgorithm(DEFAULT_ALGORITHM);
        encryptor.setPassword(password);
        encryptor.setSaltGenerator(new RandomSaltGenerator());
        encryptor.setIvGenerator(new RandomIvGenerator());
        return encryptor;
    }
}
