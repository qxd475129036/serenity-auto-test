# 技术栈

本项目技术选型的唯一真相源。涉及选型问题先查这里，再决定。

## 核心栈

| 项 | 版本 | 说明 |
|---|---|---|
| next | 16.3.4 | App Router；`params`/`searchParams` 是异步（Promise），用前查 `node_modules/next/dist/docs/` |
| react / react-dom | 19.2.8 | |
| typescript | 5.9.3 | `strict: true` |
| tailwindcss | 4.3.3 | CSS-first 配置（`@theme`），无 tailwind.config.js |
| @tailwindcss/postcss | 4.x | PostCSS 插件 |
| shadcn (CLI) | 4.21.0 | `npx shadcn add <component>` |
| @shadcn/react | 0.3.1 | |
| radix-ui | 1.6.7 | 组件原语基底 |
| @base-ui/react | 1.8.0 | 部分组件基底 |

## 支撑库

| 库 | 版本 | 用途 |
|---|---|---|
| lucide-react | 1.43.0 | 唯一图标库（components.json: iconLibrary=lucide） |
| class-variance-authority | 0.7.1 | 组件变体（shadcn 惯例） |
| cn | 0.2.6 | className 合并工具 |
| sonner | 2.0.8 | Toast 通知 |
| next-themes | 0.4.6 | 亮暗主题（已安装，ThemeProvider 未挂载） |
| recharts | 3.8.0 | 图表（配合 Chart 组件） |
| cmdk | 1.1.1 | 命令面板（Command 组件） |
| date-fns | 4.4.0 | 日期处理 |
| tw-animate-css | 1.4.0 | Tailwind 动画工具类（shadcn 配套） |
| better-auth | 1.7.x | 认证框架（无状态 cookie session） |
| better-auth-credentials-plugin | 0.5.x | 用户名/密码凭据转发第三方 API 校验 |
| zod | 4.x | schema 校验（credentials-plugin peer 依赖） |
| vaul | 1.1.2 | Drawer 抽屉 |
| embla-carousel-react | 8.6.0 | Carousel 轮播 |
| input-otp | 1.5.0 | OTP 输入 |
| react-day-picker | 10.0.1 | Calendar 日历 |
| react-resizable-panels | 4.12.4 | Resizable 分栏 |

## shadcn 配置（components.json）

- style: `radix-nova`；baseColor: `neutral`；cssVariables: true；rsc: true
- 图标库: `lucide`
- 别名: `@/components`、`@/lib/utils`、`@/components/ui`、`@/lib`、`@/hooks`

## 开发依赖

- eslint 9 + `eslint-config-next` 16.3.4（core-web-vitals + typescript）
- @types/node 20、@types/react 19

## 包管理

- **npm**（仓库内有 package-lock.json）。禁止混用 pnpm/yarn 安装，避免 lock 文件漂移。

## 版本升级规则

- 升级 Next / React 必须单独一个 PR，先读 `node_modules/next/dist/docs/` 中对应指南。
- 更新 shadcn 组件: `npx shadcn add <name> --overwrite`，升级后必须走验证三件套（docs/verification.md）。
