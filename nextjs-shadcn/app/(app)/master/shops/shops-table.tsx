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

/** 店舗マスタ */
type Shop = {
  code: string // 店舗コード
  name: string // 店舗名
  area: string // エリア
  manager: string // 担当者
  phone: string // TEL
  status: "active" | "closed" // ステータス
}

/** ステータス表示マップ */
const STATUS_MAP: Record<
  Shop["status"],
  { label: string; variant: "default" | "secondary" }
> = {
  active: { label: "営業中", variant: "default" },
  closed: { label: "閉鎖", variant: "secondary" },
}

/**
 * 单行 header —— 所有列平铺，不再使用 column group 嵌套。
 */
const columns: ColumnDef<typeof features, Shop, unknown>[] = [
  { accessorKey: "code", header: "コード", enableSorting: true },
  { accessorKey: "name", header: "店舗名", enableSorting: true },
  { accessorKey: "area", header: "エリア", enableSorting: true },
  { accessorKey: "manager", header: "担当者", enableSorting: true },
  { accessorKey: "phone", header: "TEL", enableSorting: false },
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

/** モックデータ（30 件，方便体验分页） */
const MOCK_SHOPS: Shop[] = [
  { code: "S001", name: "東京駅前店", area: "東京都", manager: "山田太郎", phone: "03-1111-2222", status: "active" },
  { code: "S002", name: "新宿西口店", area: "東京都", manager: "佐藤花子", phone: "03-3333-4444", status: "active" },
  { code: "S003", name: "渋谷ヒカリエ店", area: "東京都", manager: "鈴木一郎", phone: "03-5555-6666", status: "active" },
  { code: "S004", name: "池袋東口店", area: "東京都", manager: "高橋次郎", phone: "03-7777-8888", status: "closed" },
  { code: "S005", name: "横浜駅ビル店", area: "神奈川県", manager: "田中三郎", phone: "045-111-2222", status: "active" },
  { code: "S006", name: "川崎アゼリア店", area: "神奈川県", manager: "伊藤四郎", phone: "044-333-4444", status: "active" },
  { code: "S007", name: "大宮駅前店", area: "埼玉県", manager: "渡辺五郎", phone: "048-111-2222", status: "active" },
  { code: "S008", name: "浦和パルコ店", area: "埼玉県", manager: "中村六郎", phone: "048-333-4444", status: "closed" },
  { code: "S009", name: "千葉駅ビル店", area: "千葉県", manager: "小林七郎", phone: "043-111-2222", status: "active" },
  { code: "S010", name: "柏高島屋店", area: "千葉県", manager: "加藤八郎", phone: "04-7111-2222", status: "active" },
  { code: "S011", name: "大阪梅田店", area: "大阪府", manager: "松本九郎", phone: "06-1111-2222", status: "active" },
  { code: "S012", name: "難波デパート店", area: "大阪府", manager: "山本十郎", phone: "06-3333-4444", status: "active" },
  { code: "S013", name: "京都駅前店", area: "京都府", manager: "井上十一郎", phone: "075-111-2222", status: "active" },
  { code: "S014", name: "四条河原町店", area: "京都府", manager: "木村十二郎", phone: "075-333-4444", status: "closed" },
  { code: "S015", name: "神戸三宮店", area: "兵庫県", manager: "林十三郎", phone: "078-111-2222", status: "active" },
  { code: "S016", name: "福岡天神店", area: "福岡県", manager: "加藤十四郎", phone: "092-111-2222", status: "active" },
  { code: "S017", name: "博多駅ビル店", area: "福岡県", manager: "斎藤十五郎", phone: "092-333-4444", status: "active" },
  { code: "S018", name: "名古屋駅前店", area: "愛知県", manager: "清水十六郎", phone: "052-111-2222", status: "active" },
  { code: "S019", name: "栄オアシス店", area: "愛知県", manager: "森田十七郎", phone: "052-333-4444", status: "closed" },
  { code: "S020", name: "札幌駅前店", area: "北海道", manager: "遠藤十八郎", phone: "011-111-2222", status: "active" },
  { code: "S021", name: "仙台駅前店", area: "宮城県", manager: "内田十九郎", phone: "022-111-2222", status: "active" },
  { code: "S022", name: "盛岡駅前店", area: "岩手県", manager: "菅原二十郎", phone: "019-111-2222", status: "closed" },
  { code: "S023", name: "金沢駅前店", area: "石川県", manager: "松田二十一", phone: "076-111-2222", status: "active" },
  { code: "S024", name: "広島駅前店", area: "広島県", manager: "中島二十二", phone: "082-111-2222", status: "active" },
  { code: "S025", name: "松山駅前店", area: "愛媛県", manager: "古川二十三", phone: "089-111-2222", status: "active" },
  { code: "S026", name: "高知駅前店", area: "高知県", manager: "福本二十四", phone: "088-111-2222", status: "closed" },
  { code: "S027", name: "那覇空港店", area: "沖縄県", manager: "平良二十五", phone: "098-111-2222", status: "active" },
  { code: "S028", name: "旭川駅前店", area: "北海道", manager: "荒木二十六", phone: "0166-11-2222", status: "active" },
  { code: "S029", name: "新潟駅前店", area: "新潟県", manager: "五十嵐二十七", phone: "025-111-2222", status: "active" },
  { code: "S030", name: "宇都宮駅前店", area: "栃木県", manager: "大谷二十八", phone: "028-111-2222", status: "active" },
]

export function ShopsTable({
  pagination,
}: {
  pagination?: TablePaginationConfig
}) {
  // columns 是模块级常量，引用天然稳定，无需 useMemo
  const table = useAppTable({
    key: "master-shops",
    columns,
    data: MOCK_SHOPS,
    getRowId: (row) => row.code,
    initialState: { pagination: getPaginationInitialState(pagination) },
  })

  return <DataTable table={table} pagination={pagination} />
}
