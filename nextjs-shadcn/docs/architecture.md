# 架构与目录约定

## 分层与依赖方向

```
app（路由/页面） → components（组件） → hooks / lib（共享逻辑）
```

依赖只能自上而下，低层不得 import 高层。`features/` 与 `docs/` 是纯文档目录，不参与代码依赖。

## 目录地图

```
proxy.ts            路由守卫（Next.js 16 Proxy）：未登录页面跳转 /login
app/
  layout.tsx          根布局：Geist 字体、TooltipProvider、metadata
  globals.css         Tailwind v4 入口 + 设计 token（@theme / :root / .dark）
  (app)/              登录后业务系统的路由组（不参与 URL）
    layout.tsx          AppHeader（顶部导航）+ 内容区
    page.tsx            首页（工作台）/（含登出入口）
    PAGE.md             首页页面级细则
    permissions/        権限（ユーザー）管理占位路由
    master/             マスタ管理占位路由
    billing/            請求業務管理占位路由
    cod/                代引業務管理占位路由
    repayments/         弁済業務管理占位路由
    statements/         明細ダウンロード占位路由
  demo/               组件演示页 /demo（含 PAGE.md，不套顶部导航）
  login/              登录页 /login（含 PAGE.md）
components/
  ui/                 shadcn 组件库（61 个，CLI 生成）
  app/                业务系统外壳与工作台组件（AppHeader、ModuleCard、PlaceholderPage、nav-config）
  login/              登录域包装组件（SignOutButton）
hooks/
  use-mobile.ts       响应式断点 hook
lib/
  utils.ts            cn() className 合并
features/
  home/SPEC.md            首页（工作台）功能域规格
  back-office/SPEC.md     业务后台模块地图与占位页规格
  components-demo/SPEC.md 组件演示功能域规格
  login/SPEC.md           登录功能域规格
docs/                 本套规范文档
```

## 路由与页面约定

- 只用 App Router 文件约定: `page.tsx` / `layout.tsx` / `route.ts` / `error.tsx` / `loading.tsx`。
- `app/layout.tsx` 统一应用于全部页面（html/body、字体、metadata、TooltipProvider）。
- `app/(app)/layout.tsx` 是登录后业务系统的路由组布局，统一渲染顶部导航；路由组不参与 URL，`app/(app)/page.tsx` 仍是 `/`。
- `/login` 与 `/demo` 不在 `(app)` 路由组内，不显示顶部导航。
- 新路由 = 新建 `app/{route}/` 目录；页面复杂时同目录加 `PAGE.md`（页面级细则）。
- 登录后业务模块的路由与占位规则见 [features/back-office/SPEC.md](../features/back-office/SPEC.md)。
- PAGE 按页面顺序维护元素小节，每个元素固定记录“展示 / 定义 / 默认 / 交互”；用户 Actions 内联在触发元素下，不维护 DOM/组件树、元素 ID、独立 Actions 表或组件库通用 API。
- 业务逻辑按功能域组织，规格写 `features/{域}/SPEC.md`；对应 UI 包装组件放 `components/{域}/`。

## 布局宽度约定

登录后业务系统（`(app)` 路由组）的内容宽度统一由布局层控制，**各 page 不得单独设置宽度尺寸**。

### 宽度规则

- **最小宽度**: 1440px（`body` 设 `min-w-[1440px]`，屏幕窄于此时出现横向滚动，内容不被压缩）
- **大屏占比**: 屏幕宽度大于 1440px 时，内容区占屏幕宽度的 80%，居中显示
- 内容容器使用 `w-[80%] min-w-[1440px] mx-auto`，实际宽度 = `max(1440px, 屏幕宽度 × 80%)`

| 屏幕宽度 | 内容宽度 | 行为 |
|---------|---------|------|
| ≤ 1440px | 1440px | 横向滚动 |
| 1440 ~ 1800px | 1440px | 80% 尚未超过 1440，取最小值 |
| > 1800px | 屏幕宽度 × 80% | 随屏幕增长，左右各留 10% |

