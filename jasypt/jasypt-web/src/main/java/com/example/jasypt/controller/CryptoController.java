package com.example.jasypt.controller;

import com.example.jasypt.dto.BatchCryptoRequest;
import com.example.jasypt.dto.BatchCryptoResponse;
import com.example.jasypt.dto.CryptoRequest;
import com.example.jasypt.dto.CryptoResponse;
import com.example.jasypt.dto.KeyResponse;
import com.example.jasypt.service.CryptoService;
import org.jasypt.exceptions.EncryptionOperationNotPossibleException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
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

    @GetMapping("/key")
    public ResponseEntity<KeyResponse> generateKey() {
        return ResponseEntity.ok()
                .header("Cache-Control", "no-store")
                .body(new KeyResponse(cryptoService.generateKey()));
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

    @PostMapping("/encrypt/batch")
    public ResponseEntity<?> encryptBatch(@RequestBody BatchCryptoRequest request) {
        ResponseEntity<?> invalid = validateBatch(request);
        if (invalid != null) {
            return invalid;
        }
        return ResponseEntity.ok(
                new BatchCryptoResponse(cryptoService.encryptBatch(request.texts(), request.password())));
    }

    @PostMapping("/decrypt/batch")
    public ResponseEntity<?> decryptBatch(@RequestBody BatchCryptoRequest request) {
        ResponseEntity<?> invalid = validateBatch(request);
        if (invalid != null) {
            return invalid;
        }
        return ResponseEntity.ok(
                new BatchCryptoResponse(cryptoService.decryptBatch(request.texts(), request.password())));
    }

    /**
     * 批量接口的公共参数校验：单条内容的失败原因由结果列表逐条返回，这里只校验整批参数。
     */
    private ResponseEntity<?> validateBatch(BatchCryptoRequest request) {
        if (request == null || request.texts() == null || request.texts().isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("error", "texts 不能为空"));
        }
        if (isBlank(request.password())) {
            return ResponseEntity.badRequest().body(Map.of("error", "password 不能为空"));
        }
        return null;
    }

    private boolean isBlank(String value) {
        return value == null || value.isBlank();
    }
}
