package com.example.jasypt.core;

import org.jasypt.encryption.pbe.StandardPBEStringEncryptor;
import org.jasypt.iv.RandomIvGenerator;
import org.jasypt.salt.RandomSaltGenerator;

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
