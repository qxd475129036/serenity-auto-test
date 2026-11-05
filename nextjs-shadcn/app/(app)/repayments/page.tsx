import { redirect } from "next/navigation"

/**
 * 弁済業務管理没有独立入口页，统一跳转到占位ページ 1。
 */
export default function RepaymentsPage() {
  redirect("/repayments/placeholder-1")
}
