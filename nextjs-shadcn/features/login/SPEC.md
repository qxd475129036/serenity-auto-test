# 登录

- 路由: `/login`
- 状态: 已接入 Better Auth（用户名/密码转发第三方 API，当前 mock）
- 版本: 0.4

## 目标

- 提供登录页 `/login`，通过 **Better Auth** 完成用户名/密码登录。
- 凭据（用户名 + 密码）由 `better-auth-credentials-plugin` 转发到第三方认证 API 校验；校验通过后建立 session（签名 cookie，无状态，无需数据库）。
- 当前第三方 API 为本地 mock（`/api/mock-third-party/login`），真实接入时仅改 `THIRD_PARTY_API_URL`。

## 非目标

- 不做注册、找回密码、邮箱验证、社交登录（仅用户名/密码）。
- 不引入数据库；用户身份与 token 由第三方 API 提供。
- 路由守卫由根级 `proxy.ts` 负责，仅做登录态存在性判断，不做角色/权限控制。

## 用户与场景

- 未登录用户访问受保护页面（除 `/login`、`/api/**` 外的所有页面）→ 重定向 `/login?next=<原路径+query>`。
- 未登录用户打开 `/login` → 输入用户名密码 → 提交 → 成功后跳转到 `next`；无 `next` 时跳转 `/`；失败显示错误 toast。
- 已登录用户打开 `/login` → 自动跳转（有 `next` 回 `next`，否则回 `/`）。

## 页面与路由

| 路由 | 说明 |
|---|---|
| `/login` | 登录页，细则见 [app/login/PAGE.md](../../app/login/PAGE.md) |
| `/api/auth/*` | Better Auth 全量端点（登录/登出/session） |
| `/api/mock-third-party/login` | Mock 第三方认证 API |

## 功能需求

### 正常流程

- UI 语言: 日文（ja），页面根节点 `lang="ja"`；文案以 app/login/PAGE.md 为准。
- 用户名、密码输入（带前缀图标，Label 关联，autoComplete 语义正确）；密码支持显隐切换。
- 提交时调用 `authClient.signIn.credentials({ username, password })`。
- 成功: toast 提示，并跳转到 `next`（默认 `/`）。
- 失败: toast 展示错误信息（来自 Better Auth 的 `error.message`）。
- 回跳参数 `next` 仅接受站内路径：必须以 `/` 开头、不以 `//` 开头、不以 `/login` 或 `/api` 开头；非法值回退 `/`（防开放重定向与自跳转）。

### 路由守卫

- 由根级 `proxy.ts`（Next.js 16 Proxy，替代 middleware）实现，使用 `getSessionCookie` 做乐观判断。
- 公开路由: `/login` 与 `/api/**`；静态资源不拦截。
- 未登录访问其他页面 → 跳转 `/login`；目标非 `/` 时附带 `next`（保留原 query string）。

### 异常与边界

- 用户名或密码为空时提交，显示错误 toast（不发请求）。
- 第三方 API 返回非 2xx → Better Auth 返回 401，前端展示 "Invalid username or password"。
- 请求中按钮禁用并显示 "Signing in..."，防重复提交。

## 验收标准

- `/login` 200 渲染，无 console 错误；默认亮色显示正常。
- 未登录访问 `/` 或 `/demo` → 跳转 `/login`（`/demo` 附带 `next`）。
- 用户名 `admin`、密码 `password` 登录成功：无 `next` 时到 `/`；带 `next` 时回到原页面（含 query）。
- 已登录访问 `/login` → 自动跳转到 `next` 或 `/`。
- 错误密码出 error toast（401）。
- 登出后回到登录表单。
- 验证三件套通过（docs/verification.md）。

## 数据与接口

- 第三方认证 API（当前 mock）:
  - `POST /api/mock-third-party/login`
  - 入参: `{ username: string, password: string }`
  - 成功: `{ data: { token: string, user: { username: string, name: string } } }`
  - 失败: `{ error: { code: string, message: string } }`
  - Mock 规则: `password === "password"` 成功，否则 401。
- Better Auth 凭据端点: `POST /api/auth/sign-in/credentials`（由 plugin 注册，body 同 inputSchema）。
- 环境变量: `BETTER_AUTH_SECRET`、`NEXT_PUBLIC_APP_URL`、`THIRD_PARTY_API_URL`（见 `.env.local`）。

## 风险与依赖

- 无状态模式下 session 全在 cookie，第三方 token 随 user 字段存入 cookie，token 过大可能超 cookie 限制（当前 mock token 很小）。
- Better Auth 要求 `BETTER_AUTH_SECRET`，未设置时 dev 报错。

## 决策记录

- 2026-10: 原 `/demo1` 变体页改为登录页 `/login`。
- 2026-10: 确定认证方案为 Better Auth + better-auth-credentials-plugin，无状态模式，用户名/密码转发第三方 API（先 mock）。登录字段由 email 改为 username。
- 2026-11: 登录页 UI/UX 重构：系统定位为日企内部请求系统 "rabbit"，改为左右分栏（左品牌面板 + 右表单），UI 语言日文，新增密码显隐切换；保持单色中性 token 配色（品牌色待定）。
- 2026-11: 新增路由守卫（`proxy.ts`）与登录后回跳（`next`）；已登录访问 `/login` 自动跳转；登出入口迁移到首页 `/`。
- 2026-11: 登录页移除返回按钮、记住我、忘记密码占位入口，简化表单。

## 开放问题

1. 真实第三方 API 的地址、错误码约定与 token 刷新策略待定（接入时改 `THIRD_PARTY_API_URL` 并在 callback 中补充 token 刷新逻辑）。
