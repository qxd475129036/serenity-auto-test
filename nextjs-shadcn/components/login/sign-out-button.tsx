"use client"

import { useRouter } from "next/navigation"
import { LogOutIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { authClient } from "@/lib/auth-client"

/**
 * 首页登出入口。首页受 Proxy 登录守卫保护，渲染时必然已登录。
 */
export function SignOutButton() {
  const router = useRouter()

  async function handleSignOut() {
    await authClient.signOut()
    router.replace("/login")
  }

  return (
    <Button
      variant="outline"
      size="sm"
      aria-label="ログアウト"
      onClick={handleSignOut}
    >
      <LogOutIcon />
      ログアウト
    </Button>
  )
}
