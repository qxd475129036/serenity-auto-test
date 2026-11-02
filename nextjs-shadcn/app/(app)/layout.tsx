import type { ReactNode } from "react"
import { AppHeader } from "@/components/app/app-header"

/**
 * 登录后业务系统的路由组布局：顶部导航 + 内容区。
 * 路由组不参与 URL，首页仍为 `/`。
 */
export default function AppLayout({ children }: { children: ReactNode }) {
  return (
    <>
      <AppHeader />
      <main className="flex-1">{children}</main>
    </>
  )
}
