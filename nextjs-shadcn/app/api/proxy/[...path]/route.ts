import type { NextRequest } from "next/server"

import { UPSTREAM_PERMISSIONS } from "@/lib/api/permissions"
import { authorizeApiRequest, fail, handleRelay } from "@/lib/api/proxy"

type RouteContext = { params: Promise<{ path?: string[] }> }

/**
 * 通用后端中转：`/api/proxy/<path>` → `${THIRD_PARTY_API_URL}/api/<path>`。
 *
 * 与 `createApiHandler` 共用同一套鉴权与转发逻辑（双会话校验 + 权限校验 + 统一响应包）。
 * 权限按 `UPSTREAM_PERMISSIONS` 的「后端路径 → 权限码」映射判定，未登记则仅需登录。
 *
 * 例：`POST /api/proxy/getData` → `POST ${THIRD_PARTY_API_URL}/api/getData`
 */
async function handle(
  request: NextRequest,
  context: RouteContext,
): Promise<Response> {
  const { path } = await context.params

  if (!path || path.length === 0) {
    return fail("E_NOT_FOUND", "データが見つかりませんでした。", 404)
  }

  // 路径安全：拒绝空段、相对路径与反斜杠，避免越出 /api/ 前缀。
  if (
    path.some(
      (segment) =>
        !segment ||
        segment === "." ||
        segment === ".." ||
        segment.includes("\\"),
    )
  ) {
    return fail("E_NOT_FOUND", "データが見つかりませんでした。", 404)
  }

  const upstreamPath = `/api/${path.join("/")}`
  const auth = await authorizeApiRequest(
    request,
    UPSTREAM_PERMISSIONS[upstreamPath],
  )
  if (!auth.ok) {
    return auth.response
  }

  const method = request.method
  const bodyText =
    method === "GET" || method === "HEAD" ? undefined : await request.text()

  return handleRelay({
    request,
    upstreamPath,
    session: auth.session,
    bodyText,
  })
}

export const GET = handle
export const POST = handle
export const PUT = handle
export const PATCH = handle
export const DELETE = handle
