import type { Metadata } from "next"
import { PlaceholderPage } from "@/components/app/placeholder-page"

export const metadata: Metadata = {
  title: "計上管理",
}

export default function PostingsPage() {
  return (
    <PlaceholderPage
      title="計上管理"
      description="請求の計上処理を管理します。"
    />
  )
}
