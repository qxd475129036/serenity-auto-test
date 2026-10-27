# 计划:引入 shadcn/ui 全部组件

## 概述

在已有的 Next.js 16 项目(当前目录)中初始化 shadcn/ui 并安装其全部组件。

## 当前状态分析

- 项目已存在:create-next-app 生成的 Next.js 16.3.4 + React 19.2.8 + Tailwind CSS v4 + TypeScript,App Router、无 src 目录、Turbopack。
- `tsconfig.json` 已配置 `@/*` -> `./*` 路径别名(shadcn 必需,已满足)。
- `app/globals.css` 为默认 Tailwind v4 模板,尚无 shadcn 主题变量。
- **未安装依赖**(无 node_modules)。
- **无 components.json**(shadcn 未初始化)。

## 实施步骤

### 1. 安装项目依赖

```bash
npm install
```

安装 package.json 中已有的 next/react/tailwind 等依赖。

### 2. 初始化 shadcn/ui

```bash
npx shadcn@latest init -y -b neutral
```

- 自动检测 Next.js + Tailwind v4。
- 生成 `components.json`。
- 重写 `app/globals.css` 为 shadcn 主题变量(含暗色模式)。
- 创建 `lib/utils.ts`(cn 函数)。
- 安装基础依赖:class-variance-authority、clsx、tailwind-merge、lucide-react、tw-animate-css。

### 3. 安装全部 shadcn 组件

```bash
npx shadcn@latest add --all -y -o
```

- 一键安装注册表中全部组件(button、dialog、dropdown-menu、data-table、chart、form、calendar、sonner 等约 50 个),源码写入 `components/ui/`。
- `-o` 覆盖已存在文件,`-y` 跳过确认。
- 组件所需第三方依赖(如 recharts、react-day-picker、embla-carousel-react、next-themes、sonner、input-otp、react-resizable-panels 等)由 CLI 自动装。

### 4. 验证

- `npm run build`:确认 TypeScript 编译与生产构建通过。
- 检查 `components/ui/` 目录组件数量,抽查 `components.json` 与 `lib/utils.ts`。

## 假设与决策

- 基础色板使用 shadcn 默认的 **neutral**(未指定,取默认值)。
- 保留现有 App Router 结构与 `app/page.tsx`,不额外创建演示页。
- 不修改 ESLint 配置。
