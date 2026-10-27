# 编码规范

## 类型

- tsconfig `strict: true`；禁止 `any`，用 `unknown` + 类型收窄。
- `@ts-ignore` / 非空断言 `!` 必须带说明注释，解释为什么安全。
- 组件 props 显式声明类型；回调参数不依赖隐式 any。

## 命名

- 文件/目录: kebab-case（`button.tsx`、`use-mobile.ts`）；页面遵循 App Router 文件名约定（`page.tsx`、`layout.tsx`）。
- 组件: PascalCase；函数/变量: camelCase；hooks: `useXxx`。
- 常量: UPPER_SNAKE_CASE。

## 导入

- 跨目录一律用 `@/` 别名，禁止 `../../../` 深相对路径。
- 同目录内用 `./`。
- 顺序: next → 第三方 → `@/components` → 相对路径。

## shadcn 组件

- 新增组件: `npx shadcn add <name>`（生成到 `components/ui/`）。
- 不手工新建 `components/ui/` 下的文件；不手改生成文件的结构（调样式可以，改 API 前先 `--overwrite` 对比官方版本）。
- 需要定制/封装: 在 `components/{域}/xxx.tsx` 包装 ui 组件并重新导出，页面引用包装层。
- 组件导出清单见 `.trae/documents/plan-components-demo-page.md` 附录。

## 错误处理

- 服务端: 抛错交给 `error.tsx` 边界；需要穿透时用 `unstable_rethrow`。
- 客户端: 用 sonner toast 或 `Alert` 组件内联提示，不用 `alert()`。
- 禁止空 `catch {}`；必须 catch 时处理或向上抛。

## 依赖

- 未经批准不引入新依赖；加依赖前先确认现有库能否覆盖（`npm ls <keyword>`）。
- 批准引入后必须登记到 docs/tech-stack.md。
- 包管理只用 npm。
