import { redirect } from "next/navigation"

/**
 * 代引業務管理没有独立入口页，统一跳转到占位ページ 1。
 */
export default function CodPage() {
  redirect("/cod/placeholder-1")
}
