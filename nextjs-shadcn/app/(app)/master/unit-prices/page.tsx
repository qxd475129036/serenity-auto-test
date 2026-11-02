import type { Metadata } from "next"
import { PlaceholderPage } from "@/components/app/placeholder-page"

export const metadata: Metadata = {
  title: "単価管理",
}

export default function UnitPricesPage() {
  return (
    <PlaceholderPage
      title="単価管理"
      description="業務ごとの単価マスタを管理します。"
    />
  )
}
