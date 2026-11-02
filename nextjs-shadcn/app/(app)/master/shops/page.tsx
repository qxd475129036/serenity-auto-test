import type { Metadata } from "next"
import { PlaceholderPage } from "@/components/app/placeholder-page"

export const metadata: Metadata = {
  title: "店舗管理",
}

export default function ShopsPage() {
  return (
    <PlaceholderPage
      title="店舗管理"
      description="請求対象の店舗マスタを管理します。"
    />
  )
}
