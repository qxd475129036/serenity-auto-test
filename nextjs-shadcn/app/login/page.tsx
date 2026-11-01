"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useState, type SyntheticEvent } from "react"
import { toast } from "sonner"
import {
  ArrowLeftIcon,
  EyeIcon,
  EyeOffIcon,
  LockIcon,
  LogOutIcon,
  RabbitIcon,
  UserIcon,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { DirectionProvider } from "@/components/ui/direction"
import {
  Field,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field"
import {
  InputGroup,
  InputGroupAddon,
  InputGroupButton,
  InputGroupInput,
} from "@/components/ui/input-group"
import { Label } from "@/components/ui/label"
import { Spinner } from "@/components/ui/spinner"
import { Toaster } from "@/components/ui/sonner"

import { authClient } from "@/lib/auth-client"

const SYSTEM_NAME = "rabbit"
const SYSTEM_NAME_JA = "社内申請システム"

function localizeAuthError(message: string): string {
  if (message.includes("Invalid username or password")) {
    return "ユーザー名またはパスワードが正しくありません。"
  }
  return message
}

function BrandMark({ className }: { className?: string }) {
  return (
    <div className={cn("flex items-center gap-2.5", className)}>
      <span className="flex size-9 items-center justify-center rounded-lg bg-primary-foreground/10">
        <RabbitIcon className="size-5" />
      </span>
      <span className="font-heading text-lg font-semibold tracking-tight">
        {SYSTEM_NAME}
      </span>
    </div>
  )
}

export default function LoginPage() {
  const router = useRouter()
  const { data: session, isPending: sessionPending } = authClient.useSession()
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [remember, setRemember] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const disabled = submitting || sessionPending

  async function handleSubmit(e: SyntheticEvent<HTMLFormElement>) {
    e.preventDefault()
    if (!username.trim() || !password) {
      toast.error("ユーザー名とパスワードを入力してください。")
      return
    }

    setSubmitting(true)
    try {
      const result = await authClient.signIn.credentials({
        username: username.trim(),
        password,
        rememberMe: remember,
      })

      if (result.error) {
        toast.error(
          localizeAuthError(result.error.message ?? "ログインに失敗しました。")
        )
        return
      }

      toast.success("ログインしました。")
      router.refresh()
    } catch (err) {
      const message = err instanceof Error ? err.message : "ログインに失敗しました。"
      toast.error(localizeAuthError(message))
    } finally {
      setSubmitting(false)
    }
  }

  async function handleSignOut() {
    await authClient.signOut()
    toast.success("ログアウトしました。")
    router.refresh()
  }

  const user = session?.user

  return (
    <DirectionProvider dir="ltr">
      <Toaster />
      <div lang="ja" className="flex min-h-dvh bg-background text-foreground">
        {/* Brand panel (desktop) */}
        <aside className="hidden w-[42%] max-w-2xl flex-col justify-between gap-10 bg-primary p-10 text-primary-foreground lg:flex">
          <BrandMark />
          <div>
            <p className="text-sm font-medium text-primary-foreground/60">
              {SYSTEM_NAME_JA}
            </p>
            <h2 className="mt-2 font-heading text-3xl leading-tight font-semibold tracking-tight">
              申請から承認まで、ひとつの窓口。
            </h2>
            <p className="mt-4 max-w-sm text-sm leading-relaxed text-primary-foreground/70">
              社内申請、承認フロー、進捗確認を {SYSTEM_NAME} でまとめて管理できます。
            </p>
          </div>
          <p className="text-xs text-primary-foreground/50">
            © 2026 {SYSTEM_NAME} — 社内利用専用システム
          </p>
        </aside>

        {/* Form side */}
        <main className="flex min-w-0 flex-1 flex-col">
          <h1 className="sr-only">
            {`${SYSTEM_NAME} ${SYSTEM_NAME_JA} - ログイン`}
          </h1>
          <div className="flex items-center gap-2 px-6 pt-5">
            <Link href="/">
              <Button
                variant="ghost"
                size="icon-sm"
                aria-label="トップページへ戻る"
              >
                <ArrowLeftIcon />
              </Button>
            </Link>
            {/* Compact wordmark (mobile / tablet) */}
            <span className="flex items-center gap-2 lg:hidden">
              <RabbitIcon className="size-5" />
              <span className="text-sm font-semibold tracking-tight">
                {SYSTEM_NAME}
              </span>
            </span>
          </div>

          <div className="flex flex-1 items-center justify-center px-6 py-10">
            <div className="w-full max-w-sm">
              {user ? (
                <Card>
                  <CardHeader>
                    <CardTitle>ログイン済み</CardTitle>
                    <CardDescription>
                      認証に成功しました。現在のセッション情報を表示しています。
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-1 text-sm">
                      <div className="text-muted-foreground">ユーザー名</div>
                      <div className="font-medium">
                        {user.name ?? user.email}
                      </div>
                    </div>
                    <div className="space-y-1 text-sm">
                      <div className="text-muted-foreground">Token</div>
                      <div className="break-all font-mono text-xs">
                        {user.token ?? "—"}
                      </div>
                    </div>
                    <Button
                      type="button"
                      variant="outline"
                      className="w-full"
                      onClick={handleSignOut}
                    >
                      <LogOutIcon />
                      ログアウト
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <Card>
                  <CardHeader>
                    <CardTitle>ログイン</CardTitle>
                    <CardDescription>
                      会社アカウントでサインインしてください。
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={handleSubmit} className="space-y-4">
                      <Field>
                        <FieldLabel htmlFor="username">ユーザー名</FieldLabel>
                        <FieldGroup>
                          <InputGroup className="w-full">
                            <InputGroupAddon>
                              <UserIcon className="size-4 opacity-50" />
                            </InputGroupAddon>
                            <InputGroupInput
                              id="username"
                              type="text"
                              autoComplete="username"
                              placeholder="ユーザー名"
                              value={username}
                              onChange={(e) => setUsername(e.target.value)}
                              disabled={disabled}
                            />
                          </InputGroup>
                        </FieldGroup>
                      </Field>
                      <Field>
                        <FieldLabel htmlFor="password">パスワード</FieldLabel>
                        <FieldGroup>
                          <InputGroup className="w-full">
                            <InputGroupAddon>
                              <LockIcon className="size-4 opacity-50" />
                            </InputGroupAddon>
                            <InputGroupInput
                              id="password"
                              type={showPassword ? "text" : "password"}
                              autoComplete="current-password"
                              placeholder="パスワード"
                              value={password}
                              onChange={(e) => setPassword(e.target.value)}
                              disabled={disabled}
                            />
                            <InputGroupAddon align="inline-end">
                              <InputGroupButton
                                type="button"
                                aria-label={
                                  showPassword
                                    ? "パスワードを非表示にする"
                                    : "パスワードを表示する"
                                }
                                aria-pressed={showPassword}
                                onClick={() => setShowPassword((v) => !v)}
                                disabled={disabled}
                              >
                                {showPassword ? (
                                  <EyeOffIcon className="size-4" />
                                ) : (
                                  <EyeIcon className="size-4" />
                                )}
                              </InputGroupButton>
                            </InputGroupAddon>
                          </InputGroup>
                        </FieldGroup>
                      </Field>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Checkbox
                            id="remember"
                            checked={remember}
                            onCheckedChange={(checked) =>
                              setRemember(checked === true)
                            }
                            disabled={disabled}
                          />
                          <Label htmlFor="remember" className="text-sm">
                            ログイン状態を保持
                          </Label>
                        </div>
                        <Button
                          type="button"
                          variant="link"
                          size="sm"
                          className="h-auto p-0 text-sm"
                          disabled={disabled}
                        >
                          パスワードをお忘れですか？
                        </Button>
                      </div>
                      <Button
                        type="submit"
                        size="lg"
                        className="w-full"
                        disabled={disabled}
                      >
                        {submitting ? (
                          <>
                            <Spinner className="size-4" />
                            ログイン中…
                          </>
                        ) : (
                          "ログイン"
                        )}
                      </Button>
                    </form>
                  </CardContent>
                </Card>
              )}

              {!user && (
                <p className="mt-6 text-center text-xs text-muted-foreground">
                  テスト用（モーク API）：ユーザー名 <code>admin</code>／パスワード{" "}
                  <code>password</code>
                </p>
              )}
            </div>
          </div>
        </main>
      </div>
    </DirectionProvider>
  )
}
