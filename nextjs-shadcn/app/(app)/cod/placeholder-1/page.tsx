import type { Metadata } from "next"
import { PlaceholderPage } from "@/components/app/placeholder-page"

export const metadata: Metadata = {
  title: "代引業務 占位ページ 1",
}

export default function CodPlaceholder1Page() {
  return (
    <PlaceholderPage
      title="代引業務 占位ページ 1"
      description="代引業務管理の占位ページ（1）です。"
    />
  )
}
