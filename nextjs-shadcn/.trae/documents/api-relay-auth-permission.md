# API 共通中转层：统一会话注入、登录校验与权限校验

## Summary

以 `POST /api/get-data`（现有后端 getData 转发代理）为样板，抽出一套**共通 API 中转层**：

1. **包装函数** `createApiHandler(config)`：每个 `app/api/**/route.ts` 一行接入，自动完成
   「取双会话 → 校验登录 → 校验权限 → 注入 Spring `JSESSIONID` → 转发后端 → 统一响应包」。
2. **通用 catch-all 代理** `app/api/proxy/[...path]/route.ts`：复用同一套逻辑，未单独建路由的后端接口可零代码转发。

认证接口 `/api/auth/*` 与历史 mock `/api/mock-third-party/*` 不走该层。
`get-data` 改造为首个接入样板，行为与文案保持不变。

用户已确认的决策：
- 权限 = **静态「接口 → 权限码」映射** + **会话中携带的权限码**（登录时从后端用户信息接口拉取并写入会话）。
- 形态 = **包装函数 + catch-all 代理两者结合**。
- 认证口径 = **双会话校验**（Better Auth 会话存在且 `user.token` 非空 + Spring session cookie 存在）。

## Current State Analysis

### 现有代码

- [app/api/get-data/route.ts](file:///Users/quxd/git/serenity-auto-test/nextjs-shadcn/app/api/get-data/route.ts#L1-L127)：
  已实现「读 Spring cookie → 转发 `${THIRD_PARTY_API_URL}/api/getData` → 包 `{data}`」，
  但**完全没有登录校验**；只转发 cookie，cookie 缺失时仍会请求上游。
  错误包/上游状态映射（L17-L37）是本项目唯一一份，需要抽公用。
- [lib/auth.ts](file:///Users/quxd/git/serenity-auto-test/nextjs-shadcn/lib/auth.ts#L47-L90)：
  Better Auth 无状态实例；`user.additionalFields` 目前只有 `token`；
  `credentials` callback 成功时返回 `{ email, name, token }`；`hooks.after` 负责种/清 Spring cookie。
- [lib/auth-client.ts](file:///Users/quxd/git/serenity-auto-test/nextjs-shadcn/lib/auth-client.ts)：仅客户端，服务端 API 鉴权不使用。
- [proxy.ts](file:///Users/quxd/git/serenity-auto-test/nextjs-shadcn/proxy.ts#L37-L42)：`matcher` 已排除 `/api/**`，页面守卫与 API 鉴权互不影响。
- [docs/api.md](file:///Users/quxd/git/serenity-auto-test/nextjs-shadcn/docs/api.md#L7-L42)：定义统一响应包 `{data}` / `{error:{code,message}}`、
  错误码表（E_VALIDATION / E_NOT_FOUND / E_UNAUTHORIZED / E_FORBIDDEN / E_INTERNAL），并规定 `/api/auth/*` 例外。
- [.env.local](file:///Users/quxd/git/serenity-auto-test/nextjs-shadcn/.env.local)：`THIRD_PARTY_API_URL=http://127.0.0.1:8080`、
  `SPRING_SESSION_COOKIE_NAME=JSESSIONID`。
- API 路由全量清单：仅 `app/api/auth/[...all]/route.ts`、`app/api/get-data/route.ts`、`app/api/mock-third-party/login/route.ts`。
- 当前**无任何角色/权限模型**（[features/back-office/SPEC.md](file:///Users/quxd/git/serenity-auto-test/nextjs-shadcn/features/back-office/SPEC.md#L13-L18) 明确写「不做角色/权限判定」）。

### 关键约束

- Better Auth 无数据库，权限码必须随会话（签名 cookie 的 JWT）持久化，故需加 `permissions` additionalField。
- Spring 登录成功响应是 302、无响应体，权限必须**登录后额外请求**后端用户信息接口获得。
- Next 16 route handler 签名 `(request: NextRequest, ctx: { params: Promise<...> })`；包装函数返回 `(request) => Promise<Response>` 可被直接导出。

## Proposed Changes

### 1. 新增 `lib/api/permissions.ts`：权限码与「接口 → 权限」映射

```ts
export const PERMISSIONS = {
  DATA_READ: "data:read",
} as const
export type Permission = (typeof PERMISSIONS)[keyof typeof PERMISSIONS] | (string & {})

/** 后端接口路径 → 所需权限码（catch-all 代理使用；未登记的接口仅要求登录） */
export const UPSTREAM_PERMISSIONS: Record<string, Permission> = {
  "/api/getData": PERMISSIONS.DATA_READ,
}

/** 会话权限码是否满足要求：支持 "*" 通配；required 为空表示仅需登录 */
export function hasPermission(granted: readonly string[], required?: Permission): boolean
```

### 2. 新增 `lib/api/session.ts`：服务端双重会话读取

```ts
export const SESSION_COOKIE_NAME = process.env.SPRING_SESSION_COOKIE_NAME?.trim() || "SESSION"

export type ApiSession = { username: string; springSessionId: string; permissions: string[] }

export async function getApiSession(request: NextRequest): Promise<ApiSession | null>
```

实现要点：
1. `const session = await auth.api.getSession({ headers: request.headers })`（服务端引入 `lib/auth`）。
2. 无 session、或 `session.user.token` 非字符串/空 → `null`。
3. `request.cookies.get(SESSION_COOKIE_NAME)?.value` 为空 → `null`（双会话口径）。
4. `permissions` 取 `session.user.permissions`（`string[]`，缺省 `[]`）。
5. 返回 `{ username: session.user.name ?? session.user.email, springSessionId, permissions }`。

### 3. 新增 `lib/api/proxy.ts`：统一响应 + 转发 + 包装函数

- `ok(data)` / `fail(code, message, status)`（错误码类型复用 docs/api.md 的五种）。
- `upstreamErrorResponse(status)`：401→E_UNAUTHORIZED、403→E_FORBIDDEN、404→E_NOT_FOUND、
  **3xx→E_UNAUTHORIZED（Spring 会话过期会 302 到 /login）**、其余→E_INTERNAL(502)。
  文案沿用 get-data 现有日文。
- `relayToBackend({ request, upstreamPath, session })`：构造头（`Accept`、原始 `Content-Type`、`Cookie: <name>=<sessionId>`），
  `fetch(..., { method, body, redirect: "manual", cache: "no-store" })`；转发原始 body（`text`/`arrayBuffer`）。
- `createApiHandler(config)`，`config` 形态：

```ts
type ApiHandlerConfig = {
  upstreamPath: string                       // 如 "/api/getData"
  permission?: Permission                    // 省略 = 仅需登录
  validateBody?: (body: unknown) => string | null  // 返回非空字符串 = 校验失败消息
}

export function createApiHandler(config: ApiHandlerConfig) {
  return async (request: NextRequest): Promise<Response> => { ... }
}
```

处理顺序（**任何一步失败即短路**）：
1. `BACKEND_BASE_URL` 未配置 → 500 E_INTERNAL（文案同现状）。
2. `getApiSession` 为 `null` → **401 E_UNAUTHORIZED**「認証が必要です。」。
3. `permission` 且 `!hasPermission` → **403 E_FORBIDDEN**「アクセス権限がありません。」。
4. `validateBody` 存在时解析 JSON 并校验；失败 → 400 E_VALIDATION（文案同现状）。
5. 转发；非 2xx / 3xx → `upstreamErrorResponse`；空响应体 → `{ data: null }`；
   JSON 解析失败 → 502 E_INTERNAL「…応答を解析できませんでした。」；成功 → `{ data: parsed }`。

### 4. 改造 `app/api/get-data/route.ts`（行为不变，去掉重复代码）

```ts
export const POST = createApiHandler({
  upstreamPath: "/api/getData",
  permission: PERMISSIONS.DATA_READ,
  validateBody: /* 保留现有「必须是 JSON 对象」校验与日文消息 */,
})
```

删除文件内的 `errorResponse` / `upstreamErrorResponse` 与手写 fetch 逻辑（已被 `lib/api/proxy.ts` 取代）。
对外契约不变：请求 `{ lobCd: 10 }`，成功 `{data}`，失败 `{error:{code,message}}`。

### 5. 新增 `app/api/proxy/[...path]/route.ts`：通用中转

- 导出 `GET/POST/PUT/PATCH/DELETE`，方法白名单之外的请求由框架 405。
- 路径安全：拼接 `/api/${path.join("/")}`；若任一段为空/含 `..`/含反斜杠 → 404 E_NOT_FOUND；结果必须以 `/api/` 开头。
- 权限：`UPSTREAM_PERMISSIONS[upstreamPath]`（未登记 = 仅登录）。
- 复用 `getApiSession` + `relayToBackend`，**不复制**包装函数里的错误映射（提取为 `handleRelay` 内部函数供两者调用）。
- 透传 query string；body 原样转发。
- 例：`/api/proxy/getData` → `${THIRD_PARTY_API_URL}/api/getData`。

### 6. `lib/auth.ts`：会话携带权限码

1. `user.additionalFields` 增加：
   ```ts
   permissions: { type: "string[]", required: false, returned: true },
   ```
2. credentials callback 登录成功后，拉取权限：
   - `const permissionsPath = process.env.PERMISSIONS_API_PATH?.trim() || "/api/me"`
   - 用 `Cookie: <name>=<sessionId>` 调 `${thirdPartyApiUrl}${permissionsPath}`（`AbortSignal.timeout(3000)`、`cache: "no-store"`）。
   - 宽松解析（按顺序命中即用）：顶层字符串数组 → `permissions` 数组 → `authorities`（兼容 `[{authority}]` 与 `["ROLE_X"]`）→ `roles` 数组。
   - 非 2xx / 网络失败 / 解析失败 → `[]`（不阻断登录；此时受权限保护的接口会返回 403，属预期）。
3. 返回值增加 `permissions`。

### 7. `.env.local` 增加权限接口路径

```bash
# 登录后拉取当前用户权限码的后端接口（默认 /api/me）
PERMISSIONS_API_PATH=/api/me
```

### 8. 文档同步

- [docs/api.md](file:///Users/quxd/git/serenity-auto-test/nextjs-shadcn/docs/api.md)：
  新增「API 共通中转层」小节（包装函数用法、双会话校验顺序 401/403、catch-all `/api/proxy/*` 约定、权限映射表与环境变量）；
  接口清单补 `/api/proxy/*`；`/api/get-data` 说明改为「已接入中转层」。
- [features/back-office/SPEC.md](file:///Users/quxd/git/serenity-auto-test/nextjs-shadcn/features/back-office/SPEC.md#L13-L18)：
  非目标中「不做角色/权限判定」改为「页面级菜单暂未按权限过滤；API 级权限校验由共通中转层负责」；
  「数据与接口」补充 API 中转与权限口径。
- [features/login/SPEC.md](file:///Users/quxd/git/serenity-auto-test/nextjs-shadcn/features/login/SPEC.md)：
  目标/数据与接口补一句：会话额外携带后端返回的权限码（`user.permissions`），供 API 中转层校验。

### 9. 不做的事

- 不改 `proxy.ts`（页面守卫）、不改登录页 UI、不做页面/菜单级权限过滤。
- 不引入新依赖、不改 `components/ui/`、不删除 mock 路由。
- 不做权限缓存/刷新机制（权限在每次登录时写入会话）。

## Assumptions & Decisions

| # | 决策 | 依据 |
|---|---|---|
| A1 | 认证 = Better Auth 会话 + Spring session cookie 双存在 | 用户选择「双会话校验」 |
| A2 | 权限码在登录时从 `PERMISSIONS_API_PATH`（默认 `/api/me`）拉取，失败则空数组 | 用户选择「后端有用户信息接口」但未给字段；解析放宽到 permissions/authorities/roles/顶层数组 |
| A3 | 权限在 Next 侧判定的同时，后端仍会自行鉴权（Spring 403 兜底） | 纵深防御；上游 403 映射为 E_FORBIDDEN |
| A4 | catch-all 统一放在 `/api/proxy/*`，不覆盖 `/api/auth/*` 与既有显式路由 | 避免与静态路由冲突；「两者结合」的落地方式 |
| A5 | 未在 `UPSTREAM_PERMISSIONS` 登记的路径仅要求登录 | 避免新增接口被默认拒绝；敏感接口显式登记权限 |
| A6 | 上游 3xx 视为会话失效返回 401 | Spring Security 未认证时 302 → `/login` |
| A7 | `get-data` 声明 `data:read` 权限 | 让权限链路真实生效；若后端无该权限码则返回 403，需按后端实际权限码调整 `lib/api/permissions.ts` |

## Verification

1. `npm run typecheck && npm run lint && npx next build --webpack` 全绿。
2. 未登录（无任何 cookie）：
   - `POST /api/get-data` → **401** `{"error":{"code":"E_UNAUTHORIZED",...}}`
   - `GET /api/proxy/getData` → 401
   - `GET /api/auth/get-session` 不受影响（仍 200）。
3. 已登录（需真实账号，用户提供或在浏览器完成）：
   - `POST /api/get-data` 带浏览器 cookie → 200 `{data: ...}`，且上游收到 `Cookie: JSESSIONID=...`；
   - `/api/proxy/getData` 与 `/api/get-data` 结果一致；
   - 会话中无 `data:read`（后端未返回该权限）→ **403 E_FORBIDDEN**，用于验证权限链路。
4. 浏览器：`/data` 页点击「検索」正常出数据；删除 cookie 后点击 → 提示 401 错误文案。
5. 证据格式按 [docs/verification.md](file:///Users/quxd/git/serenity-auto-test/nextjs-shadcn/docs/verification.md) 汇报。

## Risks

- 后端实际权限接口路径/字段未知：默认 `/api/me` + 宽松解析；若不符，只需改 `PERMISSIONS_API_PATH` 或 `lib/auth.ts` 中的解析函数。
- 权限码命名需与后端对齐（`data:read` 为占位），不一致会导致 get-data 403。
- 登录时多一次后端请求（3s 超时），失败不阻断登录。
- catch-all 代理会扩大服务端可访问的上游面，已用 `/api/` 前缀与路径段校验限制。
