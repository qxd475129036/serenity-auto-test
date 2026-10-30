# 登录

- 路由: `/login`
- 状态: 已接入 Better Auth（用户名/密码转发第三方 API，当前 mock）
- 版本: 0.2

## 目标

- 提供登录页 `/login`，通过 **Better Auth** 完成用户名/密码登录。
- 凭据（用户名 + 密码）由 `better-auth-credentials-plugin` 转发到第三方认证 API 校验；校验通过后建立 session（签名 cookie，无状态，无需数据库）。
- 当前第三方 API 为本地 mock（`/api/mock-third-party/login`），真实接入时仅改 `THIRD_PARTY_API_URL`。

## 非目标

- 不做注册、找回密码、邮箱验证、社交登录（仅用户名/密码）。
- 不引入数据库；用户身份与 token 由第三方 API 提供。
- 不做路由级守卫/middleware；登录态由页面内 `useSession` 判定。

## 用户与场景

- 未登录用户打开 `/login` → 输入用户名密码 → 提交 → 成功后显示已登录态（用户名 + token 摘要 + 登出按钮）；失败显示错误 toast。
- 已登录用户打开 `/login` → 直接看到已登录态，可登出。

## 页面与路由

| 路由 | 说明 |
|---|---|
| `/login` | 登录页，细则见 [app/login/PAGE.md](../../app/login/PAGE.md) |
| `/api/auth/*` | Better Auth 全量端点（登录/登出/session） |
| `/api/mock-third-party/login` | Mock 第三方认证 API |

## 功能需求

### 正常流程

- 用户名、密码输入（带前缀图标，Label 关联，autoComplete 语义正确）。
- 记住我 Checkbox（作为 `rememberMe` 传给 Better Auth）。
- 提交时调用 `authClient.signIn.credentials({ username, password, rememberMe })`。
- 成功: toast 提示，页面刷新后展示已登录态（用户名、token 摘要、Sign out 按钮）。
- 失败: toast 展示错误信息（来自 Better Auth 的 `error.message`）。
- 忘记密码: 占位按钮（type="button"），后续接流程。
- 返回按钮回首页 `/`。
- 已登录态: Sign out 调用 `authClient.signOut()`，刷新后回到表单。

### 异常与边界

- 用户名或密码为空时提交，显示错误 toast（不发请求）。
- 第三方 API 返回非 2xx → Better Auth 返回 401，前端展示 "Invalid username or password"。
- 请求中按钮禁用并显示 "Signing in..."，防重复提交。

## 验收标准

- `/login` 200 渲染，无 console 错误；默认亮色显示正常。
- 用户名 `admin`、密码 `password` 登录成功，展示已登录态（含 token）。
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

## 开放问题

1. 真实第三方 API 的地址、错误码约定与 token 刷新策略待定（接入时改 `THIRD_PARTY_API_URL` 并在 callback 中补充 token 刷新逻辑）。
