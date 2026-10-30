"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useState, type SyntheticEvent } from "react"
import { toast } from "sonner"
import { ArrowLeftIcon, LockIcon, LogOutIcon, UserIcon } from "lucide-react"
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
  InputGroupInput,
} from "@/components/ui/input-group"
import { Label } from "@/components/ui/label"
import { Toaster } from "@/components/ui/sonner"

import { authClient } from "@/lib/auth-client"

export default function LoginPage() {
  const router = useRouter()
  const { data: session, isPending: sessionPending } = authClient.useSession()
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [remember, setRemember] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e: SyntheticEvent<HTMLFormElement>) {
    e.preventDefault()
    if (!username.trim() || !password) {
      toast.error("Please enter your username and password.")
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
        toast.error(result.error.message || "Sign in failed.")
        return
      }

      toast.success(`Signed in as ${result.data?.user?.name ?? username.trim()}`)
      router.refresh()
    } catch (err) {
      const message = err instanceof Error ? err.message : "Sign in failed."
      toast.error(message)
    } finally {
      setSubmitting(false)
    }
  }

  async function handleSignOut() {
    await authClient.signOut()
    toast.success("Signed out.")
    router.refresh()
  }

  const user = session?.user

  return (
    <DirectionProvider dir="ltr">
      <Toaster />
      <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-background px-4 py-8 text-foreground">
        <Link href="/">
          <Button variant="ghost" size="icon-sm" aria-label="Go home">
            <ArrowLeftIcon />
          </Button>
        </Link>

        {user ? (
          <Card className="w-full max-w-sm">
            <CardHeader>
              <CardTitle>Signed in</CardTitle>
              <CardDescription>
                You are authenticated against the mock third-party API.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-1 text-sm">
                <div className="text-muted-foreground">Username</div>
                <div className="font-medium">{user.name ?? user.email}</div>
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
                Sign out
              </Button>
            </CardContent>
          </Card>
        ) : (
          <Card className="w-full max-w-sm">
            <CardHeader>
              <CardTitle>Sign in to your account</CardTitle>
              <CardDescription>
                Enter your credentials to continue.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <FieldGroup>
                  <Field>
                    <FieldLabel htmlFor="username">Username</FieldLabel>
                    <FieldGroup>
                      <InputGroup className="w-full">
                        <InputGroupAddon>
                          <UserIcon className="size-4 opacity-50" />
                        </InputGroupAddon>
                        <InputGroupInput
                          id="username"
                          type="text"
                          autoComplete="username"
                          placeholder="username"
                          value={username}
                          onChange={(e) => setUsername(e.target.value)}
                          disabled={submitting || sessionPending}
                        />
                      </InputGroup>
                    </FieldGroup>
                  </Field>
                  <Field>
                    <FieldLabel htmlFor="password">Password</FieldLabel>
                    <FieldGroup>
                      <InputGroup className="w-full">
                        <InputGroupAddon>
                          <LockIcon className="size-4 opacity-50" />
                        </InputGroupAddon>
                        <InputGroupInput
                          id="password"
                          type="password"
                          autoComplete="current-password"
                          placeholder="••••••••"
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          disabled={submitting || sessionPending}
                        />
                      </InputGroup>
                    </FieldGroup>
                  </Field>
                </FieldGroup>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Checkbox
                      id="remember"
                      checked={remember}
                      onCheckedChange={(checked) => setRemember(checked === true)}
                      disabled={submitting || sessionPending}
                    />
                    <Label htmlFor="remember" className="text-sm">
                      Remember me
                    </Label>
                  </div>
                  <Button
                    type="button"
                    variant="link"
                    size="sm"
                    className="h-auto p-0 text-sm"
                    disabled={submitting || sessionPending}
                  >
                    Forgot password?
                  </Button>
                </div>
                <Button
                  type="submit"
                  className="w-full"
                  disabled={submitting || sessionPending}
                >
                  {submitting ? "Signing in..." : "Sign in"}
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        <p className="text-xs text-muted-foreground">
          Mock third-party API — try username <code>admin</code> / password{" "}
          <code>password</code>.
        </p>
      </div>
    </DirectionProvider>
  )
}
