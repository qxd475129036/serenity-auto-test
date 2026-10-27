# nextjs-shadcn

基于 Next.js 16 App Router 的 shadcn/ui 组件演示场，展示全部 61 个组件，并作为后续产品功能的骨架工程。

## 功能入口

| 路由 | 说明 |
|---|---|
| `/` | 项目入口与组件演示导航 |
| `/demo` | 61 个 shadcn/ui 组件的交互演示 |
| `/login` | 登录表单 UI 骨架，暂未接入后端 |

## 技术栈

- Next.js 16 + React 19 + TypeScript strict
- Tailwind CSS v4 + shadcn/ui（radix-nova / neutral）
- 包管理器：npm

## 本地运行

```bash
npm install
npm run dev
```

打开 [http://localhost:3000](http://localhost:3000)。

## 验证

```bash
npm run typecheck
npm run lint
npm run build
```

## 文档

- [架构与目录约定](docs/architecture.md)
- [技术栈](docs/tech-stack.md)
- [设计系统](docs/design-system.md)
- [编码规范](docs/coding-conventions.md)
- [API 约定](docs/api.md)
- [验证要求](docs/verification.md)

AI 开发入口与硬性规则见 [AGENTS.md](AGENTS.md)。
