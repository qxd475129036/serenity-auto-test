import type { Metadata } from "next"
import type { TablePaginationConfig } from "@/components/app/use-table"
import { UnitPricesTable } from "./unit-prices-table"

export const metadata: Metadata = {
  title: "単価管理",
}

/** 页面级分页配置：本页演示 5 件/页与自定义选项 */
const PAGINATION: TablePaginationConfig = {
  pageSize: 5,
  pageSizeOptions: [5, 10, 20],
}

export default function UnitPricesPage() {
  return (
    <>
      <header className="mb-6 space-y-1">
        <h1 className="font-heading text-2xl font-semibold tracking-tight">
          単価管理
        </h1>
        <p className="text-sm text-muted-foreground">
          業務ごとの単価マスタを管理します。表示件数はページ側の設定で切り替わります。
        </p>
      </header>
      <UnitPricesTable pagination={PAGINATION} />
    </>
  )
}
