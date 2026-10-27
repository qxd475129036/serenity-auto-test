# 构建、验证与环境

## 1. 本地构建（默认闭环）

```bash
./mvnw clean verify
```

- H2 文件数据库（`target/test-db`，Oracle 模式，自动加载 schema）+ `scripts/run_local_reconciliation.sh` 本地批处理脚本 + `LocalOrderApi` 本地 HTTP stub
- 全部场景应通过（`api.enabled=false` 门控的场景自动跳过）
- 报告产出：`target/site/serenity/index.html`

## 2. 标签过滤

```bash
./mvnw clean verify -Dtags=smoke       # 核心成功路径
./mvnw clean verify -Dtags=negative    # 异常路径
./mvnw clean verify -Dtags=demo        # 全部演示 Story
./mvnw clean verify -Dtags=screenplay  # Screenplay 场景
./mvnw clean verify -Dtags=parallel    # 并行场景
```

tags 同时被 surefire（选择执行）与 serenity-maven-plugin（选择报告）消费。标签词汇见 requirements-hierarchy.md 第 6 节。

## 3. 外部 API

```bash
./mvnw clean verify \
  -Dapi.enabled=true \
  -Dapi.base.url=https://staging.example.com \
  -Dapi.order.id=10001
```

## 4. staging 环境

```bash
export ORACLE_URL='jdbc:oracle:thin:@//staging-db:1521/ORCLPDB1'
export ORACLE_USER='test_user'
export ORACLE_PASSWORD='test_password'
export BATCH_SHELL_PATH='/opt/batch/run_reconciliation.sh'
export BATCH_LOG_DIR='/opt/batch/logs'
export BATCH_DATE='2026-10-31'

./mvnw clean verify -Pstaging
```

也可直接用 `-Ddb.url=... -Ddb.user=... -Ddb.password=... -Dbatch.shell.path=... -Dbatch.log.dir=...` 覆盖。

## 5. 批处理脚本契约

外部批处理脚本必须满足：

- 接受 `--date <业务日期>`（未知参数 → 退出码 64）
- 退出码 `0` = 成功，非零 = 失败（本地脚本：`2` = 模拟失败，`3` = DB_KIND 不是 h2，`64` = 参数错误）
- 日志写入 `BATCH_LOG_FILE`（默认 `target/batch-logs/reconciliation.log`）
- 接收环境变量 `DB_KIND` / `JDBC_URL` / `JDBC_USER` / `JDBC_PASSWORD` / `JDBC_DRIVER_JAR`
- 超时由 `batch.timeout.seconds` 控制（test 30 秒，staging 600 秒）

## 6. 报告验证标准（新需求交付必查）

打开 `target/site/serenity/index.html`，逐条确认：

1. 新 Story 出现在 Requirements 的正确 `Epic > Feature > Story` 位置，字符串与现有聚合键一致
2. 场景标题显示 `@Title` 中文文案，数量与预期一致
3. REST 场景带请求/响应证据；数据库场景显示完整步骤树与断言结果
4. 文件证据可下载（使用 `recordReportData().downloadable()` 时）
5. `@Pending` 场景显示为 Pending，构建不红
6. 标签过滤生效：如 `-Dtags=smoke` 只执行 smoke 场景

## 7. 故障速查

| 症状 | 首先检查 |
| --- | --- |
| 报告里同一功能被劈成两个 Feature | `@Epic` / `@Feature` 字符串不一致（错别字 / 同义不同词） |
| 新场景没进报告 | `@Test` 是否真的执行？是否被 `-Dtags` 过滤掉？ |
| 本地构建因外部 API 场景失败 | 传了 `-Dapi.enabled=true` 但服务不可用 |
| `IllegalStateException: Missing configuration '...'` | 缺必填配置，按报错里的属性名 / 环境变量提示补齐 |
| 批处理场景超时失败 | 超时设置过小（本地 30s）或脚本挂起 |
