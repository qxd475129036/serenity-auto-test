package com.example.jasypt.spring;

import com.example.jasypt.core.JasyptCrypto;

import java.util.function.Supplier;

import org.jasypt.encryption.StringEncryptor;

/**
 * 把 jasypt-spring-boot 的解密调用委托给 core，保证算法、盐、IV 只有一份实现。
 */
public class CoreStringEncryptor implements StringEncryptor {

    private final Supplier<String> passwordSupplier;

    public CoreStringEncryptor(Supplier<String> passwordSupplier) {
        this.passwordSupplier = passwordSupplier;
    }

    @Override
    public String encrypt(String message) {
        return JasyptCrypto.encrypt(message, password());
    }

    @Override
    public String decrypt(String encryptedMessage) {
        return JasyptCrypto.decrypt(encryptedMessage, password());
    }

    private String password() {
        String password = passwordSupplier.get();
        if (password == null || password.trim().isEmpty()) {
            throw new IllegalStateException(
                    "缺少 jasypt.encryptor.password，请通过 JASYPT_ENCRYPTOR_PASSWORD 环境变量"
                            + " 或 --jasypt.encryptor.password 启动参数提供密钥");
        }
        return password;
    }
}
