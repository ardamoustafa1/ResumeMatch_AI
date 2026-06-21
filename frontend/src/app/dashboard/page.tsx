"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowUpRight, Check, LogOut, MessageSquareText, ScanSearch, ShieldCheck, Sparkles, Terminal } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { apiFetch, websocketUrl } from "@/lib/api"
import type { AnalysisRecord, FullAnalysisResult, ProgressEvent } from "@/lib/types"
import { useAuthStore } from "@/stores/authStore"

import { AnalysisForm } from "@/components/dashboard/AnalysisForm"
import { HistoryList } from "@/components/dashboard/HistoryList"
import { ChromeExtensionCard } from "@/components/dashboard/ExtensionCard"
import { AccountDataCard } from "@/components/dashboard/AccountDataCard"
import { ResultsPanel } from "@/components/dashboard/ResultsPanel"
import { motion } from "framer-motion"
import { BrandMark } from "@/components/brand-mark"

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
  const [provider, setProvider] = useState("auto")
  const [language, setLanguage] = useState("English")
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

  function completeAnalysis(nextResult: FullAnalysisResult, partial = false) {
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
    } catch {
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
        if ((record.status === "completed" || record.status === "partial_completed") && record.result) {
          completeAnalysis(record.result, record.status === "partial_completed")
        }
      } catch {
        // keep polling
      }
    }, 2000)
  }

  async function connectRealtime(analysisId: string) {
    try {
      const { ticket } = await apiFetch<{ ticket: string }>(`/ws/ticket?analysis_id=${analysisId}`, { method: "POST" })
      const socket = new WebSocket(websocketUrl(analysisId, ticket))
      socketRef.current = socket
      socket.onmessage = (event) => {
        const message = JSON.parse(event.data) as ProgressEvent
        if (message.progress !== null) setProgress(message.progress)
        if (message.event === "progress") {
          setLogs((current) => [...current, terminalSteps[message.step] ?? message.message])
        } else if (message.event === "completed" || message.event === "partial_completed") {
          completeAnalysis(message.data as FullAnalysisResult, message.event === "partial_completed")
        } else if (message.event === "failed") {
          stopRealtime()
          setAnalyzing(false)
          setLogs((current) => [...current, "✕ Analysis failed"])
          toast.error("Analysis failed after multiple attempts.")
        }
      }
      socket.onerror = () => socket.close()
      socket.onclose = () => { socketRef.current = null }
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
          provider: provider,
          language: language,
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
        <div className="size-8 animate-spin rounded-full border-4 border-blue-400 border-t-transparent" />
      </main>
    )
  }

  return (
    <main className="dashboard-shell">
      <header className="sticky top-0 z-40 border-b border-white/[0.07] bg-[#080a0f]/80 backdrop-blur-2xl">
        <div className="mx-auto flex h-[68px] max-w-[1480px] items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-5">
            <BrandMark />
            <span className="hidden h-5 w-px bg-white/[0.08] sm:block" />
            <div className="hidden sm:block">
              <p className="text-[11px] font-medium text-zinc-400">Opportunity workspace</p>
              <p className="text-[10px] text-zinc-700">{user.email}</p>
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <Button variant="ghost" size="sm" className="text-zinc-500" onClick={async () => { await logout(); router.replace("/login") }}>
              <LogOut className="size-4" />
              <span className="hidden sm:inline">Sign out</span>
            </Button>
          </div>
        </div>
      </header>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="mx-auto grid max-w-[1480px] gap-5 px-4 py-5 sm:px-6 sm:py-7 lg:grid-cols-[minmax(0,1.08fr)_minmax(400px,.92fr)] lg:px-8"
      >
        <div className="space-y-6">
          <AnalysisForm
            company={company} setCompany={setCompany}
            recruiterName={recruiterName} setRecruiterName={setRecruiterName}
            provider={provider} setProvider={setProvider}
            language={language} setLanguage={setLanguage}
            cvText={cvText} setCvText={setCvText}
            jdText={jdText} setJdText={setJdText}
            uploading={uploading} analyzing={analyzing}
            uploadCv={uploadCv} startAnalysis={startAnalysis}
          />

          <div className="grid gap-5 xl:grid-cols-2">
            <HistoryList history={history} deleteAnalysis={deleteAnalysis} />
            <ChromeExtensionCard copy={copy} />
          </div>
          <AccountDataCard />
        </div>

        <div className="space-y-6">
          {analyzing && (
            <Card className="overflow-hidden bg-black">
              <div className="flex items-center gap-2 border-b border-zinc-800 bg-zinc-900 p-4">
                <Terminal className="size-4 text-zinc-400" />
                <span className="font-mono text-xs text-zinc-400">analysis.log</span>
              </div>
              <CardContent className="pt-6">
                <div className="mb-5 h-2 overflow-hidden rounded-full bg-zinc-800">
                  <div className="h-full rounded-full bg-gradient-to-r from-blue-500 to-violet-500 transition-all" style={{ width: `${progress}%` }} />
                </div>
                <div className="min-h-48 space-y-3 font-mono text-sm">
                  {logs.map((log, index) => (
                    <p key={`${index}-${log}`} className="text-blue-300">
                      <span className="mr-2 text-zinc-600">&gt;</span>{log}
                    </p>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {!analyzing && !result && <EmptyResultState />}

          {result && <ResultsPanel result={result} copy={copy} />}
        </div>
      </motion.div>
    </main>
  )
}

function EmptyResultState() {
  return (
    <section className="dashboard-card sticky top-[88px] overflow-hidden">
      <div className="relative border-b border-white/[0.07] p-6 sm:p-7">
        <div className="absolute right-0 top-0 size-56 bg-[radial-gradient(circle,rgba(108,124,255,.16),transparent_66%)]" />
        <div className="relative">
          <div className="mb-5 flex items-center justify-between">
            <span className="eyebrow text-[#8995ff]">What you&apos;ll receive</span>
            <span className="rounded-full border border-white/[0.08] bg-white/[0.025] px-2.5 py-1 text-[9px] text-zinc-600">Preview</span>
          </div>
          <h2 className="text-balance text-3xl font-semibold leading-[1.06] tracking-[-0.05em]">
            Clarity before you hit apply.
          </h2>
          <p className="mt-3 max-w-md text-sm leading-6 text-zinc-500">
            A decision-ready view of your fit, your strongest proof, and the gaps worth closing.
          </p>
        </div>
      </div>

      <div className="grid gap-px bg-white/[0.07] sm:grid-cols-2">
        {[
          [ScanSearch, "Fit intelligence", "An explainable 0–100 match score with skill-level evidence.", "text-[#91a0ff]"],
          [Sparkles, "Better positioning", "Specific edits that make your existing experience easier to see.", "text-violet-300"],
          [MessageSquareText, "Personal outreach", "Editable recruiter messages grounded in your real background.", "text-cyan-300"],
          [ShieldCheck, "Private by design", "PII redaction and a fully local Ollama path when you want it.", "text-emerald-300"],
        ].map(([Icon, title, description, color]) => {
          const ItemIcon = Icon
          return (
            <div key={title as string} className="bg-[#0f1219] p-5 sm:p-6">
              <ItemIcon className={`size-4.5 ${color}`} />
              <h3 className="mt-8 text-sm font-semibold text-zinc-200">{title as string}</h3>
              <p className="mt-2 text-xs leading-5 text-zinc-600">{description as string}</p>
            </div>
          )
        })}
      </div>

      <div className="p-5 sm:p-6">
        <div className="rounded-2xl border border-white/[0.07] bg-black/20 p-4">
          <div className="mb-4 flex items-center justify-between">
            <span className="text-xs font-medium text-zinc-400">Sample signal</span>
            <ArrowUpRight className="size-3.5 text-zinc-700" />
          </div>
          <div className="flex items-end gap-2">
            <span className="text-4xl font-semibold tracking-[-0.06em] text-white">92</span>
            <span className="mb-1 text-xs text-zinc-600">role match</span>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {["FastAPI", "PostgreSQL", "AWS"].map((item) => (
              <span key={item} className="flex items-center gap-1.5 rounded-full border border-emerald-400/10 bg-emerald-400/[0.06] px-2.5 py-1 text-[10px] text-emerald-300">
                <Check className="size-2.5" /> {item}
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
