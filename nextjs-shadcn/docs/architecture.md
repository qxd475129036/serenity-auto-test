# 架构与目录约定

## 分层与依赖方向

```
app（路由/页面） → components（组件） → hooks / lib（共享逻辑）
```

依赖只能自上而下，低层不得 import 高层。`features/` 与 `docs/` 是纯文档目录，不参与代码依赖。

## 目录地图

```
app/
  layout.tsx          根布局：Geist 字体、TooltipProvider、metadata
  page.tsx            首页 /
  globals.css         Tailwind v4 入口 + 设计 token（@theme / :root / .dark）
  demo/               组件演示页 /demo（含 PAGE.md）
  login/              登录页 /login（含 PAGE.md）
  PAGE.md             首页页面级细则
components/
  ui/                 shadcn 组件库（61 个，CLI 生成）
hooks/
  use-mobile.ts       响应式断点 hook
lib/
  utils.ts            cn() className 合并
features/
  home/SPEC.md            首页功能域规格
  components-demo/SPEC.md 组件演示功能域规格
  login/SPEC.md             登录功能域规格
docs/                 本套规范文档
```

## 路由与页面约定

- 只用 App Router 文件约定: `page.tsx` / `layout.tsx` / `route.ts` / `error.tsx` / `loading.tsx`。
- `app/layout.tsx` 统一应用于全部页面（html/body、字体、metadata、TooltipProvider）；当前无路由级 layout，PAGE 不重复记录 layout 继承关系。
- 新路由 = 新建 `app/{route}/` 目录；页面复杂时同目录加 `PAGE.md`（页面级细则）。
- PAGE 按页面顺序维护元素小节，每个元素固定记录“展示 / 定义 / 默认 / 交互”；用户 Actions 内联在触发元素下，不维护 DOM/组件树、元素 ID、独立 Actions 表或组件库通用 API。
- 业务逻辑按功能域组织，规格写 `features/{域}/SPEC.md`；对应 UI 包装组件放 `components/{域}/`。

## Server / Client Component 策略

- 默认 Server Component；仅在需要状态、事件处理、浏览器 API 时加 `"use client"`。
- 当前客户端组件: `/demo`（交互密集）、`/login`（表单状态）。
- 跨 Server→Client 边界只传可序列化 props。
- Next 16 有 breaking changes：写页面/布局前先查 `node_modules/next/dist/docs/`（如 `params` 是 Promise，需 `await`）。

## 状态管理

- 不引入全局状态库；当前规模用 `useState`/`useReducer` + props 足够。
- 未来如引入（zustand 等），先更新本文档与 docs/tech-stack.md，再写代码。

## 认证

- 采用 **Better Auth**（`lib/auth.ts` 服务端 / `lib/auth-client.ts` 客户端），无状态模式：不接数据库，session 存签名 cookie。
- 用户名/密码通过 `better-auth-credentials-plugin` 转发到第三方认证 API（`THIRD_PARTY_API_URL`，当前为 `/api/mock-third-party`）校验。
- 全量端点挂载在 `/api/auth/[...all]`；登录页 `/login` 用 `authClient.signIn.credentials` / `authClient.useSession` / `authClient.signOut`。
- 详见 [features/login/SPEC.md](../features/login/SPEC.md) 与 [docs/api.md](api.md)。

## 别名

- tsconfig: `@/*` → `./`
- shadcn 子别名见 components.json（`ui` → `@/components/ui` 等）。

## 主题

- next-themes 已安装，ThemeProvider 尚未挂载；`dark` 由 `.dark` 类驱动（globals.css 中 `@custom-variant dark`）。
- 启用主题切换时：根布局挂 `<ThemeProvider attribute="class">`，并在本文档登记。
