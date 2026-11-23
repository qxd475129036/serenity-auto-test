package com.example.jasypt.service;

import com.example.jasypt.core.BatchResult;
import com.example.jasypt.core.JasyptCrypto;
import com.example.jasypt.core.SecureKeyGenerator;
import com.example.jasypt.dto.BatchItemResult;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class CryptoService {

    public String encrypt(String text, String password) {
        return JasyptCrypto.encrypt(text, password);
    }

    public String decrypt(String cipherText, String password) {
        return JasyptCrypto.decrypt(cipherText, password);
    }

    public List<BatchItemResult> encryptBatch(List<String> texts, String password) {
        return toItems(JasyptCrypto.encryptAll(texts, password));
    }

    public List<BatchItemResult> decryptBatch(List<String> texts, String password) {
        return toItems(JasyptCrypto.decryptAll(texts, password));
    }

    public String generateKey() {
        return SecureKeyGenerator.generate();
    }

    private static List<BatchItemResult> toItems(List<BatchResult> results) {
        List<BatchItemResult> items = new ArrayList<BatchItemResult>(results.size());
        for (BatchResult result : results) {
            items.add(new BatchItemResult(
                    result.getIndex(), result.isSuccess(), result.getValue(), result.getError()));
        }
        return items;
    }
}
