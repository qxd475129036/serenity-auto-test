package com.example.jasypt.service;

import com.example.jasypt.core.JasyptCrypto;
import com.example.jasypt.core.SecureKeyGenerator;
import org.springframework.stereotype.Service;

@Service
public class CryptoService {

    public String encrypt(String text, String password) {
        return JasyptCrypto.encrypt(text, password);
    }

    public String decrypt(String cipherText, String password) {
        return JasyptCrypto.decrypt(cipherText, password);
    }

    public String generateKey() {
        return SecureKeyGenerator.generate();
    }
}
