# Jasypt 加解密 REST 服务

基于 Spring Boot 3.5 + jasypt 的加解密示例，密钥由请求传入，不写在配置文件中。

## 环境要求

- **JDK 25**（编译与运行均以 JDK 25 为准，`pom.xml` 中 `java.version=25`）
- 无需预装 Maven，项目已内置 Maven Wrapper（`./mvnw`）

## 启动

```bash
# 确认当前 java 为 25
java -version

# 打包（首次运行会自动下载 Maven）
./mvnw clean package

# 启动
./mvnw spring-boot:run
```

如果本机默认 `java` 不是 25，可为 Maven 显式指定：

```bash
JAVA_HOME=/path/to/jdk-25 ./mvnw spring-boot:run
```

也可以直接运行打好的 jar：

```bash
java -jar target/jasypt-0.0.1-SNAPSHOT.jar
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

## 实现说明

- 加密算法：`PBEWITHHMACSHA512ANDAES_256`
- 随机盐：`RandomSaltGenerator`
- 随机 IV：`RandomIvGenerator`
- 每次加密都会生成新的盐和 IV，因此同一明文每次得到的密文不同；解密时必须使用加密时的同一密钥。
