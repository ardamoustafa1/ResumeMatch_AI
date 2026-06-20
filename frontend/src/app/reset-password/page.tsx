"use client"

import { useState } from "react"
import Link from "next/link"
import { KeyRound } from "lucide-react"
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

export default function ResetPasswordPage() {
  const [password, setPassword] = useState("")
  const [complete, setComplete] = useState(false)

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    const token = new URLSearchParams(window.location.search).get("token")
    if (!token) {
      toast.error("The reset link is missing its token.")
      return
    }
    try {
      await apiFetch("/auth/reset-password", {
        method: "POST",
        body: JSON.stringify({ token, password }),
      })
      setComplete(true)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Reset failed.")
    }
  }

  return (
    <main className="grid min-h-screen place-items-center px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <KeyRound className="mb-3 size-7 text-blue-400" />
          <CardTitle>Choose a new password</CardTitle>
          <CardDescription>
            Use at least 12 characters with uppercase, lowercase, number and symbol.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {complete ? (
            <Link href="/login" className="text-sm text-blue-400">
              Password updated. Continue to sign in.
            </Link>
          ) : (
            <form onSubmit={submit} className="space-y-4">
              <Input
                type="password"
                autoComplete="new-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                minLength={12}
                required
              />
              <Button type="submit" className="w-full">
                Update password
              </Button>
            </form>
          )}
        </CardContent>
      </Card>
    </main>
  )
}
