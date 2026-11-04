import type { Metadata } from "next"
import Link from "next/link"
import { Separator } from "@/components/ui/separator"
import { ModuleCard } from "@/components/app/module-card"
import { NAV_GROUPS } from "@/components/app/nav-config"

export const metadata: Metadata = {
  title: "ダッシュボード",
}

/**
 * 登录后工作台：按业务模块分组的功能入口。
 */
export default function HomePage() {
  return (
    <>
      <header className="space-y-1">
        <h1 className="font-heading text-2xl font-semibold tracking-tight">
          ダッシュボード
        </h1>
        <p className="text-sm text-muted-foreground">
          業務メニューから各機能へ移動できます。
        </p>
      </header>

      <div className="mt-8 space-y-8">
        {NAV_GROUPS.map((group) => (
          <section key={group.title} className="space-y-3">
            <div className="flex items-center gap-3">
              <h2 className="text-sm font-medium">{group.title}</h2>
              <Separator className="flex-1" />
            </div>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {group.items.map((item) => (
                <ModuleCard key={item.title} item={item} />
              ))}
            </div>
          </section>
        ))}
      </div>

      <footer className="mt-10 border-t pt-6">
        <Link
          href="/demo"
          className="text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
        >
          コンポーネント一覧（開発用）
        </Link>
      </footer>
    </>
  )
}
