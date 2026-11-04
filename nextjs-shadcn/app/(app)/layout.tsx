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
      <main className="mx-auto flex-1 w-[80%] min-w-[1440px] px-4 py-8 sm:px-6 lg:px-8">
        {children}
      </main>
    </>
  )
}
