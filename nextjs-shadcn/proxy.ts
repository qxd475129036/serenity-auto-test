import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"
import { getSessionCookie } from "better-auth/cookies"

const PUBLIC_PATHS = ["/login"]

/**
 * 路由守卫（Next.js 16 的 Proxy，替代 middleware）。
 *
 * - 公开路由: `/login` 与 `/api/**`（后者由 matcher 排除）。
 * - 未登录访问受保护页面 → 重定向 `/login?next=<原路径+query>`。
 * - 仅做登录态存在性判断（乐观检查），完整校验由 Better Auth 端点负责。
 */
export function proxy(request: NextRequest) {
  const { pathname, search } = request.nextUrl

  if (
    PUBLIC_PATHS.some(
      (path) => pathname === path || pathname.startsWith(`${path}/`)
    )
  ) {
    return NextResponse.next()
  }

  if (!getSessionCookie(request)) {
    const loginUrl = new URL("/login", request.url)
    const target = `${pathname}${search}`
    if (target !== "/") {
      loginUrl.searchParams.set("next", target)
    }
    return NextResponse.redirect(loginUrl)
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    // 排除 API、Next 静态资源/图片、favicon 与 public 下的静态文件
    "/((?!api|_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico|txt|xml|woff2?)$).*)",
  ],
}
