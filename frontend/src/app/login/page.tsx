"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { ArrowLeft, ShieldCheck, Sparkles } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { apiFetch } from "@/lib/api"
import type { User } from "@/lib/types"
import { useAuthStore } from "@/stores/authStore"

export default function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isRegister, setIsRegister] = useState(false)
  const [acceptedTOS, setAcceptedTOS] = useState(false)
  const [loading, setLoading] = useState(false)
  const router = useRouter()
  const setUser = useAuthStore((state) => state.setUser)

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    setLoading(true)
    try {
      if (isRegister) {
        if (!acceptedTOS) {
          toast.error("You must accept the Terms of Service and Privacy Policy.")
          setLoading(false)
          return
        }
        await apiFetch<User>("/auth/register", {
          method: "POST",
          body: JSON.stringify({ email, password }),
        })
        toast.success(
          "Account created. Check your email if verification is enabled.",
        )
        setIsRegister(false)
        setPassword("")
        return
      }

      const form = new URLSearchParams({ username: email, password })
      const response = await fetch("/api/v1/auth/login", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: form.toString(),
      })
      if (!response.ok) {
        throw new Error("Email or password is incorrect.")
      }
      const user = await apiFetch<User>("/auth/me")
      setUser(user)
      toast.success("Welcome back.")
      router.replace("/dashboard")
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Request failed.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-12">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(37,99,235,0.18),transparent_36%),radial-gradient(circle_at_bottom_right,rgba(147,51,234,0.16),transparent_32%)]" />
      <div className="relative w-full max-w-md">
        <Link
          href="/"
          className="mb-5 inline-flex items-center gap-2 text-sm text-zinc-400 transition hover:text-white"
        >
          <ArrowLeft className="size-4" />
          Back to overview
        </Link>
        <Card>
          <CardHeader>
            <div className="mb-4 flex size-11 items-center justify-center rounded-xl bg-blue-600/15 text-blue-400">
              <Sparkles className="size-6" />
            </div>
            <CardTitle>
              {isRegister ? "Create your account" : "Sign in to ResumeMatch"}
            </CardTitle>
            <CardDescription>
              {isRegister
                ? "Use a strong password to protect the personal data in your CV."
                : "Continue to your private analysis workspace."}
            </CardDescription>
          </CardHeader>
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium">
                  Email address
                </label>
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label htmlFor="password" className="text-sm font-medium">
                    Password
                  </label>
                  {!isRegister && (
                    <Link
                      href="/forgot-password"
                      className="text-xs text-blue-400 hover:text-blue-300"
                    >
                      Forgot password?
                    </Link>
                  )}
                </div>
                <Input
                  id="password"
                  type="password"
                  autoComplete={isRegister ? "new-password" : "current-password"}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  minLength={isRegister ? 12 : undefined}
                  required
                />
                {isRegister && (
                  <p className="text-xs leading-5 text-zinc-500">
                    At least 12 characters with uppercase, lowercase, number and
                    symbol.
                  </p>
                )}
              </div>
              {isRegister && (
                <div className="flex items-start gap-2 pt-2">
                  <input
                    type="checkbox"
                    id="tos"
                    checked={acceptedTOS}
                    onChange={(e) => setAcceptedTOS(e.target.checked)}
                    className="mt-1 size-4 rounded border-zinc-700 bg-zinc-950 text-blue-500 focus:ring-blue-500 focus:ring-offset-zinc-900"
                  />
                  <label htmlFor="tos" className="text-xs leading-5 text-zinc-400">
                    I agree to the <Link href="/terms" className="text-blue-400 hover:text-blue-300 transition">Terms of Service</Link> and <Link href="/privacy" className="text-blue-400 hover:text-blue-300 transition">Privacy Policy</Link>, and consent to the processing of my uploaded CVs according to these terms.
                  </label>
                </div>
              )}
              <div className="flex items-start gap-2 rounded-lg border border-emerald-900/50 bg-emerald-950/30 p-3 text-xs leading-5 text-emerald-200">
                <ShieldCheck className="mt-0.5 size-4 shrink-0" />
                Authentication is stored in secure HTTP-only cookies, not browser
                local storage.
              </div>
            </CardContent>
            <CardFooter className="flex-col gap-3">
              <Button type="submit" className="w-full" disabled={loading}>
                {loading
                  ? "Please wait…"
                  : isRegister
                    ? "Create account"
                    : "Sign in"}
              </Button>
              <button
                type="button"
                onClick={() => {
                  setIsRegister((value) => !value)
                  setPassword("")
                }}
                className="text-sm text-zinc-400 transition hover:text-white"
              >
                {isRegister
                  ? "Already registered? Sign in"
                  : "New here? Create an account"}
              </button>
            </CardFooter>
          </form>
        </Card>
      </div>
    </main>
  )
}
