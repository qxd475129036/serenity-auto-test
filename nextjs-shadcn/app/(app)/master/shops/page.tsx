import type { Metadata } from "next"
import type { TablePaginationConfig } from "@/components/app/use-table"
import { ShopsTable } from "./shops-table"

export const metadata: Metadata = {
  title: "店舗管理",
}

/** 页面级分页配置 */
const PAGINATION: TablePaginationConfig = {
  pageSize: 10,
  pageSizeOptions: [10, 20, 50],
}

export default function ShopsPage() {
  return (
    <>
      <header className="mb-6 space-y-1">
        <h1 className="font-heading text-2xl font-semibold tracking-tight">
          店舗管理
        </h1>
        <p className="text-sm text-muted-foreground">
          請求対象の店舗マスタを管理します。
        </p>
      </header>
      <ShopsTable pagination={PAGINATION} />
    </>
  )
}
