import { useCallback, useEffect, useState } from "react"
import { KeyRound, LoaderCircle } from "lucide-react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { apiFetch } from "@/lib/api"
import { CopyButton } from "./ResultsPanel"

export function ChromeExtensionCard({ copy }: { copy: (value: string) => Promise<void> }) {
  const [apiKey, setApiKey] = useState("")
  const [loading, setLoading] = useState(false)
  const [keys, setKeys] = useState<Array<{ id: string; name: string; prefix: string; expires_at: string }>>([])

  const loadKeys = useCallback(async () => {
    try {
      setKeys(await apiFetch("/auth/api-keys"))
    } catch {
      // Key management is optional to the main analysis workflow.
    }
  }, [])

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void loadKeys()
  }, [loadKeys])

  async function generateKey() {
    setLoading(true)
    try {
      const data = await apiFetch<{ access_token: string }>("/auth/api-key", { method: "POST" })
      setApiKey(data.access_token)
      toast.success("Extension key generated!")
      await loadKeys()
    } catch {
      toast.error("Failed to generate key.")
    } finally {
      setLoading(false)
    }
  }

  async function revokeKey(keyId: string) {
    try {
      await apiFetch(`/auth/api-keys/${keyId}`, { method: "DELETE" })
      setKeys((current) => current.filter((key) => key.id !== keyId))
      toast.success("Extension key revoked.")
    } catch {
      toast.error("Extension key could not be revoked.")
    }
  }

  return (
    <Card className="border-blue-500/20 bg-blue-950/5">
      <CardHeader>
        <CardTitle className="text-base">Chrome Extension Setup</CardTitle>
        <CardDescription>
          Generate a one-year, revocable API key to use NetworkForge directly on LinkedIn job posts.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {!apiKey ? (
          <Button onClick={() => void generateKey()} disabled={loading} variant="secondary" className="w-full text-blue-400">
            {loading ? <LoaderCircle className="size-4 animate-spin" /> : "Generate Extension Key"}
          </Button>
        ) : (
          <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4">
            <div className="mb-2 flex items-center justify-between">
              <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500">Your API Key</p>
              <CopyButton text={apiKey} copy={copy} />
            </div>
            <p className="break-all font-mono text-xs leading-relaxed text-zinc-300">{apiKey}</p>
            <p className="mt-3 text-xs leading-tight text-amber-500/80">Paste this into the extension popup. Keep it secret!</p>
          </div>
        )}
        {keys.length > 0 && (
          <div className="mt-4 space-y-2">
            <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500">Active keys</p>
            {keys.map((key) => (
              <div key={key.id} className="flex items-center justify-between rounded-lg border border-zinc-800 p-3">
                <div className="flex items-center gap-3">
                  <KeyRound className="size-4 text-zinc-500" />
                  <div>
                    <p className="text-sm">{key.name}</p>
                    <p className="font-mono text-xs text-zinc-500">
                      {key.prefix}… · expires {new Date(key.expires_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <Button variant="ghost" size="sm" onClick={() => void revokeKey(key.id)} className="text-red-400">Revoke</Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
