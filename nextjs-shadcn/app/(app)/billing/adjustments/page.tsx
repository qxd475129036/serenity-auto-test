import type { Metadata } from "next"
import { PlaceholderPage } from "@/components/app/placeholder-page"

export const metadata: Metadata = {
  title: "調整管理",
}

export default function AdjustmentsPage() {
  return (
    <PlaceholderPage
      title="調整管理"
      description="請求金額の調整を管理します。"
    />
  )
}
