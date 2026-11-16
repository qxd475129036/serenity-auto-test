# API 约定

## 现状

已引入 `/api` 路由（Better Auth、get-data 转发、mock 登录），暂无 Server Actions。
本文档定义 API 标准，接口落地后在此登记清单。

## API 共通中转层

除认证接口外的 API 统一走 `lib/api/`，由中转层完成「双会话校验 → 权限校验 → 注入 Spring cookie → 转发后端 → 统一响应包」。

- 双会话校验: Better Auth 会话存在且 `user.token` 非空，**并且** Spring session cookie（`SPRING_SESSION_COOKIE_NAME`）存在；任一缺失 → `401 E_UNAUTHORIZED`。
- 权限校验: 会话携带的 `user.permissions`（登录时从后端 `PERMISSIONS_API_PATH`，默认 `/api/me` 拉取）需包含所需权限码；含 `*` 视为全部权限；不足 → `403 E_FORBIDDEN`。
- 显式路由: `app/api/**/route.ts` 使用 `createApiHandler({ upstreamPath, permission?, validateBody? })`，一行完成上述流程。
- 通用代理: `/api/proxy/<path>` → `${THIRD_PARTY_API_URL}/api/<path>`，复用同一套逻辑；权限按 `lib/api/permissions.ts` 的 `UPSTREAM_PERMISSIONS`（后端路径 → 权限码）判定，未登记则仅需登录。
- 上游映射: 401 → E_UNAUTHORIZED；403 → E_FORBIDDEN；404 → E_NOT_FOUND；3xx（Spring 未认证跳转 `/login`）→ 401 E_UNAUTHORIZED；其余非 2xx → 502 E_INTERNAL。不回传上游错误细节。

## 路由处理器规范（引入时）

- 位置: `app/api/**/route.ts`（App Router route handler）。
- 统一响应包:

```jsonc
// 成功
{ "data": { ... } }
// 失败
{ "error": { "code": "E_VALIDATION", "message": "人类可读描述" } }
```

- 初始错误码表:

| 码 | 含义 |
|---|---|
| E_VALIDATION | 参数校验失败（message 说明字段） |
| E_NOT_FOUND | 资源不存在 |
| E_UNAUTHORIZED | 未登录 |
| E_FORBIDDEN | 权限不足 |
| E_INTERNAL | 服务端内部错误（对外不暴露细节） |

- 鉴权: 采用 **Better Auth**（无状态模式，session 存储于签名 cookie，无需数据库）。用户名/密码通过 `better-auth-credentials-plugin` 转发到 Spring Boot 表单登录（CSRF 开启时为"GET /login 取 `_csrf` + 会话 cookie → POST /login"两步流程），Spring 返回的 session cookie 值（名取 `SPRING_SESSION_COOKIE_NAME`）作为 sessionId 存入会话 `user.token`，并在登录成功时由 `hooks.after` 种植同名独立 HttpOnly cookie、登出时清除。
- API 不返回页面跳转逻辑（如 `redirect: true`），跳转决策归前端/调用方。

### 响应包例外

- `/api/auth/*`（Better Auth 挂载路由）遵循 Better Auth 自身的响应约定，**不**使用本项目的 `{data}` / `{error:{code,message}}` 包。其错误由 Better Auth 统一封装，前端通过 `authClient` 返回的 `error` 字段读取。
- 其余 `/api/**` 路由必须遵循上述统一响应包。

### 后端数据接口转发（getData）

- 浏览器 → 本项目 `POST /api/get-data` → 后端 `${THIRD_PARTY_API_URL}/api/getData`。
- 已接入共通中转层：需双会话（Better Auth + Spring）且具备 `data:read` 权限（见 `lib/api/permissions.ts`），否则 401/403。
- 入参为 JSON 对象（页面固定发送 `{ "lobCd": 10 }`），服务端原样转发；中转层从会话读取 Spring sessionId 并作为 `Cookie` 头带给后端，复用 Spring 登录态。
- 上游响应结构未知，统一包成 `{ "data": <上游 JSON> }`；上游非 2xx 按上文规则映射，不回传上游错误细节。
- 前端 `/data` 页面按数组、`{ data: [...] }` 以及 `list` / `items` / `records` / `rows` / `result` / `content` 等常见包装防御性解析。

## Server Actions 规范（引入时）

- 表单提交优先 Server Action（`useActionState`），不自造 fetch 表单。
- 命名: `submitXxx` / `deleteXxx`，与动作语义一致。
- 每个 Action 返回统一结构 `{ ok: true, data }` / `{ ok: false, error }`。

## 接口清单

| 接口 | 方法 | 说明 | 引入日期 |
|---|---|---|---|
| `/api/auth/*` | GET/POST | Better Auth 全量端点（登录/登出/session 等），由 `toNextJsHandler` 挂载（不走中转层） | 2026-10 |
| `/api/mock-third-party/login` | POST | 历史 Mock 第三方认证 API（已不再被引用，保留备用，不走中转层） | 2026-10 |
| `/api/get-data` | POST | 后端 getData 转发代理（已接入中转层，需 `data:read` 权限） | 2026-11 |
| `/api/proxy/[...path]` | GET/POST/PUT/PATCH/DELETE | 通用后端中转，转发到 `${THIRD_PARTY_API_URL}/api/<path>`，统一鉴权与响应包 | 2026-11 |

环境变量: `THIRD_PARTY_API_URL`、`SPRING_SESSION_COOKIE_NAME`、`PERMISSIONS_API_PATH`（默认 `/api/me`）。

外部依赖: Spring Boot + Spring Security 表单登录 `POST ${THIRD_PARTY_API_URL}/login`，form-urlencoded；开启 CSRF 时需先 `GET /login` 取 `_csrf` 与同会话 cookie 再 POST。成功返回 302（无 `?error`）+ `Set-Cookie: <name>=<id>`；cookie 名用 `SPRING_SESSION_COOKIE_NAME` 配置（默认 SESSION，Tomcat 默认为 JSESSIONID）。