### 控制点（唯一真相源）

宽度与内边距集中在以下三处，**不要在 page 或业务组件中再写 `max-w-*` / `mx-auto` 宽度类**：

1. `app/layout.tsx` — `<body>` 设 `min-w-[1440px]`，保证整页不窄于 1440。
2. `app/(app)/layout.tsx` — `<main>` 设 `mx-auto w-[80%] min-w-[1440px] px-4 py-8 sm:px-6 lg:px-8`，统一控制内容宽度与内边距。
3. `components/app/app-header.tsx` — 导航内层容器使用相同的 `w-[80%] min-w-[1440px] mx-auto`，保证导航与正文左右边界对齐。

page 只需返回内容本身（用 fragment `<>...</>` 包裹多个兄弟节点即可），宽度和内边距由 `<main>` 提供。

### 例外

- `/login`：全屏左右分栏登录页，不套用 80% 约束，保持自身全屏布局。
- `/demo`：组件展示场，自带 header 与独立宽度（`max-w-5xl`），不套用业务页宽度规则。

## Server / Client Component 策略

- 默认 Server Component；仅在需要状态、事件处理、浏览器 API 时加 `"use client"`。
- 当前客户端组件: `/demo`（交互密集）、`/login`（表单状态）、`components/login/sign-out-button.tsx`（登出交互）、`components/app/app-header.tsx`（导航下拉与移动抽屉）。
- 跨 Server→Client 边界只传可序列化 props。
- Next 16 有 breaking changes：写页面/布局前先查 `node_modules/next/dist/docs/`（如 `params` 是 Promise，需 `await`）。

## 状态管理

- 不引入全局状态库；当前规模用 `useState`/`useReducer` + props 足够。
- 未来如引入（zustand 等），先更新本文档与 docs/tech-stack.md，再写代码。

## 认证

- 采用 **Better Auth**（`lib/auth.ts` 服务端 / `lib/auth-client.ts` 客户端），无状态模式：不接数据库，session 存签名 cookie。
- 用户名/密码通过 `better-auth-credentials-plugin` 以 `application/x-www-form-urlencoded` 转发到 Spring Boot `POST ${THIRD_PARTY_API_URL}/login` 校验。后端开启 CSRF 时，先 `GET /login` 建立会话并解析页面中的 `_csrf`，再携同会话 cookie 与 `_csrf` POST；认证成功（302 且无 `?error`）后从 `Set-Cookie` 解析 sessionId（cookie 名取 `SPRING_SESSION_COOKIE_NAME`，默认 SESSION）。403 等流程异常一律视为失败，不误判成功。
- sessionId 双写：存入 Better Auth 会话的 `user.token`，并由 `hooks.after` 在登录成功时种植同名独立 HttpOnly cookie（浏览器 DevTools 可见，JS 不可读）、登出时清除；不写 localStorage / sessionStorage。后续调用 Spring 受保护接口需经 Next 服务端读取后携带 `Cookie: <name>=<id>` 转发。
- 全量端点挂载在 `/api/auth/[...all]`；登录页 `/login` 用 `authClient.signIn.credentials` / `authClient.useSession` / `authClient.signOut`。
- 路由守卫由根级 `proxy.ts`（Next.js 16 Proxy，替代 middleware）实现：除 `/login` 与 `/api/**` 外的页面在未登录时重定向 `/login?next=<原路径+query>`，使用 `getSessionCookie` 做乐观判断；登录成功后回 `next`（默认 `/`）。
- 详见 [features/login/SPEC.md](../features/login/SPEC.md) 与 [docs/api.md](api.md)。

## 别名

- tsconfig: `@/*` → `./`
- shadcn 子别名见 components.json（`ui` → `@/components/ui` 等）。

## 主题

- next-themes 已安装，ThemeProvider 尚未挂载；`dark` 由 `.dark` 类驱动（globals.css 中 `@custom-variant dark`）。
- 启用主题切换时：根布局挂 `<ThemeProvider attribute="class">`，并在本文档登记。
