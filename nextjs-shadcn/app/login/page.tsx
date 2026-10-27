"use client"

import Link from "next/link"
import { useState, type FormEvent } from "react"
import { toast } from "sonner"
import { ArrowLeftIcon, LockIcon, MailIcon } from "lucide-react"

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

export default function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [remember, setRemember] = useState(false)

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (!email.trim() || !password) {
      toast.error("Please enter your email and password.")
      return
    }
    toast.success(`Signed in as ${email.trim()} (demo)`)
  }

  return (
    <DirectionProvider dir="ltr">
      <Toaster />
      <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-background px-4 py-8 text-foreground">
        <Link href="/">
          <Button variant="ghost" size="icon-sm" aria-label="Go home">
            <ArrowLeftIcon />
          </Button>
        </Link>

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
                  <FieldLabel htmlFor="email">Email</FieldLabel>
                  <FieldGroup>
                    <InputGroup className="w-full">
                      <InputGroupAddon>
                        <MailIcon className="size-4 opacity-50" />
                      </InputGroupAddon>
                      <InputGroupInput
                        id="email"
                        type="email"
                        autoComplete="email"
                        placeholder="you@example.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
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
                >
                  Forgot password?
                </Button>
              </div>
              <Button type="submit" className="w-full">
                Sign in
              </Button>
            </form>
          </CardContent>
        </Card>

        <p className="text-xs text-muted-foreground">
          Demo only — no backend wired yet.
        </p>
      </div>
    </DirectionProvider>
  )
}
