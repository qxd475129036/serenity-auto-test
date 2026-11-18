package com.example.autodecrypt.boot2;

import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 普通属性注入，无需任何 jasypt 相关代码或注解。
 */
@RestController
public class SecretController {

    @Value("${demo.secret}")
    private String secret;

    @GetMapping("/secret")
    public Map<String, String> secret() {
        return Map.of("secret", secret);
    }
}
