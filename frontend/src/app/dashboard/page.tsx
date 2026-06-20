"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import { useRouter } from "next/navigation"
import {
  Check,
  Clipboard,
  FileUp,
  History,
  LoaderCircle,
  LogOut,
  Sparkles,
  Terminal,
  TriangleAlert,
  Trash2,
} from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import Link from "next/link"
import { apiFetch, websocketUrl } from "@/lib/api"
import type {
  AnalysisRecord,
  FullAnalysisResult,
  ProgressEvent,
} from "@/lib/types"
import { useAuthStore } from "@/stores/authStore"

const terminalSteps: Record<string, string> = {
  validating: "Validating input",
  analyzing_match: "Comparing CV with the role",
  generating_messages: "Writing outreach drafts",
  improving_profile: "Preparing profile suggestions",
}

export default function DashboardPage() {
  const router = useRouter()
  const { user, initialized, bootstrap, logout } = useAuthStore()
  const [cvText, setCvText] = useState("")
  const [jdText, setJdText] = useState("")
  const [company, setCompany] = useState("")
  const [recruiterName, setRecruiterName] = useState("")
  const [analyzing, setAnalyzing] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [logs, setLogs] = useState<string[]>([])
  const [result, setResult] = useState<FullAnalysisResult | null>(null)
  const [history, setHistory] = useState<AnalysisRecord[]>([])
  const socketRef = useRef<WebSocket | null>(null)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const stopRealtime = useCallback(() => {
    socketRef.current?.close()
    socketRef.current = null
    if (pollRef.current) clearInterval(pollRef.current)
    pollRef.current = null
  }, [])

  const loadHistory = useCallback(async () => {
    try {
      const data = await apiFetch<{ items: AnalysisRecord[] }>("/analysis?limit=8")
      setHistory(data.items)
    } catch {
      // History is non-critical to the main workflow.
    }
  }, [])

  useEffect(() => {
    if (!initialized) void bootstrap()
  }, [bootstrap, initialized])

  useEffect(() => {
    if (initialized && !user) router.replace("/login")
  }, [initialized, router, user])

  useEffect(() => {
    if (!user) return
    let cancelled = false
    apiFetch<{ items: AnalysisRecord[] }>("/analysis?limit=8")
      .then((data) => {
        if (!cancelled) setHistory(data.items)
      })
      .catch(() => undefined)
    return () => {
      cancelled = true
    }
  }, [user])

  useEffect(() => stopRealtime, [stopRealtime])

  function completeAnalysis(
    nextResult: FullAnalysisResult,
    partial = false,
  ) {
    stopRealtime()
    setResult(nextResult)
    setProgress(100)
    setAnalyzing(false)
    setLogs((current) => [
      ...current,
      partial ? "⚠ Analysis completed with partial results" : "✓ Analysis completed",
    ])
    toast[partial ? "warning" : "success"](
      partial ? "Partial result is ready." : "Analysis is ready.",
    )
    void loadHistory()
  }
  
  async function deleteAnalysis(id: string) {
    try {
      await apiFetch(`/analysis/${id}`, { method: "DELETE" })
      toast.success("Analysis deleted.")
      setHistory((prev) => prev.filter((a) => a.id !== id))
    } catch (err) {
      toast.error("Failed to delete analysis.")
    }
  }

  function startPolling(analysisId: string) {
    let attempts = 0
    pollRef.current = setInterval(async () => {
      attempts += 1
      if (attempts > 45) {
        stopRealtime()
        setAnalyzing(false)
        toast.error("The analysis timed out. You can safely try again.")
        return
      }
      try {
        const record = await apiFetch<AnalysisRecord>(`/analysis/${analysisId}`)
        if (
          (record.status === "completed" ||
            record.status === "partial_completed") &&
          record.result
        ) {
          completeAnalysis(record.result, record.status === "partial_completed")
        }
      } catch {
        // A processing analysis can return a non-final response; keep polling.
      }
    }, 2000)
  }

  async function connectRealtime(analysisId: string) {
    try {
      const { ticket } = await apiFetch<{ ticket: string }>(`/ws/ticket?analysis_id=${analysisId}`, { method: "POST" })
      const socket = new WebSocket(websocketUrl(analysisId, ticket))
      socketRef.current = socket
      let receivedMessage = false

    socket.onmessage = (event) => {
      receivedMessage = true
      const message = JSON.parse(event.data) as ProgressEvent
      if (message.progress !== null) setProgress(message.progress)
      if (message.event === "progress") {
        setLogs((current) => [
          ...current,
          terminalSteps[message.step] ?? message.message,
        ])
      } else if (
        message.event === "completed" ||
        message.event === "partial_completed"
      ) {
        completeAnalysis(
          message.data as FullAnalysisResult,
          message.event === "partial_completed",
        )
      } else if (message.event === "failed") {
        stopRealtime()
        setAnalyzing(false)
        setLogs((current) => [...current, "✕ Analysis failed"])
        toast.error("Analysis failed after multiple attempts.")
      }
    }
    socket.onerror = () => {
      socket.close()
    }
    socket.onclose = () => {
      socketRef.current = null
    }
    } catch (err) {
      console.error("Failed to connect realtime:", err)
    }
  }

  async function startAnalysis() {
    if (cvText.trim().length < 100 || jdText.trim().length < 50) {
      toast.error("CV must be 100+ characters and job description 50+ characters.")
      return
    }
    stopRealtime()
    setAnalyzing(true)
    setProgress(5)
    setResult(null)
    setLogs(["Creating a private analysis job"])
    try {
      const data = await apiFetch<{ analysis_id: string }>("/analysis", {
        method: "POST",
        body: JSON.stringify({
          cv_text: cvText,
          jd_text: jdText,
          company: company || null,
          recruiter_name: recruiterName || null,
        }),
      })
      setLogs((current) => [...current, `Job queued · ${data.analysis_id}`])
      await connectRealtime(data.analysis_id)
      startPolling(data.analysis_id)
    } catch (error) {
      setAnalyzing(false)
      toast.error(error instanceof Error ? error.message : "Analysis could not start.")
    }
  }

  async function uploadCv(file: File | undefined) {
    if (!file) return
    setUploading(true)
    try {
      const form = new FormData()
      form.append("file", file)
      const data = await apiFetch<{ extracted_text: string }>("/extract-text/", {
        method: "POST",
        body: form,
      })
      setCvText(data.extracted_text)
      toast.success("CV text extracted.")
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "File could not be read.")
    } finally {
      setUploading(false)
    }
  }

  async function copy(text: string) {
    await navigator.clipboard.writeText(text)
    toast.success("Copied to clipboard.")
  }

  if (!initialized || !user) {
    return (
      <main className="grid min-h-screen place-items-center">
        <LoaderCircle className="size-8 animate-spin text-blue-400" />
      </main>
    )
  }

  return (
    <main className="min-h-screen">
      <header className="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4">
          <div className="flex items-center gap-3">
            <span className="flex size-9 items-center justify-center rounded-xl bg-blue-600">
              <Sparkles className="size-5" />
            </span>
            <div>
              <p className="font-bold">ResumeMatch AI</p>
              <p className="text-xs text-zinc-500">{user.email}</p>
            </div>
          </div>
          <Button
            variant="ghost"
            onClick={async () => {
              await logout()
              router.replace("/login")
            }}
          >
            <LogOut className="size-4" />
            Sign out
          </Button>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl gap-6 px-5 py-8 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,.95fr)]">
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>New analysis</CardTitle>
              <CardDescription>
                Your CV is processed only for this analysis. Review every generated
                message before sending it.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="space-y-2 text-sm font-medium">
                  Company
                  <input
                    value={company}
                    onChange={(event) => setCompany(event.target.value)}
                    className="field"
                    placeholder="Acme"
                  />
                </label>
                <label className="space-y-2 text-sm font-medium">
                  Recruiter name
                  <input
                    value={recruiterName}
                    onChange={(event) => setRecruiterName(event.target.value)}
                    className="field"
                    placeholder="Alex"
                  />
                </label>
              </div>
              <label className="block space-y-2 text-sm font-medium">
                CV text
                <textarea
                  value={cvText}
                  onChange={(event) => setCvText(event.target.value)}
                  className="field min-h-52 resize-y"
                  placeholder="Paste your CV text or upload a PDF/image…"
                />
              </label>
              <label className="flex cursor-pointer items-center justify-center gap-2 rounded-lg border border-dashed border-zinc-700 px-4 py-3 text-sm text-zinc-400 transition hover:border-blue-500 hover:text-blue-300">
                {uploading ? (
                  <LoaderCircle className="size-4 animate-spin" />
                ) : (
                  <FileUp className="size-4" />
                )}
                {uploading ? "Extracting text…" : "Upload PDF, PNG or JPEG (max 10 MB)"}
                <input
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg"
                  className="sr-only"
                  onChange={(event) => void uploadCv(event.target.files?.[0])}
                  disabled={uploading}
                />
              </label>
              <label className="block space-y-2 text-sm font-medium">
                Job description
                <textarea
                  value={jdText}
                  onChange={(event) => setJdText(event.target.value)}
                  className="field min-h-52 resize-y"
                  placeholder="Paste the complete job description…"
                />
              </label>
              <Button
                onClick={() => void startAnalysis()}
                disabled={analyzing}
                className="w-full"
              >
                {analyzing ? (
                  <LoaderCircle className="size-4 animate-spin" />
                ) : (
                  <Sparkles className="size-4" />
                )}
                {analyzing ? "Analyzing…" : "Start AI analysis"}
              </Button>
            </CardContent>
          </Card>

          {history.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <History className="size-4 text-zinc-400" />
                  Recent analyses
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {history.map((item) => (
                  <div
                    key={item.id}
                    className="group flex items-center justify-between rounded-lg border border-zinc-800 bg-zinc-950/50 p-3 transition hover:border-zinc-700 hover:bg-zinc-900"
                  >
                    <Link href={`/dashboard/analysis/${item.id}`} className="flex-1">
                      <p className="text-sm font-medium transition group-hover:text-blue-400">
                        {item.company || "Unnamed company"}
                      </p>
                      <p className="text-xs text-zinc-500">
                        {new Date(item.created_at).toLocaleString()}
                      </p>
                    </Link>
                    <div className="flex items-center gap-3">
                      <span className="rounded-full bg-zinc-800 px-2 py-1 text-xs text-zinc-300">
                        {item.status.replace("_", " ")}
                      </span>
                      <AlertDialog>
                      <AlertDialogTrigger
                        className="text-zinc-600 opacity-0 transition hover:text-red-400 group-hover:opacity-100"
                        title="Delete"
                      >
                        <Trash2 className="h-4 w-4" />
                      </AlertDialogTrigger>
                      <AlertDialogContent className="bg-zinc-950 border-zinc-800">
                          <AlertDialogHeader>
                            <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                            <AlertDialogDescription className="text-zinc-400">
                              This action cannot be undone. This will permanently delete your
                              analysis and remove the data from our servers.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel className="bg-zinc-900 text-white border-zinc-800 hover:bg-zinc-800">Cancel</AlertDialogCancel>
                            <AlertDialogAction onClick={() => void deleteAnalysis(item.id)} className="bg-red-600 hover:bg-red-700 text-white">
                              Delete
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          <ChromeExtensionCard copy={copy} />
        </div>

        <div className="space-y-6">
          {analyzing && (
            <Card className="overflow-hidden bg-black">
              <div className="flex items-center gap-2 border-b border-zinc-800 bg-zinc-900 p-4">
                <Terminal className="size-4 text-zinc-400" />
                <span className="font-mono text-xs text-zinc-400">
                  analysis.log
                </span>
              </div>
              <CardContent className="pt-6">
                <div className="mb-5 h-2 overflow-hidden rounded-full bg-zinc-800">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-blue-500 to-violet-500 transition-all"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <div className="min-h-48 space-y-3 font-mono text-sm">
                  {logs.map((log, index) => (
                    <p key={`${index}-${log}`} className="text-blue-300">
                      <span className="mr-2 text-zinc-600">&gt;</span>
                      {log}
                    </p>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {!analyzing && !result && (
            <Card className="border-dashed">
              <CardContent className="flex min-h-72 flex-col items-center justify-center pt-6 text-center">
                <Sparkles className="mb-4 size-9 text-zinc-700" />
                <h2 className="font-bold">Your result will appear here</h2>
                <p className="mt-2 max-w-sm text-sm leading-6 text-zinc-500">
                  Add your CV and a target role to receive an explainable match
                  score and editable outreach drafts.
                </p>
              </CardContent>
            </Card>
          )}

          {result && <Results result={result} copy={copy} />}
        </div>
      </div>
    </main>
  )
}

function CopyButton({
  text,
  copy,
}: {
  text: string
  copy: (value: string) => Promise<void>
}) {
  return (
    <button
      onClick={() => void copy(text)}
      className="rounded-md p-2 text-zinc-500 transition hover:bg-zinc-800 hover:text-white"
      aria-label="Copy text"
    >
      <Clipboard className="size-4" />
    </button>
  )
}

function Results({
  result,
  copy,
}: {
  result: FullAnalysisResult
  copy: (value: string) => Promise<void>
}) {
  const match = result.match_result
  return (
    <div className="space-y-6">
      {result.errors && Object.keys(result.errors).length > 0 && (
        <div className="flex gap-3 rounded-xl border border-amber-800/60 bg-amber-950/30 p-4 text-sm text-amber-200">
          <TriangleAlert className="mt-0.5 size-4 shrink-0" />
          Some optional sections could not be generated. The available results are
          shown below.
        </div>
      )}
      {match && (
        <Card className="border-blue-500/30">
          <CardHeader>
            <CardTitle className="flex items-end gap-3">
              <span className="text-5xl text-blue-400">{match.score}%</span>
              <span className="pb-1 text-base text-zinc-400">role match</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            <SkillList title="Matched skills" items={match.matched_skills} positive />
            <SkillList title="Missing skills" items={match.missing_skills} />
            <div>
              <h3 className="mb-2 text-sm font-semibold">Improvements</h3>
              <ul className="space-y-2 text-sm leading-6 text-zinc-300">
                {match.improvement_suggestions.map((item) => (
                  <li key={item} className="flex gap-2">
                    <Check className="mt-1 size-4 shrink-0 text-blue-400" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
      )}

      {result.outreach_messages && (
        <Card>
          <CardHeader>
            <CardTitle>Outreach drafts</CardTitle>
            <CardDescription>
              Review and personalize these drafts before sending.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {[
              ["First contact", result.outreach_messages.dm_first_contact],
              ["Day 7 follow-up", result.outreach_messages.dm_follow_up],
              ["Connection note", result.outreach_messages.connection_note],
            ].map(([title, text]) => (
              <div key={title} className="rounded-xl bg-zinc-950 p-4">
                <div className="mb-2 flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-blue-300">{title}</h3>
                  <CopyButton text={text} copy={copy} />
                </div>
                <p className="whitespace-pre-wrap text-sm leading-6 text-zinc-300">
                  {text}
                </p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {result.profile_improvements && (
        <Card>
          <CardHeader>
            <CardTitle>Profile improvements</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-xl bg-zinc-950 p-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
                Suggested headline
              </p>
              <div className="mt-2 flex items-start justify-between gap-3">
                <p className="text-sm leading-6 text-zinc-200">
                  {result.profile_improvements.headline_after}
                </p>
                <CopyButton
                  text={result.profile_improvements.headline_after}
                  copy={copy}
                />
              </div>
            </div>
            <div className="rounded-xl bg-zinc-950 p-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
                About section
              </p>
              <div className="mt-2 flex items-start justify-between gap-3">
                <p className="whitespace-pre-wrap text-sm leading-6 text-zinc-300">
                  {result.profile_improvements.about_section}
                </p>
                <CopyButton
                  text={result.profile_improvements.about_section}
                  copy={copy}
                />
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function SkillList({
  title,
  items,
  positive = false,
}: {
  title: string
  items: string[]
  positive?: boolean
}) {
  return (
    <div>
      <h3 className="mb-2 text-sm font-semibold">{title}</h3>
      <div className="flex flex-wrap gap-2">
        {items.length ? (
          items.map((item) => (
            <span
              key={item}
              className={
                positive
                  ? "rounded-full bg-emerald-950 px-3 py-1 text-xs text-emerald-300"
                  : "rounded-full bg-amber-950 px-3 py-1 text-xs text-amber-300"
              }
            >
              {item}
            </span>
          ))
        ) : (
          <span className="text-sm text-zinc-500">None identified</span>
        )}
      </div>
    </div>
  )
}

function ChromeExtensionCard({ copy }: { copy: (value: string) => Promise<void> }) {
  const [apiKey, setApiKey] = useState("")
  const [loading, setLoading] = useState(false)

  async function generateKey() {
    setLoading(true)
    try {
      const data = await apiFetch<{ access_token: string }>("/auth/api-key", {
        method: "POST",
      })
      setApiKey(data.access_token)
      toast.success("Extension key generated!")
    } catch {
      toast.error("Failed to generate key.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="border-blue-500/20 bg-blue-950/5">
      <CardHeader>
        <CardTitle className="text-base">Chrome Extension Setup</CardTitle>
        <CardDescription>
          Generate a permanent API key to use ResumeMatch AI directly on LinkedIn job posts.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {!apiKey ? (
          <Button
            onClick={() => void generateKey()}
            disabled={loading}
            variant="secondary"
            className="w-full text-blue-400"
          >
            {loading ? (
              <LoaderCircle className="size-4 animate-spin" />
            ) : (
              "Generate Extension Key"
            )}
          </Button>
        ) : (
          <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4">
            <div className="mb-2 flex items-center justify-between">
              <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
                Your API Key
              </p>
              <CopyButton text={apiKey} copy={copy} />
            </div>
            <p className="break-all font-mono text-xs leading-relaxed text-zinc-300">
              {apiKey}
            </p>
            <p className="mt-3 text-xs leading-tight text-amber-500/80">
              Paste this into the extension popup. Keep it secret!
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
