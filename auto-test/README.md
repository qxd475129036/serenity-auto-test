# Batch API Test Suite

基于 Serenity BDD、JUnit 5 和 Spring JDBC 的 Java 测试工程。测试按业务域组织，并通过
`@Epic`、`@Feature`、`@Story` 描述需求层级。

## 技术栈

- JDK 25
- Spring Boot 4.0.9
- JUnit 5 + Serenity JUnit 5 Extension
- Serenity BDD 5.3.3
- Spring JdbcTemplate + H2 / Oracle JDBC
- Apache Commons Exec
- Serenity REST Assured + Screenplay REST

## 目录结构

```text
src/test/java/com/example/autotest/
├── config/TestSettings.java
├── support/LocalOrderApi.java
├── order/
│   ├── OrderLookupStoryTest.java
│   ├── OrderScreenplayStoryTest.java
│   ├── OrderParallelStoryTest.java
│   ├── OrderQuerySupport.java
│   └── OrderScreenplay.java
├── reconciliation/
│   ├── ReconciliationStoryTest.java
│   └── ReconciliationSupport.java
└── documentation/
    ├── LivingDocumentationStoryTest.java
    └── ReportEvidence.java
```

目前有 5 个 Story 测试类，每个测试类通过 class-level `@Story` 描述具体业务价值：

- 订单：同一 Feature 下包含普通查询、Screenplay 和并行查询 3 个 Story。
- 对账：对账成功，以及批处理失败时保持原数据。
- 活文档：嵌套步骤、Session Variable、动态场景和 Pending。

Serenity 报告层级为 `@Epic > @Feature > @Story > Test`。

## 需求层级演示

`订单查询` 是一个完整的演示 Feature。3 个测试类共享相同的
`@Epic("订单服务")` 和 `@Feature("订单查询")`，再分别用不同的 `@Story`
拆出业务行为：

```text
订单服务 (@Epic)
└── 订单查询 (@Feature)
    ├── 按订单号查询订单 (@Story)
    │   ├── 查询订单 1
    │   ├── 查询订单 2
    │   ├── 查询不存在的订单返回 404
    │   └── 查询配置的外部订单
    ├── 使用 Screenplay 查询订单 (@Story)
    │   ├── Actor 执行 REST Task 并回答 Question
    │   └── Screenplay Ensure 交互断言
    └── 并行查询订单 (@Story)
        ├── 并行查询订单 1
        ├── 并行查询订单 2
        ├── 并行查询订单 3
        └── 并行查询订单 4
```

因此该 Feature 在报告中显示为 `1 个 Feature -> 3 个 Story -> 10 个 Scenario`。
其中外部订单 Scenario 默认因 `api.enabled=false` 被跳过，不影响本地构建。

约定如下：

- 一个 Serenity Story 对应一个测试类，并通过 class-level `@Story` 命名。
- 一个 Scenario 对应一个 `@Test` 方法；演示 Feature 使用独立场景展示层级。
- 多个 Story 测试类只要使用相同的 `@Epic` 和 `@Feature`，就会聚合到同一 Feature。

## 本地运行

```bash
./mvnw clean verify
```

默认使用 H2 文件数据库执行本地闭环。外部订单 API 测试默认跳过。

报告地址：`target/site/serenity/index.html`。

## 标签过滤

```bash
./mvnw clean verify -Dtags=smoke
./mvnw clean verify -Dtags=negative
./mvnw clean verify -Dtags=demo
./mvnw clean verify -Dtags=screenplay
./mvnw clean verify -Dtags=parallel
```

标签用于测试筛选，`@Story` 用于报告中的需求层级。

## 外部订单 API

外部订单测试由 `@EnabledIfSystemProperty` 控制，默认跳过：

```bash
./mvnw clean verify \
  -Dapi.enabled=true \
  -Dapi.base.url=https://staging.example.com \
  -Dapi.order.id=10001
```

## 真实环境

`staging` profile 从环境变量读取批处理与数据库配置：

```bash
export ORACLE_URL='jdbc:oracle:thin:@//staging-db:1521/ORCLPDB1'
export ORACLE_USER='test_user'
export ORACLE_PASSWORD='test_password'
export BATCH_SHELL_PATH='/opt/batch/run_reconciliation.sh'
export BATCH_LOG_DIR='/opt/batch/logs'
export BATCH_DATE='2026-10-31'

./mvnw clean verify -Pstaging
```

也可直接覆盖 Maven 参数：

```bash
./mvnw clean verify \
  -Ddb.url='jdbc:oracle:thin:@//staging-db:1521/ORCLPDB1' \
  -Ddb.user=test_user \
  -Ddb.password=test_password \
  -Dbatch.shell.path=/opt/batch/run_reconciliation.sh \
  -Dbatch.log.dir=/opt/batch/logs
```

## 批处理契约

外部批处理脚本需要：

- 接受 `--date <business-date>`。
- 成功时返回退出码 `0`，失败时返回非零退出码。
- 将日志写入 `BATCH_LOG_DIR/reconciliation.log`。
- 接收 `DB_KIND`、`JDBC_URL`、`JDBC_USER`、`JDBC_PASSWORD` 等环境变量。

超时由 `-Dbatch.timeout.seconds=...` 控制。

## 数据库断言

对账场景使用：

```sql
transactions(id, status, amount)
reconciliation_summary(run_date, reconciled_count, status)
```

批处理执行、数据库操作和日志断言统一收敛在 `ReconciliationSupport`，测试类只表达业务场景。
