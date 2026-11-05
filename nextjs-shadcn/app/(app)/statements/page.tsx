import { redirect } from "next/navigation"

/**
 * 明細ダウンロード没有独立入口页，统一跳转到占位ページ 1。
 */
export default function StatementsPage() {
  redirect("/statements/placeholder-1")
}
