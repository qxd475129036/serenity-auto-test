"use client"

import type { ColumnDef } from "@tanstack/react-table"
import { Badge } from "@/components/ui/badge"
import { DataTable } from "@/components/app/data-table"
import {
  useAppTable,
  features,
  getPaginationInitialState,
  type TablePaginationConfig,
} from "@/components/app/use-table"

/** 単価マスタ */
type UnitPrice = {
  code: string // 単価コード
  serviceName: string // 業務名
  category: string // 分類
  price: number // 単価（円）
  unit: string // 単位
  validFrom: string // 適用開始日
  status: "active" | "inactive" // ステータス
}

/** ステータス表示マップ */
const STATUS_MAP: Record<
  UnitPrice["status"],
  { label: string; variant: "default" | "secondary" }
> = {
  active: { label: "有効", variant: "default" },
  inactive: { label: "無効", variant: "secondary" },
}

const columns: ColumnDef<typeof features, UnitPrice, unknown>[] = [
  {
    accessorKey: "code",
    header: "単価CD",
    enableSorting: true,
  },
  {
    accessorKey: "serviceName",
    header: "業務名",
    enableSorting: true,
  },
  {
    accessorKey: "category",
    header: "分類",
    enableSorting: true,
  },
  {
    accessorKey: "price",
    header: "単価（円）",
    enableSorting: true,
    cell: ({ row }) => (
      <span className="block text-right tabular-nums">
        {row.original.price.toLocaleString("ja-JP")}
      </span>
    ),
  },
  {
    accessorKey: "unit",
    header: "単位",
    enableSorting: false,
  },
  {
    accessorKey: "validFrom",
    header: "適用開始日",
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
]

/** モックデータ（18 件，5 件/页共 4 页） */
const MOCK_UNIT_PRICES: UnitPrice[] = [
  { code: "UP001", serviceName: "集荷作業", category: "物流", price: 1200, unit: "件", validFrom: "2026-04-01", status: "active" },
  { code: "UP002", serviceName: "配送作業", category: "物流", price: 1800, unit: "件", validFrom: "2026-04-01", status: "active" },
  { code: "UP003", serviceName: "代引手数料", category: "決済", price: 450, unit: "件", validFrom: "2026-04-01", status: "active" },
  { code: "UP004", serviceName: "返品処理", category: "物流", price: 900, unit: "件", validFrom: "2026-05-01", status: "active" },
  { code: "UP005", serviceName: "検品作業", category: "品質", price: 650, unit: "件", validFrom: "2026-05-01", status: "active" },
  { code: "UP006", serviceName: "梱包作業", category: "物流", price: 700, unit: "件", validFrom: "2026-06-01", status: "active" },
  { code: "UP007", serviceName: "保管料（日額）", category: "保管", price: 120, unit: "日", validFrom: "2026-06-01", status: "active" },
  { code: "UP008", serviceName: "冷蔵保管料", category: "保管", price: 240, unit: "日", validFrom: "2026-06-01", status: "inactive" },
  { code: "UP009", serviceName: "請求書発行", category: "事務", price: 300, unit: "通", validFrom: "2026-07-01", status: "active" },
  { code: "UP010", serviceName: "再発行手数料", category: "事務", price: 500, unit: "通", validFrom: "2026-07-01", status: "active" },
  { code: "UP011", serviceName: "システム連携", category: "システム", price: 2500, unit: "月", validFrom: "2026-07-01", status: "active" },
  { code: "UP012", serviceName: "データ出力", category: "システム", price: 800, unit: "回", validFrom: "2026-08-01", status: "active" },
  { code: "UP013", serviceName: "電話対応", category: "サポート", price: 600, unit: "件", validFrom: "2026-08-01", status: "inactive" },
  { code: "UP014", serviceName: "訪問対応", category: "サポート", price: 3500, unit: "回", validFrom: "2026-08-01", status: "active" },
  { code: "UP015", serviceName: "緊急対応", category: "サポート", price: 5200, unit: "回", validFrom: "2026-09-01", status: "active" },
  { code: "UP016", serviceName: "海外配送", category: "物流", price: 6800, unit: "件", validFrom: "2026-09-01", status: "active" },
  { code: "UP017", serviceName: "通関手続", category: "物流", price: 4200, unit: "件", validFrom: "2026-10-01", status: "active" },
  { code: "UP018", serviceName: "保険付加", category: "保険", price: 1500, unit: "件", validFrom: "2026-10-01", status: "inactive" },
]

export function UnitPricesTable({
  pagination,
}: {
  pagination?: TablePaginationConfig
}) {
  const table = useAppTable({
    key: "master-unit-prices",
    columns,
    data: MOCK_UNIT_PRICES,
    getRowId: (row) => row.code,
    initialState: { pagination: getPaginationInitialState(pagination) },
  })

  return <DataTable table={table} pagination={pagination} />
}
