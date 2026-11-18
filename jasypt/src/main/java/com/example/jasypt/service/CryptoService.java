package com.example.jasypt.service;

import org.jasypt.encryption.pbe.StandardPBEStringEncryptor;
import org.jasypt.iv.RandomIvGenerator;
import org.jasypt.salt.RandomSaltGenerator;
import org.springframework.stereotype.Service;

@Service
public class CryptoService {

    private static final String ALGORITHM = "PBEWITHHMACSHA512ANDAES_256";

    public String encrypt(String text, String password) {
        return newEncryptor(password).encrypt(text);
    }

    public String decrypt(String cipherText, String password) {
        return newEncryptor(password).decrypt(cipherText);
    }

    private StandardPBEStringEncryptor newEncryptor(String password) {
        StandardPBEStringEncryptor encryptor = new StandardPBEStringEncryptor();
        encryptor.setAlgorithm(ALGORITHM);
        encryptor.setPassword(password);
        encryptor.setSaltGenerator(new RandomSaltGenerator());
        encryptor.setIvGenerator(new RandomIvGenerator());
        return encryptor;
    }
}
