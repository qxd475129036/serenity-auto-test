import { createApiHandler } from "@/lib/api/proxy"
import { PERMISSIONS } from "@/lib/api/permissions"

/**
 * 后端 getData 接口的转发代理（已接入共通中转层）。
 *
 * 浏览器同源请求 POST /api/get-data → 中转层校验双会话与 `data:read` 权限 →
 * 携带 Spring Session cookie 转发到 `${THIRD_PARTY_API_URL}/api/getData`。
 *
 * 入参: JSON 对象（页面固定发送 `{ "lobCd": 10 }`），原样转发。
 * 成功: `{ data: <上游 JSON> }`
 * 失败: `{ error: { code, message } }`（401 未登录 / 403 无权限 / 400 参数错误 / 502 上游异常）
 */
export const POST = createApiHandler({
  upstreamPath: "/api/getData",
  permission: PERMISSIONS.DATA_READ,
  validateBody: (payload) =>
    typeof payload === "object" && payload !== null && !Array.isArray(payload)
      ? null
      : "リクエストボディは JSON オブジェクトである必要があります。",
})
