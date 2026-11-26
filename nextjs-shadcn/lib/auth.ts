import { APIError } from "@better-auth/core/error"
import { betterAuth } from "better-auth"
import { createAuthMiddleware } from "better-auth/api"
import { credentials } from "better-auth-credentials-plugin"

import { credentialsSchema } from "./auth-schema"
import {
  SPRING_SESSION_COOKIE_NAME,
  fetchCsrfToken,
  readCsrfToken,
  readSessionId,
} from "./spring-auth"

const thirdPartyApiUrl = process.env.THIRD_PARTY_API_URL?.replace(/\/+$/, "")
/** 登录后拉取当前用户权限码的后端接口（默认 /api/me） */
const permissionsApiPath =
  process.env.PERMISSIONS_API_PATH?.trim() || "/api/me"

/** 把字符串数组或 Spring `[{ authority }]` 形式统一成权限码数组。 */
function toStringArray(value: unknown): string[] | undefined {
  if (!Array.isArray(value)) {
    return undefined
  }
  const codes = value
    .map((item) => {
      if (typeof item === "string") {
        return item
      }
      if (
        item &&
        typeof item === "object" &&
        typeof (item as { authority?: unknown }).authority === "string"
      ) {
        return (item as { authority: string }).authority
      }
      return undefined
    })
    .filter((code): code is string => Boolean(code))

  return codes.length > 0 ? codes : undefined
}

/**
 * 从后端用户信息接口的响应中宽松提取权限码。
 *
 * 依次尝试：顶层字符串数组 → `permissions` → `authorities` → `roles`，
 * 以及一层 `{ data: {...} }` 包装（本项目统一响应包约定）。
 */
function readPermissionCodes(payload: unknown): string[] {
  const direct = toStringArray(payload)
  if (direct) {
    return direct
  }
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return []
  }

  const record = payload as Record<string, unknown>
  const candidates: Record<string, unknown>[] = [record]

  const nested = record.data
  if (nested && typeof nested === "object" && !Array.isArray(nested)) {
    candidates.push(nested as Record<string, unknown>)
  }

  for (const candidate of candidates) {
    for (const key of ["permissions", "authorities", "roles"]) {
      const codes = toStringArray(candidate[key])
      if (codes) {
        return codes
      }
    }
  }

  return []
}

/**
 * 登录成功后拉取当前用户权限码（供 API 中转层校验）。
 *
 * 接口路径由 `PERMISSIONS_API_PATH` 配置（默认 `/api/me`）。
 * 拉取失败不阻断登录，返回空数组（受权限保护的接口将返回 403，属预期）。
 */
async function fetchPermissions(
  baseUrl: string,
  path: string,
  sessionId: string,
): Promise<string[]> {
  try {
    const res = await fetch(`${baseUrl}${path}`, {
      headers: {
        Accept: "application/json",
        Cookie: `${SPRING_SESSION_COOKIE_NAME}=${sessionId}`,
      },
      cache: "no-store",
      signal: AbortSignal.timeout(3000),
    })
    if (!res.ok) {
      return []
    }
    return readPermissionCodes(await res.json())
  } catch {
    return []
  }
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
      permissions: {
        type: "string[]",
        required: false,
        returned: true,
      },
      csrfToken: {
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
          ctx.setCookie(SPRING_SESSION_COOKIE_NAME, token, {
            httpOnly: true,
            sameSite: "lax",
            path: "/",
            maxAge: 60 * 60 * 24 * 7,
          })
        }
      }
      if (ctx.path === "/sign-out") {
        ctx.setCookie(SPRING_SESSION_COOKIE_NAME, "", {
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
        let preLoginCsrfToken: string | undefined
        try {
          const loginPage = await fetch(`${thirdPartyApiUrl}/login`, {
            cache: "no-store",
          })
          preSessionId = readSessionId(loginPage.headers)
          preLoginCsrfToken = readCsrfToken(await loginPage.text())
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
          headers.Cookie = `${SPRING_SESSION_COOKIE_NAME}=${preSessionId}`
        }
        const body = new URLSearchParams({
          username: parsed.username,
          password: parsed.password,
        })
        if (preLoginCsrfToken) {
          body.set("_csrf", preLoginCsrfToken)
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
            // 认证成功后 Spring 会轮换 CSRF token，需用新会话重新取一次；
            // 取不到时回退登录页的旧 token（中转层遇到 403 还会再重取一次）。
            const [permissions, refreshedCsrfToken] = await Promise.all([
              fetchPermissions(
                thirdPartyApiUrl,
                permissionsApiPath,
                sessionId,
              ),
              fetchCsrfToken(thirdPartyApiUrl, sessionId),
            ])
            const csrfToken = refreshedCsrfToken ?? preLoginCsrfToken

            return {
              // Better Auth 内部用 email 作为用户唯一标识；无状态模式下存 username 即可。
              email: parsed.username,
              name: parsed.username,
              token: sessionId,
              permissions,
              ...(csrfToken ? { csrfToken } : {}),
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
