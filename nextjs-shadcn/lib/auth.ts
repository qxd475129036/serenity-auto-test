import { APIError } from "@better-auth/core/error"
import { betterAuth } from "better-auth"
import { credentials } from "better-auth-credentials-plugin"

import { credentialsSchema } from "./auth-schema"

const thirdPartyApiUrl = process.env.THIRD_PARTY_API_URL

/**
 * Better Auth 服务端实例。
 *
 * 设计要点:
 * - 无状态模式（database: undefined）：用户身份由第三方 API 管理，本项目不持久化用户表，
 *   session 完全存储在签名 cookie 中（jwt）。
 * - 禁用内置 emailAndPassword，改用 credentials-plugin 把用户名/密码转发给第三方 API 校验。
 * - 第三方 token 存入 user.additionalFields.token，随 session cookie 返回给前端，
 *   便于后续调用第三方受保护接口。
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

        const res = await fetch(`${thirdPartyApiUrl}/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: parsed.username,
            password: parsed.password,
          }),
        })

        if (!res.ok) {
          throw new APIError("UNAUTHORIZED", {
            code: "E_UNAUTHORIZED",
            message: "Invalid username or password",
          })
        }

        const json = (await res.json()) as {
          data?: { token: string; user: { username: string; name?: string } }
        }
        const data = json.data

        if (!data) {
          throw new APIError("BAD_GATEWAY", {
            code: "E_INTERNAL",
            message: "Malformed response from auth provider",
          })
        }

        return {
          // Better Auth 内部用 email 作为用户唯一标识；无状态模式下存 username 即可。
          email: parsed.username,
          name: data.user.name ?? parsed.username,
          token: data.token,
        }
      },
    }),
  ],
})

export type Auth = typeof auth
