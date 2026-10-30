import { z } from "zod"

/**
 * 登录凭据 schema。
 *
 * 仅用于用户名/密码场景；email 字段被 Better Auth 内部用作用户唯一标识，
 * 但对外暴露的登录字段是 username（见 lib/auth.ts 中的 callback 映射）。
 *
 * 该文件不依赖 better-auth 服务端代码，可被服务端与客户端安全共享。
 */
export const credentialsSchema = z.object({
  username: z.string().min(1, "Username is required"),
  password: z.string().min(1, "Password is required"),
  rememberMe: z.boolean().optional(),
})

export type CredentialsInput = z.infer<typeof credentialsSchema>
