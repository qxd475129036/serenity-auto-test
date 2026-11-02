import type { Metadata } from "next"
import { PlaceholderPage } from "@/components/app/placeholder-page"

export const metadata: Metadata = {
  title: "ロール管理",
}

export default function RolesPage() {
  return (
    <PlaceholderPage
      title="ロール管理"
      description="ロールと権限の割り当てを管理します。"
    />
  )
}
