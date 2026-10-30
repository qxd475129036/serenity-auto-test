import { toNextJsHandler } from "better-auth/next-js"

import { auth } from "@/lib/auth"

/**
 * Better Auth 全量 API 入口。
 * 由 toNextJsHandler 把 auth 实例适配为 Next.js App Router 的 GET/POST。
 * 路径由 lib/auth.ts 中 basePath 决定（默认 /api/auth）。
 */
export const { GET, POST } = toNextJsHandler(auth)
