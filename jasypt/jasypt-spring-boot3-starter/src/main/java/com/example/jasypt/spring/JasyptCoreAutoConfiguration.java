package com.example.jasypt.spring;

import org.jasypt.encryption.StringEncryptor;
import org.springframework.boot.autoconfigure.AutoConfiguration;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.context.annotation.Bean;
import org.springframework.core.env.Environment;

/**
 * 注册基于 core 的加密器，覆盖上游默认的 encryptor 构建方式。
 */
@AutoConfiguration(beforeName = "com.ulisesbocchio.jasyptspringbootstarter.JasyptSpringBootAutoConfiguration")
public class JasyptCoreAutoConfiguration {

    @Bean("jasyptStringEncryptor")
    @ConditionalOnMissingBean(name = "jasyptStringEncryptor")
    public StringEncryptor jasyptStringEncryptor(Environment environment) {
        return new CoreStringEncryptor(() -> environment.getProperty("jasypt.encryptor.password"));
    }
}
