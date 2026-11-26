/**
 * Spring Security 认证相关的共享常量与解析工具（登录流程与 API 中转层共用）。
 */

/** Spring Session cookie 名（后端使用 JSESSIONID 时由环境变量覆盖） */
export const SPRING_SESSION_COOKIE_NAME =
  process.env.SPRING_SESSION_COOKIE_NAME?.trim() || "SESSION"

/** 后端校验 CSRF 的请求头名（Spring Security 默认 X-CSRF-TOKEN） */
export const CSRF_HEADER_NAME = "X-CSRF-TOKEN"

/**
 * 从响应头中读取 Spring Session 的 cookie 值。
 *
 * 该 cookie 为 HttpOnly 且跨域，浏览器 JS 无法读取，只能由服务端在此解析。
 */
export function readSessionId(headers: Headers): string | undefined {
  const cookie = headers
    .getSetCookie()
    .map((value) => value.split(";")[0]?.trim())
    .find((value) => value?.startsWith(`${SPRING_SESSION_COOKIE_NAME}=`))

  return cookie?.slice(SPRING_SESSION_COOKIE_NAME.length + 1) || undefined
}

/** 从登录页 HTML 中解析 Spring Security 的 CSRF hidden input 值（兼容两种属性顺序）。 */
export function readCsrfToken(html: string): string | undefined {
  return (
    /name="_csrf"[^>]*value="([^"]+)"/.exec(html)?.[1] ??
    /value="([^"]+)"[^>]*name="_csrf"/.exec(html)?.[1]
  )
}

/**
 * 用当前已认证会话重新获取 CSRF token。
 *
 * Spring Security 在认证成功后会轮换 CSRF token，登录页拿到的旧 token 随即失效；
 * 因此携带当前 sessionId 请求登录页（已登录时可能被重定向到首页），从返回 HTML 的
 * `_csrf` hidden input 读取当前会话的有效 token。获取失败返回 `undefined`。
 */
export async function fetchCsrfToken(
  baseUrl: string,
  sessionId: string,
): Promise<string | undefined> {
  try {
    const res = await fetch(`${baseUrl}/login`, {
      headers: {
        Accept: "text/html",
        Cookie: `${SPRING_SESSION_COOKIE_NAME}=${sessionId}`,
      },
      cache: "no-store",
      signal: AbortSignal.timeout(3000),
    })
    if (!res.ok) {
      return undefined
    }
    return readCsrfToken(await res.text())
  } catch {
    return undefined
  }
}
