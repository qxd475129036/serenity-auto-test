import type { NextRequest } from "next/server"

import { auth } from "@/lib/auth"
import { SPRING_SESSION_COOKIE_NAME } from "@/lib/spring-auth"

/** Spring Session cookie 名（后端使用 JSESSIONID 时由环境变量覆盖） */
export const SESSION_COOKIE_NAME = SPRING_SESSION_COOKIE_NAME

/** API 中转层使用的服务端会话信息 */
export type ApiSession = {
  username: string
  /** Spring Session id（用于转发给后端的 Cookie 头） */
  springSessionId: string
  /** 后端在登录时签发的 CSRF token（用于转发给后端的 X-CSRF-TOKEN 头） */
  csrfToken?: string
  /** 后端在登录时返回的权限码 */
  permissions: string[]
}

/**
 * 读取当前请求的双会话（Better Auth 会话 + Spring Session cookie）。
 *
 * 口径（用户确认）：两者必须同时存在才算已登录，任一缺失返回 `null`。
 * - Better Auth 会话：`auth.api.getSession`，且 `user.token` 非空；
 * - Spring 会话：`<SPRING_SESSION_COOKIE_NAME>` cookie 非空。
 */
export async function getApiSession(
  request: NextRequest,
): Promise<ApiSession | null> {
  let session: Awaited<ReturnType<typeof auth.api.getSession>>
  try {
    session = await auth.api.getSession({ headers: request.headers })
  } catch {
    return null
  }

  if (!session) {
    return null
  }

  const token = (session.user as { token?: unknown }).token
  if (typeof token !== "string" || !token) {
    return null
  }

  const springSessionId = request.cookies.get(SESSION_COOKIE_NAME)?.value
  if (!springSessionId) {
    return null
  }

  const rawPermissions = (session.user as { permissions?: unknown }).permissions
  const permissions = Array.isArray(rawPermissions)
    ? rawPermissions.filter((value): value is string => typeof value === "string")
    : []

  const rawCsrfToken = (session.user as { csrfToken?: unknown }).csrfToken
  const csrfToken =
    typeof rawCsrfToken === "string" && rawCsrfToken ? rawCsrfToken : undefined

  return {
    username: session.user.name ?? session.user.email,
    springSessionId,
    csrfToken,
    permissions,
  }
}
