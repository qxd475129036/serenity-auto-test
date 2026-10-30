# API 约定

## 现状

当前无 `/api` 路由、无 Server Actions，所有页面静态。本文档定义**引入 API 时**的标准，接口落地后在此登记清单。

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

- 鉴权: 采用 **Better Auth**（无状态模式，session 存储于签名 cookie，无需数据库）。用户名/密码通过 `better-auth-credentials-plugin` 转发到第三方认证 API 校验（当前为 mock）。CSRF 由 Better Auth 内置处理。
- API 不返回页面跳转逻辑（如 `redirect: true`），跳转决策归前端/调用方。

### 响应包例外

- `/api/auth/*`（Better Auth 挂载路由）遵循 Better Auth 自身的响应约定，**不**使用本项目的 `{data}` / `{error:{code,message}}` 包。其错误由 Better Auth 统一封装，前端通过 `authClient` 返回的 `error` 字段读取。
- 其余 `/api/**` 路由必须遵循上述统一响应包。

## Server Actions 规范（引入时）

- 表单提交优先 Server Action（`useActionState`），不自造 fetch 表单。
- 命名: `submitXxx` / `deleteXxx`，与动作语义一致。
- 每个 Action 返回统一结构 `{ ok: true, data }` / `{ ok: false, error }`。

## 接口清单

| 接口 | 方法 | 说明 | 引入日期 |
|---|---|---|---|
| `/api/auth/*` | GET/POST | Better Auth 全量端点（登录/登出/session 等），由 `toNextJsHandler` 挂载 | 2026-10 |
| `/api/mock-third-party/login` | POST | Mock 第三方认证 API：入参 `{username,password}`，密码为 `password` 时成功返回 `{token,user}` | 2026-10 |
