"use client"

import type { ColumnDef } from "@tanstack/react-table"
import { Badge } from "@/components/ui/badge"
import { DataTable } from "@/components/app/data-table"
import { createSelectionColumn } from "@/components/app/table-selection-column"
import {
  useAppTable,
  features,
  getPaginationInitialState,
  type TablePaginationConfig,
} from "@/components/app/use-table"

/** 請求CDマスタ */
type BillingCode = {
  code: string // 請求コード
  name: string // 請求コード名
  category: string // 分類
  status: "active" | "inactive" // ステータス
  updatedAt: string // 更新日
}

/** ステータス表示マップ */
const STATUS_MAP: Record<
  BillingCode["status"],
  { label: string; variant: "default" | "secondary" }
> = {
  active: { label: "有効", variant: "default" },
  inactive: { label: "無効", variant: "secondary" },
}

/**
 * 列定义：首列为行选择复选框（createSelectionColumn）。
 */
const columns: ColumnDef<typeof features, BillingCode, unknown>[] = [
  createSelectionColumn<BillingCode>(),
  {
    accessorKey: "code",
    header: "請求CD",
    enableSorting: true,
  },
  {
    accessorKey: "name",
    header: "請求CD名",
    enableSorting: true,
  },
  {
    accessorKey: "category",
    header: "分類",
    enableSorting: true,
  },
  {
    accessorKey: "status",
    header: "ステータス",
    enableSorting: true,
    cell: ({ row }) => {
      const info = STATUS_MAP[row.original.status]
      return <Badge variant={info.variant}>{info.label}</Badge>
    },
  },
  {
    accessorKey: "updatedAt",
    header: "更新日",
    enableSorting: true,
  },
]

/** モックデータ（24 件，不分页一次显示） */
const MOCK_BILLING_CODES: BillingCode[] = [
  { code: "BC001", name: "定期請求（月次）", category: "定期", status: "active", updatedAt: "2026-10-01" },
  { code: "BC002", name: "定期請求（隔月）", category: "定期", status: "active", updatedAt: "2026-09-15" },
  { code: "BC003", name: "スポット請求", category: "都度", status: "active", updatedAt: "2026-10-20" },
  { code: "BC004", name: "立替金精算", category: "精算", status: "active", updatedAt: "2026-10-05" },
  { code: "BC005", name: "代引手数料", category: "手数料", status: "active", updatedAt: "2026-08-30" },
  { code: "BC006", name: "送料請求", category: "運送", status: "active", updatedAt: "2026-09-01" },
  { code: "BC007", name: "包装資材費", category: "資材", status: "inactive", updatedAt: "2026-07-12" },
  { code: "BC008", name: "システム利用料", category: "システム", status: "active", updatedAt: "2026-10-10" },
  { code: "BC009", name: "保守サポート費", category: "サービス", status: "active", updatedAt: "2026-09-20" },
  { code: "BC010", name: "印刷手数料", category: "手数料", status: "active", updatedAt: "2026-10-18" },
  { code: "BC011", name: "返金調整", category: "調整", status: "active", updatedAt: "2026-10-22" },
  { code: "BC012", name: "値引調整", category: "調整", status: "inactive", updatedAt: "2026-06-05" },
  { code: "BC013", name: "請求書再発行手数料", category: "手数料", status: "active", updatedAt: "2026-10-25" },
  { code: "BC014", name: "延滞利息", category: "利息", status: "active", updatedAt: "2026-09-10" },
  { code: "BC015", name: "前受金充当", category: "精算", status: "active", updatedAt: "2026-10-08" },
  { code: "BC016", name: "保証金返還", category: "精算", status: "inactive", updatedAt: "2026-05-30" },
  { code: "BC017", name: "オプション利用料", category: "サービス", status: "active", updatedAt: "2026-10-12" },
  { code: "BC018", name: "配送代行手数料", category: "運送", status: "active", updatedAt: "2026-09-28" },
  { code: "BC019", name: "倉庫保管料", category: "保管", status: "active", updatedAt: "2026-10-15" },
  { code: "BC020", name: "検品手数料", category: "手数料", status: "active", updatedAt: "2026-09-25" },
  { code: "BC021", name: "特別割引", category: "調整", status: "inactive", updatedAt: "2026-04-18" },
  { code: "BC022", name: "法人向け請求", category: "定期", status: "active", updatedAt: "2026-10-28" },
  { code: "BC023", name: "個人向け請求", category: "都度", status: "active", updatedAt: "2026-10-03" },
  { code: "BC024", name: "海外送金手数料", category: "手数料", status: "active", updatedAt: "2026-09-05" },
]

export function BillingCodesTable({
  pagination,
}: {
  pagination?: TablePaginationConfig
}) {
  const table = useAppTable({
    key: "master-billing-codes",
    columns,
    data: MOCK_BILLING_CODES,
    enableRowSelection: true,
    getRowId: (row) => row.code,
    initialState: { pagination: getPaginationInitialState(pagination) },
  })

  return (
    <DataTable
      table={table}
      pagination={pagination}
      enableRowSelection
    />
  )
}
