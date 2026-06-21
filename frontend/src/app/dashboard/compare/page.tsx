"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, GitCompare, Check, X } from "lucide-react"
import Link from "next/link"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { apiFetch } from "@/lib/api"
import type { AnalysisRecord } from "@/lib/types"
import { useAuthStore } from "@/stores/authStore"
import { BrandMark } from "@/components/brand-mark"
import { motion } from "framer-motion"

export default function ComparePage() {
  const router = useRouter()
  const { user, initialized, bootstrap } = useAuthStore()
  const [history, setHistory] = useState<AnalysisRecord[]>([])
  
  const [analysisAId, setAnalysisAId] = useState<string>("")
  const [analysisBId, setAnalysisBId] = useState<string>("")
  
  const [analysisA, setAnalysisA] = useState<(AnalysisRecord & { cv_text?: string, jd_text?: string }) | null>(null)
  const [analysisB, setAnalysisB] = useState<(AnalysisRecord & { cv_text?: string, jd_text?: string }) | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!initialized) void bootstrap()
  }, [bootstrap, initialized])

  useEffect(() => {
    if (initialized && !user) router.replace("/login")
  }, [initialized, router, user])

  useEffect(() => {
    if (!user) return
    let cancelled = false
    apiFetch<{ items: AnalysisRecord[] }>("/analysis?limit=50")
      .then((data) => {
        if (!cancelled) setHistory(data.items.filter(i => i.status === "completed" || i.status === "partial_completed"))
      })
      .catch(() => undefined)
    return () => { cancelled = true }
  }, [user])

  const fetchAnalysis = async (id: string, setter: (data: any) => void) => {
    if (!id) {
      setter(null)
      return
    }
    setLoading(true)
    try {
      const data = await apiFetch(`/analysis/${id}`)
      setter(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchAnalysis(analysisAId, setAnalysisA) }, [analysisAId])
  useEffect(() => { fetchAnalysis(analysisBId, setAnalysisB) }, [analysisBId])

  if (!initialized || !user) {
    return (
      <main className="grid min-h-screen place-items-center">
        <div className="size-8 animate-spin rounded-full border-4 border-blue-400 border-t-transparent" />
      </main>
    )
  }

  return (
    <main className="dashboard-shell min-h-screen bg-[#080a0f]">
      <header className="sticky top-0 z-40 border-b border-white/[0.07] bg-[#080a0f]/80 backdrop-blur-2xl">
        <div className="mx-auto flex h-[68px] max-w-[1480px] items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-5">
            <Link href="/dashboard">
              <BrandMark />
            </Link>
            <span className="h-5 w-px bg-white/[0.08]" />
            <div className="flex items-center gap-2 text-sm font-medium text-zinc-300">
              <GitCompare className="size-4" /> Compare CV Versions
            </div>
          </div>
          <Button variant="ghost" size="sm" asChild>
            <Link href="/dashboard" className="text-zinc-400">
              <ArrowLeft className="mr-2 size-4" /> Back to Dashboard
            </Link>
          </Button>
        </div>
      </header>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mx-auto max-w-[1480px] p-4 sm:p-6 lg:p-8"
      >
        <div className="mb-8 grid gap-6 md:grid-cols-2">
          {/* Selector A */}
          <Card className="bg-[#0f1219] border-white/[0.07]">
            <CardContent className="p-6">
              <label className="text-sm font-medium text-zinc-400 mb-2 block">Select Version A</label>
              <select 
                className="w-full bg-black/40 border border-white/[0.1] rounded-md p-2 text-sm text-zinc-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
                value={analysisAId}
                onChange={(e) => setAnalysisAId(e.target.value)}
              >
                <option value="">-- Select Analysis --</option>
                {history.map(h => (
                  <option key={h.id} value={h.id}>
                    {new Date(h.created_at).toLocaleString()} - {h.company || "Unknown Company"} ({h.result?.match_result?.score || 0})
                  </option>
                ))}
              </select>
            </CardContent>
          </Card>

          {/* Selector B */}
          <Card className="bg-[#0f1219] border-white/[0.07]">
            <CardContent className="p-6">
              <label className="text-sm font-medium text-zinc-400 mb-2 block">Select Version B</label>
              <select 
                className="w-full bg-black/40 border border-white/[0.1] rounded-md p-2 text-sm text-zinc-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
                value={analysisBId}
                onChange={(e) => setAnalysisBId(e.target.value)}
              >
                <option value="">-- Select Analysis --</option>
                {history.map(h => (
                  <option key={h.id} value={h.id}>
                    {new Date(h.created_at).toLocaleString()} - {h.company || "Unknown Company"} ({h.result?.match_result?.score || 0})
                  </option>
                ))}
              </select>
            </CardContent>
          </Card>
        </div>

        {loading && <div className="text-center text-zinc-500 py-12">Loading analysis data...</div>}

        {!loading && analysisA && analysisB && (
          <div className="grid gap-6 md:grid-cols-2">
            <ComparisonColumn analysis={analysisA} title="Version A" />
            <ComparisonColumn analysis={analysisB} title="Version B" />
          </div>
        )}
      </motion.div>
    </main>
  )
}

function ComparisonColumn({ analysis, title }: { analysis: any, title: string }) {
  const result = analysis.result?.match_result;
  
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-white">{title}</h2>
      
      <Card className="bg-[#0f1219] border-white/[0.07]">
        <CardContent className="p-6">
          <div className="flex items-end gap-3 mb-6 border-b border-white/[0.05] pb-4">
            <span className="text-5xl font-bold text-white">{result?.score || 0}</span>
            <span className="text-sm text-zinc-500 mb-1">Match Score</span>
          </div>

          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-medium text-emerald-400 mb-3 flex items-center gap-2">
                <Check className="size-4" /> Matched Skills ({result?.matched_skills?.length || 0})
              </h3>
              <div className="flex flex-wrap gap-2">
                {result?.matched_skills?.map((s: string) => (
                  <span key={s} className="px-2 py-1 bg-emerald-500/10 text-emerald-300 text-xs rounded border border-emerald-500/20">{s}</span>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-sm font-medium text-rose-400 mb-3 flex items-center gap-2">
                <X className="size-4" /> Missing Skills ({result?.missing_skills?.length || 0})
              </h3>
              <div className="flex flex-wrap gap-2">
                {result?.missing_skills?.map((s: string) => (
                  <span key={s} className="px-2 py-1 bg-rose-500/10 text-rose-300 text-xs rounded border border-rose-500/20">{s}</span>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-[#0f1219] border-white/[0.07]">
        <CardContent className="p-6">
          <h3 className="text-sm font-medium text-zinc-300 mb-4">CV Text</h3>
          <div className="bg-black/50 p-4 rounded-md border border-white/[0.05] text-xs text-zinc-400 whitespace-pre-wrap max-h-96 overflow-y-auto">
            {analysis.cv_text || "No CV text available."}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
