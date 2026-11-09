# 登录

- 路由: `/login`
- 状态: 已接入 Spring Boot + Spring Security 表单登录（经 Better Auth 转发）
- 版本: 0.6

## 目标

- 提供登录页 `/login`，通过 **Better Auth** 完成用户名/密码登录。
- 凭据（用户名 + 密码）由 `better-auth-credentials-plugin` 以 `application/x-www-form-urlencoded` 转发到 Spring Boot 的 `POST /login` 校验；校验通过后建立 session（签名 cookie，无状态，无需数据库）。
- Spring Boot 返回的 sessionId（`Set-Cookie: <name>=<id>`，名取 `SPRING_SESSION_COOKIE_NAME`）同时存放于两处：Better Auth 会话的 `user.token`，以及登录成功响应中额外种植的同名 HttpOnly cookie（浏览器 DevTools 可见）；均不写入 localStorage / sessionStorage。

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
| `/api/mock-third-party/login` | 历史 Mock 第三方认证 API（已不再被引用，保留备用） |

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

- 第三方认证 API（Spring Boot + Spring Security，两步流程）:
  - Step 1 `GET ${THIRD_PARTY_API_URL}/login`：建立会话，从 `Set-Cookie` 解析 session cookie（名取 `SPRING_SESSION_COOKIE_NAME`），并从登录页 HTML 解析 `_csrf` hidden input 值；解析不到 `_csrf` 视为后端未开启 CSRF，Step 2 不携带。
  - Step 2 `POST ${THIRD_PARTY_API_URL}/login`：`application/x-www-form-urlencoded`，携带 `Cookie: <name>=<Step 1 的 id>` 与 `username`、`password`（有 CSRF 时附带 `_csrf`），`redirect: "manual"`。
  - 成功: 302 且 `Location` 不含 `?error`；sessionId 取 POST 响应的新 `Set-Cookie`（认证成功后 Spring 默认轮换 session id），无则回退 Step 1 的 id。
  - 失败: `Location` 含 `?error` / 401 / 200 登录页 HTML → 统一映射为 401 `Invalid username or password`；403（如 CSRF token 缺失）与其余异常 → 502 `Malformed response from auth provider`，**绝不视为成功**。
- Better Auth 凭据端点: `POST /api/auth/sign-in/credentials`（由 plugin 注册，body 同 inputSchema）。
- 环境变量: `BETTER_AUTH_SECRET`、`NEXT_PUBLIC_APP_URL`、`THIRD_PARTY_API_URL`、`SPRING_SESSION_COOKIE_NAME`（默认 `SESSION`，见 `.env.local`）。
- 存储: sessionId 存于 Better Auth 会话（HttpOnly cookie）的 `user.token`，同时由 `hooks.after` 在登录成功时种同名独立 HttpOnly cookie、登出时清除；前端 JS 不可读，调用 Spring 受保护接口须经 Next 服务端读取后以 `Cookie: <name>=<id>` 转发。

## 风险与依赖

- 无状态模式下 session 全在 cookie，Spring sessionId 随 user 字段存入 cookie（UUID 级，体积可忽略）。
- Better Auth 要求 `BETTER_AUTH_SECRET`，未设置时 dev 报错。

## 决策记录

- 2026-10: 原 `/demo1` 变体页改为登录页 `/login`。
- 2026-10: 确定认证方案为 Better Auth + better-auth-credentials-plugin，无状态模式，用户名/密码转发第三方 API（先 mock）。登录字段由 email 改为 username。
- 2026-11: 登录页 UI/UX 重构：系统定位为日企内部请求系统 "rabbit"，改为左右分栏（左品牌面板 + 右表单），UI 语言日文，新增密码显隐切换；保持单色中性 token 配色（品牌色待定）。
- 2026-11: 新增路由守卫（`proxy.ts`）与登录后回跳（`next`）；已登录访问 `/login` 自动跳转；登出入口迁移到首页 `/`。
- 2026-11: 登录页移除返回按钮、记住我、忘记密码占位入口，简化表单。
- 2026-11: 接入真实 Spring Boot + Spring Security 表单登录：callback 改为 form-urlencoded 并解析 `Set-Cookie: SESSION`；sessionId 仅存 HttpOnly cookie，不落 localStorage。
- 2026-11: 适配后端开启 CSRF 的场景：登录改为"GET /login 取 `_csrf` 与同会话 cookie → POST 携带"两步流程；修复无 `_csrf` 时后端 403 被误判为登录成功的 bug；登录成功后由 `hooks.after` 额外种植同名独立 HttpOnly cookie（DevTools 可见），登出时清除。

## 开放问题

1. Spring session 的过期/续期策略待定（会话失效时需引导用户重新登录）。
2. 调用 Spring 受保护接口的 BFF 转发路由尚未实现（本次仅完成登录接入与 sessionId 存储）。
