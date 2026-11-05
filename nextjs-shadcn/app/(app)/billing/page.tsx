import { redirect } from "next/navigation"

/**
 * 請求業務管理没有独立入口页，统一跳转到取込状態管理。
 */
export default function BillingPage() {
  redirect("/billing/import-status")
}
