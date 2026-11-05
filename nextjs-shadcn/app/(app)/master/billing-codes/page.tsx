import type { Metadata } from "next"
import type { TablePaginationConfig } from "@/components/app/use-table"
import { BillingCodesTable } from "./billing-codes-table"

export const metadata: Metadata = {
  title: "請求CD管理",
}

/** 页面级分页配置：本页取消分页，一次显示全部数据 */
const PAGINATION: TablePaginationConfig = {
  enabled: false,
}

export default function BillingCodesPage() {
  return (
    <>
      <header className="mb-6 space-y-1">
        <h1 className="font-heading text-2xl font-semibold tracking-tight">
          請求CD管理
        </h1>
        <p className="text-sm text-muted-foreground">
          請求コードの定義と割り当てを管理します。行の選択に対応しています。
        </p>
      </header>
      <BillingCodesTable pagination={PAGINATION} />
    </>
  )
}
