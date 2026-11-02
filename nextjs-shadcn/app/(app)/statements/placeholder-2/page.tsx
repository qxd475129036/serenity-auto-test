import type { Metadata } from "next"
import { PlaceholderPage } from "@/components/app/placeholder-page"

export const metadata: Metadata = {
  title: "明細ダウンロード 占位ページ 2",
}

export default function StatementsPlaceholder2Page() {
  return (
    <PlaceholderPage
      title="明細ダウンロード 占位ページ 2"
      description="明細ダウンロードの占位ページ（2）です。"
    />
  )
}
