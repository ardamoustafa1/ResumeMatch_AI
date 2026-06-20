"use client"

import { useState } from "react"
import Link from "next/link"
import { Mail } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { apiFetch } from "@/lib/api"

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("")
  const [sent, setSent] = useState(false)

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    try {
      await apiFetch("/auth/forgot-password", {
        method: "POST",
        body: JSON.stringify({ email }),
      })
      setSent(true)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Request failed.")
    }
  }

  return (
    <main className="grid min-h-screen place-items-center px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <Mail className="mb-3 size-7 text-blue-400" />
          <CardTitle>Reset your password</CardTitle>
          <CardDescription>
            Enter your account email. The response is intentionally the same for
            existing and unknown accounts.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {sent ? (
            <div className="space-y-4">
              <p className="rounded-lg bg-emerald-950/40 p-4 text-sm text-emerald-200">
                If the account exists, reset instructions have been sent.
              </p>
              <Link href="/login" className="text-sm text-blue-400">
                Return to sign in
              </Link>
            </div>
          ) : (
            <form onSubmit={submit} className="space-y-4">
              <label className="block space-y-2 text-sm font-medium">
                Email address
                <Input
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  required
                />
              </label>
              <Button type="submit" className="w-full">
                Send reset instructions
              </Button>
            </form>
          )}
        </CardContent>
      </Card>
    </main>
  )
}
