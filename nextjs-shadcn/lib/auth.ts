import { APIError } from "@better-auth/core/error"
import { betterAuth } from "better-auth"
import { createAuthMiddleware } from "better-auth/api"
import { credentials } from "better-auth-credentials-plugin"

import { credentialsSchema } from "./auth-schema"

const thirdPartyApiUrl = process.env.THIRD_PARTY_API_URL?.replace(/\/+$/, "")
const springSessionCookieName =
  process.env.SPRING_SESSION_COOKIE_NAME?.trim() || "SESSION"

/**
 * 从响应头中读取 Spring Session 的 cookie 值（默认 cookie 名 SESSION / JSESSIONID）。
 *
 * 该 cookie 为 HttpOnly 且跨域，浏览器 JS 无法读取，只能由服务端在此解析。
 */
function readSessionId(headers: Headers): string | undefined {
  const cookie = headers
    .getSetCookie()
    .map((value) => value.split(";")[0]?.trim())
    .find((value) => value?.startsWith(`${springSessionCookieName}=`))

  return cookie?.slice(springSessionCookieName.length + 1) || undefined
}

/** 从登录页 HTML 中解析 Spring Security 的 CSRF hidden input 值（兼容两种属性顺序）。 */
function readCsrfToken(html: string): string | undefined {
  return (
    /name="_csrf"[^>]*value="([^"]+)"/.exec(html)?.[1] ??
    /value="([^"]+)"[^>]*name="_csrf"/.exec(html)?.[1]
  )
}

/**
 * Better Auth 服务端实例。
 *
 * 设计要点:
 * - 无状态模式（database: undefined）：用户身份由第三方 API 管理，本项目不持久化用户表，
 *   session 完全存储在签名 cookie 中（jwt）。
 * - 禁用内置 emailAndPassword，改用 credentials-plugin 把用户名/密码转发给 Spring Boot 校验。
 * - 第三方 sessionId 存入 user.additionalFields.token，并在登录成功后由 hooks.after
 *   额外种一个独立的 HttpOnly cookie（名同 SPRING_SESSION_COOKIE_NAME），便于浏览器侧
 *   可见与后续服务端代理携带。
 *
 * 本文件仅供服务端使用；客户端请从 lib/auth-client.ts 引入 authClient。
 */
export const auth = betterAuth({
  database: undefined,
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
  emailAndPassword: {
    enabled: false,
  },
  session: {
    cookieCache: {
      enabled: true,
      strategy: "jwt",
    },
  },
  user: {
    additionalFields: {
      token: {
        type: "string",
        required: false,
        returned: true,
      },
    },
  },
  hooks: {
    after: createAuthMiddleware(async (ctx) => {
      if (ctx.path === "/sign-in/credentials") {
        const token = (ctx.context.newSession?.user as { token?: unknown } | undefined)
          ?.token
        if (typeof token === "string" && token) {
          ctx.setCookie(springSessionCookieName, token, {
            httpOnly: true,
            sameSite: "lax",
            path: "/",
            maxAge: 60 * 60 * 24 * 7,
          })
        }
      }
      if (ctx.path === "/sign-out") {
        ctx.setCookie(springSessionCookieName, "", {
          httpOnly: true,
          path: "/",
          maxAge: 0,
        })
      }
    }),
  },
  plugins: [
    credentials({
      autoSignUp: true,
      inputSchema: credentialsSchema,
      async callback(_ctx, parsed) {
        if (!thirdPartyApiUrl) {
          throw new APIError("INTERNAL_SERVER_ERROR", {
            code: "E_INTERNAL",
            message: "THIRD_PARTY_API_URL is not configured",
          })
        }

        // Step 1: GET /login 建立会话并取 CSRF token（后端未开 CSRF 时解析不到则跳过）。
        let preSessionId: string | undefined
        let csrfToken: string | undefined
        try {
          const loginPage = await fetch(`${thirdPartyApiUrl}/login`, {
            cache: "no-store",
          })
          preSessionId = readSessionId(loginPage.headers)
          csrfToken = readCsrfToken(await loginPage.text())
        } catch {
          throw new APIError("BAD_GATEWAY", {
            code: "E_INTERNAL",
            message: "Auth provider is unreachable",
          })
        }

        // Step 2: POST /login 携带同会话 cookie 与 _csrf（如有）。
        const headers: Record<string, string> = {
          "Content-Type": "application/x-www-form-urlencoded",
        }
        if (preSessionId) {
          headers.Cookie = `${springSessionCookieName}=${preSessionId}`
        }
        const body = new URLSearchParams({
          username: parsed.username,
          password: parsed.password,
        })
        if (csrfToken) {
          body.set("_csrf", csrfToken)
        }

        let res: Response
        try {
          res = await fetch(`${thirdPartyApiUrl}/login`, {
            method: "POST",
            headers,
            body,
            redirect: "manual",
            cache: "no-store",
          })
        } catch {
          throw new APIError("BAD_GATEWAY", {
            code: "E_INTERNAL",
            message: "Auth provider is unreachable",
          })
        }

        const location = res.headers.get("location") ?? ""
        const isRedirect = res.status >= 300 && res.status < 400
        const rejectedByRedirect = /[?&]error(?:=|&|$)/.test(location)

        if (isRedirect && !rejectedByRedirect) {
          // 认证成功后 Spring 默认轮换 session id（session fixation 保护），
          // 优先取 POST 响应里的新 id，无则回退到 GET 阶段的 id。
          const sessionId = readSessionId(res.headers) ?? preSessionId
          if (sessionId) {
            return {
              // Better Auth 内部用 email 作为用户唯一标识；无状态模式下存 username 即可。
              email: parsed.username,
              name: parsed.username,
              token: sessionId,
            }
          }
        }

        // 凭据错误：重定向到 ?error、返回 401，或直接返回登录页 HTML（200）。
        if (rejectedByRedirect || res.status === 401 || res.status === 200) {
          throw new APIError("UNAUTHORIZED", {
            code: "E_UNAUTHORIZED",
            message: "Invalid username or password",
          })
        }

        // 403 及其他异常（如 CSRF 流程失败）一律视为上游流程异常，绝不能误判为成功。
        throw new APIError("BAD_GATEWAY", {
          code: "E_INTERNAL",
          message: "Malformed response from auth provider",
        })
      },
    }),
  ],
})

export type Auth = typeof auth
