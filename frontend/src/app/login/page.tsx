"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import Image from "next/image"
import { ArrowLeft, Check, ShieldCheck } from "lucide-react"
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
import { BrandMark } from "@/components/brand-mark"

export default function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isRegister, setIsRegister] = useState(false)
  const [acceptedTOS, setAcceptedTOS] = useState(false)
  const [loading, setLoading] = useState(false)
  const [mfaToken, setMfaToken] = useState("")
  const [mfaCode, setMfaCode] = useState("")
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

      if (mfaToken) {
        await apiFetch("/auth/mfa/verify", {
          method: "POST",
          body: JSON.stringify({ mfa_token: mfaToken, code: mfaCode }),
        })
        const user = await apiFetch<User>("/auth/me")
        setUser(user)
        toast.success("Welcome back.")
        router.replace("/dashboard")
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
      const data = await response.json()
      if (data.status === "mfa_required") {
        setMfaToken(data.mfa_token)
        toast.info("Two-factor authentication required.")
        return
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
    <main className="dashboard-shell relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-8">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(80,98,235,0.15),transparent_34%),radial-gradient(circle_at_80%_80%,rgba(139,80,220,0.11),transparent_32%)]" />
      <div className="relative grid w-full max-w-5xl overflow-hidden rounded-[1.6rem] border border-white/[0.09] bg-[#0d1017]/95 shadow-[0_50px_140px_rgba(0,0,0,.55)] lg:grid-cols-[1.04fr_.96fr]">
        <section className="relative hidden min-h-[660px] overflow-hidden border-r border-white/[0.07] p-9 lg:flex lg:flex-col">
          <Image src="/brand/networkforge-hero.png" alt="" fill priority sizes="52vw" className="object-cover opacity-65" />
          <div className="absolute inset-0 bg-gradient-to-t from-[#0b0e14] via-[#0b0e14]/45 to-[#0b0e14]/15" />
          <div className="relative">
            <BrandMark />
          </div>
          <div className="relative mt-auto max-w-md">
            <p className="eyebrow text-[#9aa4ff]">Private career intelligence</p>
            <h1 className="mt-4 text-4xl font-semibold leading-[1.06] tracking-[-0.055em]">
              Make the next move with evidence.
            </h1>
            <p className="mt-4 text-sm leading-7 text-zinc-400">
              Understand your fit, sharpen your positioning, and write outreach that starts with something real.
            </p>
            <div className="mt-7 space-y-3">
              {["Explainable role matching", "Local Ollama inference", "Editable, grounded outreach"].map((item) => (
                <div key={item} className="flex items-center gap-2.5 text-xs text-zinc-300">
                  <span className="flex size-5 items-center justify-center rounded-full bg-emerald-400/10">
                    <Check className="size-3 text-emerald-400" />
                  </span>
                  {item}
                </div>
              ))}
            </div>
          </div>
        </section>

        <div className="relative flex min-h-[620px] flex-col justify-center p-5 sm:p-10 lg:p-12">
        <Link
          href="/"
          className="absolute left-5 top-5 inline-flex items-center gap-2 text-xs text-zinc-600 transition hover:text-white sm:left-10 sm:top-8 lg:left-12"
        >
          <ArrowLeft className="size-4" />
          Back to overview
        </Link>
        <BrandMark className="mb-8 mt-10 lg:hidden" />
        <Card className="border-0 bg-transparent shadow-none backdrop-blur-none">
          <CardHeader>
            <CardTitle>
              {mfaToken ? "Two-Factor Authentication" : isRegister ? "Create your account" : "Sign in to NetworkForge"}
            </CardTitle>
            <CardDescription>
              {mfaToken ? "Enter the 6-digit code from your authenticator app." : isRegister
                ? "Use a strong password to protect the personal data in your CV."
                : "Continue to your private analysis workspace."}
            </CardDescription>
          </CardHeader>
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              {mfaToken ? (
                <div className="space-y-2">
                  <label htmlFor="mfaCode" className="text-sm font-medium">Authenticator Code</label>
                  <Input
                    id="mfaCode"
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    autoComplete="one-time-code"
                    value={mfaCode}
                    onChange={(event) => setMfaCode(event.target.value)}
                    required
                    maxLength={6}
                    placeholder="000000"
                  />
                </div>
              ) : (
                <>
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
              </>
              )}
            </CardContent>
            <CardFooter className="flex-col gap-3">
              <Button type="submit" className="w-full" disabled={loading}>
                {loading
                  ? "Please wait…"
                  : mfaToken
                    ? "Verify Code"
                    : isRegister
                      ? "Create account"
                      : "Sign in"}
              </Button>
              {!mfaToken && (
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
              )}
              {mfaToken && (
                <button type="button" onClick={() => setMfaToken("")} className="text-sm text-zinc-400 transition hover:text-white">
                  Cancel
                </button>
              )}
            </CardFooter>
          </form>
        </Card>
        </div>
      </div>
    </main>
  )
}
