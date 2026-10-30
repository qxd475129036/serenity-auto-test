import { createAuthClient } from "better-auth/react"
import { inferAdditionalFields } from "better-auth/client/plugins"
import type { User } from "better-auth"
import { credentialsClient } from "better-auth-credentials-plugin/client"

import type { Auth } from "./auth"
import { credentialsSchema } from "./auth-schema"

/**
 * Better Auth 客户端实例。
 *
 * - credentialsClient 注册用户名/密码登录端点（路径与服务端一致: /sign-in/credentials）。
 * - inferAdditionalFields 让 session.user 上能拿到服务端定义的 token 额外字段。
 *
 * 仅在客户端使用；服务端请从 lib/auth.ts 引入 auth。
 */
export const authClient = createAuthClient({
  plugins: [
    credentialsClient<
      User & { token?: string },
      "/sign-in/credentials",
      typeof credentialsSchema
    >(),
    inferAdditionalFields<Auth>(),
  ],
})
