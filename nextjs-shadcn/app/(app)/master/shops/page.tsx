import type { Metadata } from "next"
import { ShopsTable } from "./shops-table"

export const metadata: Metadata = {
  title: "店舗管理",
}

export default function ShopsPage() {
  return (
    <div className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <header className="mb-6 space-y-1">
        <h1 className="font-heading text-2xl font-semibold tracking-tight">
          店舗管理
        </h1>
        <p className="text-sm text-muted-foreground">
          請求対象の店舗マスタを管理します。
        </p>
      </header>
      <ShopsTable />
    </div>
  )
}
