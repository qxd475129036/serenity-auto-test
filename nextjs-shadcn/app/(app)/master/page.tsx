import { redirect } from "next/navigation"

/**
 * マスタ管理没有独立入口页，统一跳转到店舗管理。
 */
export default function MasterPage() {
  redirect("/master/shops")
}
