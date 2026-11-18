# Jasypt 加解密工程

基于 JDK 25 + Spring Boot 3.5 + jasypt 的多模块示例，支持三种用法：

- **作为 jar 引用**：依赖 `jasypt-core` 后直接调用共通方法，不会引入或启动 Web 层。
- **独立启动**：运行 `jasypt-web`，通过 REST 接口或浏览器页面加解密。
- **Spring Boot 自动解密**：按 Boot 大版本选择 starter，配置中的 `ENC(...)` 在启动时自动解密。

## 环境要求

- **jasypt-core**：源码与字节码均按 Java 8 编译（`maven.compiler.release=8`），引用方使用 **JDK 8 及以上** 即可。
- **jasypt-web**：使用 **JDK 25**（`java.version=25`），构建和启动整个工程需要 JDK 25。
- **jasypt-spring-boot3-starter**：**JDK 21 及以上**，编译与运行目标均为 Java 21，适用于 Spring Boot 3.5。
- **jasypt-spring-boot2-starter**：字节码兼容 **Java 8**，适用于 Spring Boot 2.7。
- 无需预装 Maven，项目已内置 Maven Wrapper（`./mvnw`）。

## 模块结构

| 模块 | 说明 | JDK / Boot 要求 |
| --- | --- | --- |
| `jasypt-core` | 纯 Java 核心库，仅依赖 jasypt，无 Spring/Web 依赖 | Java 8+ |
| `jasypt-web` | Spring Boot Web 应用，依赖 `jasypt-core`，提供 REST 接口与操作页面 | JDK 25 |
| `jasypt-spring-boot3-starter` | 封装 `ulisesbocchio/jasypt-spring-boot-starter:4.0.4`，加密器委托 core | JDK 21+ / Boot 3.5 |
| `jasypt-spring-boot2-starter` | 封装 `ulisesbocchio/jasypt-spring-boot-starter:3.0.5`，加密器委托 core | Java 8+ / Boot 2.7 |

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

## 用法三：Spring Boot 自动解密 `ENC(...)`

### 跨 Boot 版本的结论与取舍

上游 `ulisesbocchio/jasypt-spring-boot` 分为两条线：3.0.5 面向 Spring Boot 2.7 / Java 8，4.0.4 面向 Spring Boot 3.5 / Java 17。两者在 Boot 基线和依赖上不同，无法用同一个上游版本可靠覆盖两个 Boot 大版本。

因此本工程提供两个 starter：

| Boot 版本 | 使用模块 | 坐标 |
| --- | --- | --- |
| Spring Boot 3.5 | `jasypt-spring-boot3-starter` | `com.example:jasypt-spring-boot3-starter:0.0.1-SNAPSHOT` |
| Spring Boot 2.7 | `jasypt-spring-boot2-starter` | `com.example:jasypt-spring-boot2-starter:0.0.1-SNAPSHOT` |

两个 starter 都注册同一个委托实现：把 jasypt-spring-boot 的解密调用转交给 `jasypt-core` 的 `JasyptCrypto`。因此算法、盐、IV 只有 core 一份实现，core 或页面生成的 `ENC(...)` 密文一定能被 starter 解开。使用方不需要配置算法、盐、IV，只需提供密钥。

### 1. 安装 starter 到本地仓库

```bash
# 安装全部模块（推荐）
./mvnw install

# 或只安装某个 Boot 版本的 starter（会自动带上 core）
./mvnw -pl jasypt-spring-boot3-starter -am install
./mvnw -pl jasypt-spring-boot2-starter -am install
```

### 2. 在第三方工程中添加对应依赖

Spring Boot 3.5：

```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>jasypt-spring-boot3-starter</artifactId>
    <version>0.0.1-SNAPSHOT</version>
</dependency>
```

Spring Boot 2.7：

```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>jasypt-spring-boot2-starter</artifactId>
    <version>0.0.1-SNAPSHOT</version>
</dependency>
```

只能按 Boot 版本二选一，不要同时引入两个 starter。两个 starter 都已传递上游依赖，**不要再重复添加** `com.github.ulisesbocchio:jasypt-spring-boot-starter`。

### 3. 在配置中写 ENC 密文

`application.yml`：

```yaml
demo:
  secret: "ENC(密文)"
```

或 `application.properties`：

```properties
demo.secret=ENC(密文)
```

业务代码保持普通写法即可，例如：

```java
@Value("${demo.secret}")
private String secret;
```

### 4. 启动阶段提供密钥

密钥使用约定属性 `jasypt.encryptor.password`，任选一种方式传入，不要写进配置文件：

```bash
# 环境变量
JASYPT_ENCRYPTOR_PASSWORD=my-secret-key java -jar app.jar

# 启动参数
java -jar app.jar --jasypt.encryptor.password=my-secret-key

# JVM 系统属性
java -Djasypt.encryptor.password=my-secret-key -jar app.jar
```

缺少密钥且存在需要解密的属性时，应用会启动失败并明确提示需要 `jasypt.encryptor.password`，不会把 `ENC(...)` 当明文使用。

### 5. 内置的算法默认值

两个 starter 都固定使用 core 的实现，无需也不建议再配置以下属性：

- 算法：`PBEWITHHMACSHA512ANDAES_256`
- 盐生成器：`RandomSaltGenerator`
- IV 生成器：`RandomIvGenerator`
- 输出编码：Base64

由于加解密完全委托 core，`jasypt.encryptor.algorithm`、`jasypt.encryptor.salt-generator-classname`、`jasypt.encryptor.iv-generator-classname` 等配置不会改变实际算法。验证时故意传入无效算法值仍能正常解密，可确认使用的是 core 加密器。

