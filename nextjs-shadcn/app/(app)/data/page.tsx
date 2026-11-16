import type { Metadata } from "next"
import { GetDataTable } from "./get-data-table"

export const metadata: Metadata = {
  title: "データ取得",
}

export default function GetDataPage() {
  return (
    <>
      <header className="mb-6 space-y-1">
        <h1 className="font-heading text-2xl font-semibold tracking-tight">
          データ取得
        </h1>
        <p className="text-sm text-muted-foreground">
          バックエンドの getData API（lobCd = 10）から取得したデータを表示します。
        </p>
      </header>
      <GetDataTable />
    </>
  )
}
