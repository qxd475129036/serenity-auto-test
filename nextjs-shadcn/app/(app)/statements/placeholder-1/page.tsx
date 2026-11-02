import type { Metadata } from "next"
import { PlaceholderPage } from "@/components/app/placeholder-page"

export const metadata: Metadata = {
  title: "明細ダウンロード 占位ページ 1",
}

export default function StatementsPlaceholder1Page() {
  return (
    <PlaceholderPage
      title="明細ダウンロード 占位ページ 1"
      description="明細ダウンロードの占位ページ（1）です。"
    />
  )
}