### 6. 生成 `ENC(...)` 密文

可用本工程的操作页面，或直接调用接口。启动时使用的密钥必须与生成密文时一致：

```bash
curl -s -X POST http://localhost:8080/api/encrypt \
  -H "Content-Type: application/json" \
  -d '{"text":"demo-secret-value","password":"demo-secret-key"}'
```

返回：

```json
{"result":"LcX9FokeFRJxxbiJi0nz47ioGIXywm2Zol7suf/vmVMQPzdHkDnMidsgvQwSkJLxvFSk3ZLRGugamnVYSM1hCg=="}
```

把 `result` 填入配置：

```yaml
demo:
  secret: "ENC(LcX9FokeFRJxxbiJi0nz47ioGIXywm2Zol7suf/vmVMQPzdHkDnMidsgvQwSkJLxvFSk3ZLRGugamnVYSM1hCg==)"
```

### 7. 完整第三方示例

两个示例都是普通 Spring Boot 工程，只声明对应 starter 一个 jasypt 依赖，用 `@Value` 读取配置，不包含任何 jasypt 代码。

Spring Boot 3.5（端口 8082，示例使用 JDK 21 构建和运行）：

```bash
JAVA_HOME=/path/to/jdk-21 \
  ./mvnw -f examples/jasypt-auto-decrypt-demo/pom.xml clean package

JASYPT_ENCRYPTOR_PASSWORD=demo-secret-key \
  /path/to/jdk-21/bin/java -jar examples/jasypt-auto-decrypt-demo/target/jasypt-auto-decrypt-demo-1.0.0.jar

curl http://localhost:8082/secret
```

Spring Boot 2.7（端口 8083，示例使用 JDK 17 构建和运行）：

```bash
JAVA_HOME=/path/to/jdk-17 \
  ./mvnw -f examples/jasypt-auto-decrypt-demo-boot2/pom.xml clean package

JASYPT_ENCRYPTOR_PASSWORD=demo-secret-key \
  /path/to/jdk-17/bin/java -jar examples/jasypt-auto-decrypt-demo-boot2/target/jasypt-auto-decrypt-demo-boot2-1.0.0.jar

curl http://localhost:8083/secret
```

两个示例都返回：

```json
{"secret":"demo-secret-value"}
```

### 8. 验证结果

| 场景 | 版本 | 结果 |
| --- | --- | --- |
| Boot 3 + 环境变量密钥 | Spring Boot 3.5.16 / JDK 21 | 解密成功，返回 `demo-secret-value` |
| Boot 3 + 启动参数密钥 | Spring Boot 3.5.16 / JDK 21 | 解密成功 |
| Boot 3 + 无效算法配置 | Spring Boot 3.5.16 / JDK 21 | 仍解密成功，日志为 `Found Custom Encryptor Bean com.example.jasypt.spring.CoreStringEncryptor` |
| Boot 3 starter 字节码 | Java 21 | `major version: 65` |
| Boot 2 + 环境变量密钥 | Spring Boot 2.7.18 / JDK 17 | 解密成功，返回 `demo-secret-value` |
| Boot 2 + 启动参数密钥 | Spring Boot 2.7.18 / JDK 17 | 解密成功，日志为 `Found Custom Encryptor Bean com.example.jasypt.spring.boot2.CoreStringEncryptor` |
| 缺少密钥 | Spring Boot 3.5.16 / JDK 21 | fail-fast，提示提供 `jasypt.encryptor.password` |
| 原有 Web 页面与接口 | JDK 25 | 页面 200，加解密闭环正常 |
| core 直接被调用 | Java 8 字节码 | 独立工程加解密往返成功 |

### 限制与取舍

- 必须按 Boot 大版本选择对应 starter：Boot 2.7 用 `jasypt-spring-boot2-starter`，Boot 3.5 用 `jasypt-spring-boot3-starter`；这是上游两条版本线造成的取舍。
- 自动解密只作用于 Spring `Environment` 中的属性（`@Value`、`@ConfigurationProperties`、`Environment#getProperty` 等）；自行读取文件或 `System.getenv()` 的值不会被解密。
- `jasypt-core` 仍保持 Java 8、无 Spring 依赖；`jasypt-web` 仍为 JDK 25；Boot 3 starter 为 JDK 21+，Boot 2 starter 为 Java 8+。
- 算法、盐、IV 由 core 固定，starter 不接受使用方改写，以保证密文互通。
- jasypt 提供的是配置加密/防窥，不应替代密钥管理系统；生产环境应通过环境变量、启动参数或专用密钥服务下发密钥。
- 每次加密使用随机盐和随机 IV，同一明文每次得到的密文不同，属正常行为。

## 实现说明

- 共通方法：`jasypt-core` 中的 `com.example.jasypt.core.JasyptCrypto`；Web 层与 starter 都只做委托，不重复实现算法。
- 自动解密：`jasypt-spring-boot3-starter` 传递 `com.github.ulisesbocchio:jasypt-spring-boot-starter:4.0.4`；`jasypt-spring-boot2-starter` 传递 `3.0.5`。两者均注册名为 `jasyptStringEncryptor` 的 `StringEncryptor` Bean，内部调用 core。
- 加密算法：`PBEWITHHMACSHA512ANDAES_256`
- 随机盐：`RandomSaltGenerator`
- 随机 IV：`RandomIvGenerator`
- 每次加密都会生成新的盐和 IV，因此同一明文每次得到的密文不同；解密时必须使用加密时的同一密钥。
