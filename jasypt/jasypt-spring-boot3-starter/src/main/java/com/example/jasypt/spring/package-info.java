/**
 * Spring Boot 3.5 自动解密 starter 模块。
 *
 * <p>本模块传递 {@code com.github.ulisesbocchio:jasypt-spring-boot-starter} 提供属性源解密能力，
 * 并注册一个名为 {@code jasyptStringEncryptor} 的加密器，把实际加解密委托给
 * {@link com.example.jasypt.core.JasyptCrypto}。算法、盐、IV 固定为 core 的默认值，
 * 使用方无需配置，core 生成的 {@code ENC(...)} 密文可被直接解开。</p>
 *
 * <p>密钥通过 {@code jasypt.encryptor.password} 提供，可由环境变量
 * {@code JASYPT_ENCRYPTOR_PASSWORD} 或启动参数传入。</p>
 */
package com.example.jasypt.spring;
