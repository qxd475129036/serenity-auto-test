<!-- BEGIN:nextjs-agent-rules -->

# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->

# 项目: nextjs-shadcn

基于 Next.js App Router 的 shadcn/ui 组件演示场：交互式展示全部 61 个 shadcn 组件，并作为后续产品功能的骨架工程。

## 技术栈（摘要）

Next.js 16（App Router）+ React 19 + TypeScript（strict）+ Tailwind CSS v4 + shadcn/ui（radix-nova / neutral 基色）
包管理器: **npm**（禁止混用 pnpm/yarn）
详见 [docs/tech-stack.md](docs/tech-stack.md)

## 目录地图

```
app/               路由与页面；页面级细则放同目录 PAGE.md
components/ui/     shadcn 组件库（CLI 生成，61 个）
features/          功能域 SPEC.md（业务规则唯一真相源）
docs/              项目级与规范级文档
hooks/ lib/        共享 hooks 与工具
```

## 必读文档（AI 入口索引）

- 架构与目录约定: [docs/architecture.md](docs/architecture.md)
- 设计系统（token/组件/可访问性）: [docs/design-system.md](docs/design-system.md)
- 编码规范与禁令: [docs/coding-conventions.md](docs/coding-conventions.md)
- 接口约定: [docs/api.md](docs/api.md)
- 验证命令与证据要求: [docs/verification.md](docs/verification.md)

## 硬性禁令

- 不修改与本任务无关的文件
- 不引入未经批准的新依赖；shadcn 组件用 `npx shadcn add`，不手写 `components/ui/` 新文件
- 不使用 `any`；不用裸 `@ts-ignore`
- 不修改本文件顶部 `nextjs-agent-rules` 块（由 next dev 自动管理）
- 提交前必跑: `npm run typecheck && npm run lint && npm run build`

## 任务流程

1. 定位功能域，读 `features/{域}/SPEC.md`
2. 涉及具体页面时，再读 `app/{route}/PAGE.md`
3. 先输出实现计划，确认后再改代码
4. 完成后按 [docs/verification.md](docs/verification.md) 的证据格式汇报

## 任务指令模板

> 读 AGENTS.md → features/components-demo/SPEC.md → app/demo/PAGE.md，实现 XXX。
