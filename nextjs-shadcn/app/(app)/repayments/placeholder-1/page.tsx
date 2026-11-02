import type { Metadata } from "next"
import { PlaceholderPage } from "@/components/app/placeholder-page"

export const metadata: Metadata = {
  title: "弁済業務 占位ページ 1",
}

export default function RepaymentsPlaceholder1Page() {
  return (
    <PlaceholderPage
      title="弁済業務 占位ページ 1"
      description="弁済業務管理の占位ページ（1）です。"
    />
  )
}
