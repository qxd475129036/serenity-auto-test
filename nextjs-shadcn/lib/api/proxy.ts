import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

import { hasPermission, type Permission } from "./permissions"
import { SESSION_COOKIE_NAME, getApiSession, type ApiSession } from "./session"

/** 后端数据服务基础地址（沿用认证后端的既有环境变量约定） */
const BACKEND_BASE_URL = process.env.THIRD_PARTY_API_URL?.replace(/\/+$/, "")

export type ErrorCode =
  | "E_VALIDATION"
  | "E_NOT_FOUND"
  | "E_UNAUTHORIZED"
  | "E_FORBIDDEN"
  | "E_INTERNAL"

/** 统一成功响应包 `{ data }` */
export function ok(data: unknown): NextResponse {
  return NextResponse.json({ data })
}

/** 统一失败响应包 `{ error: { code, message } }` */
export function fail(
  code: ErrorCode,
  message: string,
  status: number,
): NextResponse {
  return NextResponse.json({ error: { code, message } }, { status })
}

/** 上游状态码 → 本项目统一错误包（不向上游响应细节） */
export function upstreamErrorResponse(status: number): NextResponse {
  if (status === 401) {
    return fail("E_UNAUTHORIZED", "認証が必要です。", 401)
  }
  if (status === 403) {
    return fail("E_FORBIDDEN", "アクセス権限がありません。", 403)
  }
  if (status === 404) {
    return fail("E_NOT_FOUND", "データが見つかりませんでした。", 404)
  }
  return fail("E_INTERNAL", "データ取得サーバーでエラーが発生しました。", 502)
}

function backendNotConfigured(): NextResponse {
  return fail("E_INTERNAL", "THIRD_PARTY_API_URL が設定されていません。", 500)
}

type Authorized = { ok: true; session: ApiSession }
type Rejected = { ok: false; response: NextResponse }

/**
 * API 中转层统一鉴权：配置检查 → 双会话校验 → 权限校验。
 *
 * 任何一步失败都返回对应的统一错误包，调用方直接短路返回即可。
 */
export async function authorizeApiRequest(
  request: NextRequest,
  permission?: Permission,
): Promise<Authorized | Rejected> {
  if (!BACKEND_BASE_URL) {
    return { ok: false, response: backendNotConfigured() }
  }

  const session = await getApiSession(request)
  if (!session) {
    return {
      ok: false,
      response: fail("E_UNAUTHORIZED", "認証が必要です。", 401),
    }
  }

  if (!hasPermission(session.permissions, permission)) {
    return {
      ok: false,
      response: fail("E_FORBIDDEN", "アクセス権限がありません。", 403),
    }
  }

  return { ok: true, session }
}

type RelayOptions = {
  request: NextRequest
  /** 后端路径，如 `/api/getData` */
  upstreamPath: string
  session: ApiSession
  /** 已读取的请求体文本（GET/HEAD 为 undefined） */
  bodyText?: string
  /** 可选请求体校验：返回非空字符串表示校验失败消息 */
  validateBody?: (body: unknown) => string | null
}

/**
 * 携带 Spring Session cookie 转发到后端，并把上游响应包成统一结构。
 *
 * - 上游 3xx（未登录跳转 /login）→ 401
 * - 上游 401/403/404 → 对应错误码；其余非 2xx → 502
 */
export async function handleRelay({
  request,
  upstreamPath,
  session,
  bodyText,
  validateBody,
}: RelayOptions): Promise<Response> {
  if (!BACKEND_BASE_URL) {
    return backendNotConfigured()
  }

  if (validateBody) {
    let payload: unknown
    try {
      payload = JSON.parse(bodyText ?? "")
    } catch {
      return fail("E_VALIDATION", "リクエストボディが不正な JSON です。", 400)
    }

    const message = validateBody(payload)
    if (message) {
      return fail("E_VALIDATION", message, 400)
    }
  }

  const headers: Record<string, string> = {
    Accept: "application/json",
    Cookie: `${SESSION_COOKIE_NAME}=${session.springSessionId}`,
  }
  const contentType = request.headers.get("content-type")
  if (contentType) {
    headers["Content-Type"] = contentType
  }

  const method = request.method
  const hasBody = method !== "GET" && method !== "HEAD"
  const upstreamUrl = `${BACKEND_BASE_URL}${upstreamPath}${request.nextUrl.search}`

  let upstream: Response
  try {
    upstream = await fetch(upstreamUrl, {
      method,
      headers,
      body: hasBody ? (bodyText ?? "") : undefined,
      redirect: "manual",
      cache: "no-store",
    })
  } catch {
    return fail("E_INTERNAL", "データ取得サーバーに接続できませんでした。", 502)
  }

  // Spring Security 未认证时会 302 到 /login，视为会话失效。
  if (upstream.status >= 300 && upstream.status < 400) {
    return fail("E_UNAUTHORIZED", "認証が必要です。", 401)
  }

  if (!upstream.ok) {
    return upstreamErrorResponse(upstream.status)
  }

  const text = await upstream.text()
  if (!text) {
    return ok(null)
  }

  try {
    return ok(JSON.parse(text))
  } catch {
    return fail(
      "E_INTERNAL",
      "データ取得サーバーの応答を解析できませんでした。",
      502,
    )
  }
}

export type ApiHandlerConfig = {
  /** 后端路径，如 `/api/getData` */
  upstreamPath: string
  /** 所需权限码；省略表示仅需登录 */
  permission?: Permission
  /** 可选请求体校验：返回非空字符串表示校验失败消息 */
  validateBody?: (body: unknown) => string | null
}

/**
 * 创建一个带「双会话校验 + 权限校验 + Spring cookie 注入 + 统一响应包」的 route handler。
 *
 * 用法：
 * ```ts
 * export const POST = createApiHandler({ upstreamPath: "/api/getData" })
 * ```
 */
export function createApiHandler(config: ApiHandlerConfig) {
  return async (request: NextRequest): Promise<Response> => {
    const auth = await authorizeApiRequest(request, config.permission)
    if (!auth.ok) {
      return auth.response
    }

    const method = request.method
    const bodyText =
      method === "GET" || method === "HEAD" ? undefined : await request.text()

    return handleRelay({
      request,
      upstreamPath: config.upstreamPath,
      session: auth.session,
      bodyText,
      validateBody: config.validateBody,
    })
  }
}
