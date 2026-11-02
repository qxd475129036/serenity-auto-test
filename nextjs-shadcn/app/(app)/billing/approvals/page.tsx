import type { Metadata } from "next"
import { PlaceholderPage } from "@/components/app/placeholder-page"

export const metadata: Metadata = {
  title: "請求承認管理",
}

export default function ApprovalsPage() {
  return (
    <PlaceholderPage
      title="請求承認管理"
      description="請求内容の承認フローを管理します。"
    />
  )
}
