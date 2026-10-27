# 需求层级规则（Epic / Feature / Story / 场景）

本文档回答：拿到一个新需求，测试类的 `@Epic` / `@Feature` / `@Story` / `@Title` 怎么写、场景怎么拆。

## 1. 层级模型

Serenity 按 class-level 注解字符串聚合测试结果，报告 Requirements 页呈现为树：

```text
@Epic  (业务服务)            例: "订单服务"
└── @Feature (功能域)        例: "订单查询"
    └── @Story (业务行为)    例: "按订单号查询订单"     ← 一个 Story = 一个测试类
        └── @Test 场景(@Title) 例: "查询不存在的订单返回 404"   ← 一个 @Test = 一个场景
```

| 层级 | 语义 | 粒度判据 |
| --- | --- | --- |
| `@Epic` | 业务服务 / 大领域 | 通常与域包目录一一对应 |
| `@Feature` | 服务内的功能域 | 一组可独立交付的相近行为 |
| `@Story` | 单个完整业务行为 | 能一句话说清「作为用户，我想……以便……」；对应一个测试类 |
| `@Title`（@Test 上） | Story 内单个场景 | 不同输入 / 预期 / 数据通路各一个 |

## 2. 现有清单（快照，以仓库实际注解为准）

```text
订单服务 (@Epic, 包 order)
└── 订单查询 (@Feature)
    ├── 按订单号查询订单 (@Story → OrderLookupStoryTest, 4 场景)
    ├── 使用 Screenplay 查询订单 (@Story → OrderScreenplayStoryTest, 2 场景)
    └── 并行查询订单 (@Story → OrderParallelStoryTest, 4 场景)
交易对账 (@Epic, 包 reconciliation)
└── 日终批处理 (@Feature)
    └── 执行日终对账 (@Story → ReconciliationStoryTest, 2 场景)
测试工程能力 (@Epic, 包 documentation)
└── 测试报告 (@Feature)
    └── 生成活文档 (@Story → LivingDocumentationStoryTest, 5 场景)
```

## 3. 命名规范

- `@Epic`：业务服务名词短语，2-6 字，如「订单服务」「交易对账」「测试工程能力」
- `@Feature`：「业务对象 + 功能域」，稳定、长期复用，如「订单查询」「日终批处理」「测试报告」
- `@Story`：「动词 + 对象」业务行为，描述用户价值，如「按订单号查询订单」「执行日终对账」「生成活文档」
- `@Title`：具体场景，「条件 / 输入 + 预期行为」，如「查询不存在的订单返回 404」「日终对账失败」「Session Variable 跨步骤共享状态」
- 四级一律中文业务语言；不出现 Java 类名、英文代码名与技术实现细节（表名、HTTP 路径除外——仅当它本身就是断言对象时）
- 不写 `@Title` 时 Serenity 会从方法名生成标题（变成英文），本工程必须显式写 `@Title`

## 4. 拆分决策树（新需求按序执行）

1. **定业务服务**：`rg -n '@Epic\("' src` 枚举已有 `@Epic`。需求属于已有服务 → 复用该字符串，代码放对应域包；不属于 → 新建 Epic，并新建域包 `com.example.autotest.{域}`
2. **定功能域**：`rg -n '@Feature\("' src` 枚举该 Epic 下已有 `@Feature`。属于已有功能域 → 复用；否则新建 Feature（仍放同一域包）
3. **定 Story 粒度**：需求能否表达为单一业务行为？能 → 1 个 Story = 1 个测试类；不能 → 拆多个 Story，各一个测试类。判据：两个行为无法用一句「用户 + 想 + 以便」描述，就必须拆
4. **定场景粒度**：同一 Story 内，不同输入、不同预期（成功 / 失败 / 边界）、不同数据通路（本地 stub / 外部 API，H2 / Oracle）各建独立 `@Test` 场景；「同一行为换 N 组数据重复」用少量场景或 `@TestFactory` 动态场景
5. **已确认但未实现的需求**：测试类中放占位场景并加 `@Pending`，不写实现（报告显示 Pending，构建不失败）

## 5. 聚合规则（为什么必须匹配已有字符串）

- Serenity 按 `@Epic` + `@Feature` + `@Story` 三个字符串对测试结果分组；多个测试类共享相同 `@Epic` + `@Feature` 时聚合到同一 Feature
- 现有示例：order 包 3 个测试类共享 `@Epic("订单服务")` + `@Feature("订单查询")` → 报告呈现 `1 个 Feature → 3 个 Story → 10 个 Scenario`
- 反例：同一功能写成「订单查询」和「订单查询功能」，报告会劈裂出两个互不相干的 Feature

## 6. 标签词汇表

| 标签 | 级别 | 含义 | 现有示例 |
| --- | --- | --- | --- |
| `demo` | class | 演示类测试，整 Story 参与筛选 | 现有 5 个演示类 |
| `smoke` | method | 核心成功路径 | 查询订单 1 |
| `negative` | method | 异常 / 失败路径 | 查询不存在的订单返回 404 |
| `screenplay` | method | Screenplay 模式场景 | Actor 执行 REST Task 并回答 Question |
| `parallel` | method | 并发执行场景（必须配合 `@Execution(ExecutionMode.CONCURRENT)`） | 并行查询订单 1 |
| `api` | method | 依赖真实外部 API（必须配合 `@EnabledIfSystemProperty`） | 查询配置的外部订单 |

规则：class 级标签标识整个 Story（是否演示）；method 级标签标识场景的执行特征。`-Dtags=...` 过滤用法见 [verification.md](verification.md)。
