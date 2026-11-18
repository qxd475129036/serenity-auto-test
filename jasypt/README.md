# Jasypt 加解密工程

基于 JDK 25 + Spring Boot 3.5 + jasypt 的多模块示例，支持两种用法：

- **作为 jar 引用**：依赖 `jasypt-core` 后直接调用共通方法，不会引入或启动 Web 层。
- **独立启动**：运行 `jasypt-web`，通过 REST 接口或浏览器页面加解密。

## 环境要求

- **jasypt-core**：源码与字节码均按 Java 8 编译（`maven.compiler.release=8`），引用方使用 **JDK 8 及以上** 即可。
- **jasypt-web**：使用 **JDK 25**（`java.version=25`），构建和启动整个工程需要 JDK 25。
- 无需预装 Maven，项目已内置 Maven Wrapper（`./mvnw`）。

## 模块结构

| 模块 | 说明 | JDK 要求 |
| --- | --- | --- |
| `jasypt-core` | 纯 Java 核心库，仅依赖 jasypt，无 Spring/Web 依赖 | 编译目标 Java 8，运行需 JDK 8+ |
| `jasypt-web` | Spring Boot Web 应用，依赖 `jasypt-core`，提供 REST 接口与操作页面 | JDK 25 |

## 用法一：独立启动（页面 + REST）

> 与改造前相比：启动命令和 jar 路径有调整，访问地址与接口路径保持不变。

```bash
# 确认当前 java 为 25
java -version

# 打包（首次运行会自动下载 Maven）
./mvnw clean package

# 启动
./mvnw -pl jasypt-web -am spring-boot:run
```

如果本机默认 `java` 不是 25，可为 Maven 显式指定：

```bash
JAVA_HOME=/path/to/jdk-25 ./mvnw -pl jasypt-web -am spring-boot:run
```

也可以直接运行打好的 jar：

```bash
java -jar jasypt-web/target/jasypt-web-0.0.1-SNAPSHOT.jar
```

服务默认监听 `http://localhost:8080`。

## 浏览器操作页面

服务启动后直接访问：

```
http://localhost:8080/
```

页面包含加密区和解密区：输入文本与密钥即可调用对应接口，支持一键复制结果；空参数、密钥错误、密文无效、服务未启动等情况会在页面上给出明确提示。

## 接口说明

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/encrypt` | 输入明文和密钥，返回密文 |
| POST | `/api/decrypt` | 输入密文和密钥，返回明文 |

请求体：

```json
{
  "text": "要加密的明文或要解密的密文",
  "password": "你的密钥"
}
```

响应体（成功）：

```json
{
  "result": "结果"
}
```

响应体（失败，HTTP 400）：

```json
{
  "error": "错误原因"
}
```

## curl 示例

先加密：

```bash
curl -s -X POST http://localhost:8080/api/encrypt \
  -H "Content-Type: application/json" \
  -d '{"text":"hello jasypt","password":"my-secret-key"}'
```

返回示例（每次加密结果不同，因为随机盐和随机 IV）：

```json
{"result":"R2vL3k..."}
```

再解密（把上一步的 result 填入 text）：

```bash
curl -s -X POST http://localhost:8080/api/decrypt \
  -H "Content-Type: application/json" \
  -d '{"text":"上一步返回的密文","password":"my-secret-key"}'
```

返回：

```json
{"result":"hello jasypt"}
```

密钥错误或密文无效时返回 HTTP 400：

```json
{"error":"解密失败：密钥错误或密文无效"}
```

## 用法二：作为 jar 引用（不启动 Web）

### 1. 安装核心库到本地仓库

在工程根目录执行：

```bash
./mvnw -pl jasypt-core install
```

安装后的坐标为 `com.example:jasypt-core:0.0.1-SNAPSHOT`。

### 2. 在引用方 pom.xml 中添加依赖

```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>jasypt-core</artifactId>
    <version>0.0.1-SNAPSHOT</version>
</dependency>
```

`jasypt-core` 只传递 `org.jasypt:jasypt`，不会带入 Spring Boot、Web 容器或页面资源，引入后不会启动任何服务。

### 3. 调用共通方法

```java
import com.example.jasypt.core.JasyptCrypto;

public class Demo {
    public static void main(String[] args) {
        String password = "my-secret-key";

        String cipherText = JasyptCrypto.encrypt("hello jasypt", password);
        String plainText = JasyptCrypto.decrypt(cipherText, password);

        System.out.println(cipherText);
        System.out.println(plainText);
    }
}
```

密钥错误或密文无效时，`decrypt` 会抛出 `org.jasypt.exceptions.EncryptionOperationNotPossibleException`，可按业务需要捕获：

```java
try {
    String plainText = JasyptCrypto.decrypt(cipherText, password);
} catch (EncryptionOperationNotPossibleException e) {
    // 密钥错误或密文无效
}
```

注意：`jasypt-core` 以 Java 8 编译（`release=8`），引用方运行环境需为 JDK 8 及以上；调用时请传入非空密钥。

## 实现说明

- 共通方法：`jasypt-core` 中的 `com.example.jasypt.core.JasyptCrypto`；Web 层只做委托，不重复实现算法。
- 加密算法：`PBEWITHHMACSHA512ANDAES_256`
- 随机盐：`RandomSaltGenerator`
- 随机 IV：`RandomIvGenerator`
- 每次加密都会生成新的盐和 IV，因此同一明文每次得到的密文不同；解密时必须使用加密时的同一密钥。
