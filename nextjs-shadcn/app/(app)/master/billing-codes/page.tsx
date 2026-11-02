import type { Metadata } from "next"
import { PlaceholderPage } from "@/components/app/placeholder-page"

export const metadata: Metadata = {
  title: "請求CD管理",
}

export default function BillingCodesPage() {
  return (
    <PlaceholderPage
      title="請求CD管理"
      description="請求コードの定義と割り当てを管理します。"
    />
  )
}
