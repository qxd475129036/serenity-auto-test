import type { Metadata } from "next"
import { PlaceholderPage } from "@/components/app/placeholder-page"

export const metadata: Metadata = {
  title: "弁済業務 占位ページ 2",
}

export default function RepaymentsPlaceholder2Page() {
  return (
    <PlaceholderPage
      title="弁済業務 占位ページ 2"
      description="弁済業務管理の占位ページ（2）です。"
    />
  )
}
