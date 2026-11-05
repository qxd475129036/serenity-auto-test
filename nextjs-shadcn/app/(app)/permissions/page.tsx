import { redirect } from "next/navigation"

/**
 * 権限（ユーザー）管理没有独立入口页，统一跳转到ユーザー管理。
 */
export default function PermissionsPage() {
  redirect("/permissions/users")
}
