import type { Metadata } from "next"
import { PlaceholderPage } from "@/components/app/placeholder-page"

export const metadata: Metadata = {
  title: "取込状態管理",
}

export default function ImportStatusPage() {
  return (
    <PlaceholderPage
      title="取込状態管理"
      description="請求データの取込状況を確認します。"
    />
  )
}
