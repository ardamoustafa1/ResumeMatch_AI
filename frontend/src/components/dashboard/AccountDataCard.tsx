import { useState } from "react"
import { useRouter } from "next/navigation"
import { Download, Trash2, ShieldAlert, ShieldCheck } from "lucide-react"
import { QRCodeSVG } from "qrcode.react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog"
import { apiFetch } from "@/lib/api"
import { useAuthStore } from "@/stores/authStore"

export function AccountDataCard() {
  const router = useRouter()
  const { user, setUser } = useAuthStore()
  const [mfaSetupData, setMfaSetupData] = useState<{ secret: string; uri: string } | null>(null)
  const [mfaCode, setMfaCode] = useState("")
  const [settingUpMfa, setSettingUpMfa] = useState(false)

  async function deleteAccount() {
    try {
      await apiFetch<void>("/auth/me", { method: "DELETE" })
      setUser(null)
      router.replace("/")
      toast.success("Your account and associated data were deleted.")
    } catch {
      toast.error("Account deletion failed.")
    }
  }

  async function startMfaSetup() {
    try {
      setSettingUpMfa(true)
      const data = await apiFetch<{ secret: string; uri: string }>("/auth/mfa/setup", { method: "POST" })
      setMfaSetupData(data)
    } catch {
      toast.error("Failed to start MFA setup.")
    } finally {
      setSettingUpMfa(false)
    }
  }

  async function verifyAndEnableMfa() {
    try {
      await apiFetch("/auth/mfa/enable", {
        method: "POST",
        body: JSON.stringify({ code: mfaCode })
      })
      toast.success("MFA successfully enabled!")
      setMfaSetupData(null)
      setMfaCode("")
    } catch {
      toast.error("Invalid MFA code. Please try again.")
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Your data & security</CardTitle>
        <CardDescription>Export your stored data, configure two-factor authentication, or permanently delete your account.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {mfaSetupData ? (
          <div className="rounded-xl border border-blue-500/20 bg-blue-950/20 p-4">
            <h4 className="mb-2 font-semibold text-blue-400">Setup Two-Factor Authentication</h4>
            <p className="mb-4 text-sm text-zinc-300">Scan this QR code with Google Authenticator or Authy.</p>
            <div className="mb-4 rounded bg-white p-2 inline-block">
              <QRCodeSVG value={mfaSetupData.uri} size={150} />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-xs text-zinc-400">Enter the 6-digit code to verify:</label>
              <div className="flex gap-2">
                <Input value={mfaCode} onChange={(e) => setMfaCode(e.target.value)} placeholder="000000" maxLength={6} className="max-w-[120px]" />
                <Button onClick={() => void verifyAndEnableMfa()}>Verify</Button>
                <Button variant="ghost" onClick={() => setMfaSetupData(null)}>Cancel</Button>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-between rounded-xl border border-zinc-800 bg-zinc-950 p-4">
            <div className="flex items-center gap-3">
              {user?.mfa_enabled ? <ShieldCheck className="size-5 text-emerald-400" /> : <ShieldAlert className="size-5 text-amber-400" />}
              <div>
                <p className="text-sm font-medium">Two-Factor Authentication</p>
                <p className="text-xs text-zinc-500">{user?.mfa_enabled ? "MFA is enabled on your account." : "Not enabled. We recommend turning this on."}</p>
              </div>
            </div>
            {!user?.mfa_enabled && (
              <Button size="sm" variant="secondary" onClick={() => void startMfaSetup()} disabled={settingUpMfa}>Setup MFA</Button>
            )}
          </div>
        )}

        <div className="flex flex-col gap-3 sm:flex-row pt-4 border-t border-zinc-800">
          <Button asChild variant="secondary" className="flex-1">
            <a href="/api/v1/auth/export" download>
              <Download className="size-4" /> Export JSON
            </a>
          </Button>
          <AlertDialog>
            <AlertDialogTrigger render={<Button variant="danger" className="flex-1" />}>
              <Trash2 className="size-4" /> Delete account
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete your account permanently?</AlertDialogTitle>
                <AlertDialogDescription>
                  This removes your account, analyses, API keys, tokens, and notification settings. This action cannot be undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={() => void deleteAccount()} className="bg-red-600 text-white hover:bg-red-700">
                  Delete everything
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </CardContent>
    </Card>
  )
}
