import type { Metadata } from "next"
import { PlaceholderPage } from "@/components/app/placeholder-page"

export const metadata: Metadata = {
  title: "ユーザー管理",
}

export default function UsersPage() {
  return (
    <PlaceholderPage
      title="ユーザー管理"
      description="社内ユーザーの登録・編集・無効化を行います。"
    />
  )
}
