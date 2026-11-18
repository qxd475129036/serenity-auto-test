package com.example.jasypt.controller;

import com.example.jasypt.dto.CryptoRequest;
import com.example.jasypt.dto.CryptoResponse;
import com.example.jasypt.service.CryptoService;
import org.jasypt.exceptions.EncryptionOperationNotPossibleException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api")
public class CryptoController {

    private final CryptoService cryptoService;

    public CryptoController(CryptoService cryptoService) {
        this.cryptoService = cryptoService;
    }

    @PostMapping("/encrypt")
    public ResponseEntity<?> encrypt(@RequestBody CryptoRequest request) {
        if (isBlank(request.text()) || isBlank(request.password())) {
            return ResponseEntity.badRequest().body(Map.of("error", "text 和 password 不能为空"));
        }
        return ResponseEntity.ok(new CryptoResponse(cryptoService.encrypt(request.text(), request.password())));
    }

    @PostMapping("/decrypt")
    public ResponseEntity<?> decrypt(@RequestBody CryptoRequest request) {
        if (isBlank(request.text()) || isBlank(request.password())) {
            return ResponseEntity.badRequest().body(Map.of("error", "text 和 password 不能为空"));
        }
        try {
            return ResponseEntity.ok(new CryptoResponse(cryptoService.decrypt(request.text(), request.password())));
        } catch (EncryptionOperationNotPossibleException e) {
            return ResponseEntity.badRequest().body(Map.of("error", "解密失败：密钥错误或密文无效"));
        }
    }

    private boolean isBlank(String value) {
        return value == null || value.isBlank();
    }
}
