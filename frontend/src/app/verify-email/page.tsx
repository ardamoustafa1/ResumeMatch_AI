"use client"

import { useState } from "react"
import Link from "next/link"
import { BadgeCheck } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { apiFetch } from "@/lib/api"

export default function VerifyEmailPage() {
  const [verified, setVerified] = useState(false)

  async function verify() {
    const token = new URLSearchParams(window.location.search).get("token")
    if (!token) {
      toast.error("The verification link is missing its token.")
      return
    }
    try {
      await apiFetch("/auth/verify-email", {
        method: "POST",
        body: JSON.stringify({ token }),
      })
      setVerified(true)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Verification failed.")
    }
  }

  return (
    <main className="grid min-h-screen place-items-center px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <BadgeCheck className="mb-3 size-7 text-blue-400" />
          <CardTitle>Verify your email</CardTitle>
          <CardDescription>
            Confirm ownership of the address linked to your account.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {verified ? (
            <Link href="/login" className="text-sm text-blue-400">
              Email verified. Continue to sign in.
            </Link>
          ) : (
            <Button onClick={() => void verify()} className="w-full">
              Verify email
            </Button>
          )}
        </CardContent>
      </Card>
    </main>
  )
}
