"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import Link from "next/link"
import { ArrowLeft, LoaderCircle, Sparkles, TriangleAlert, Check, Clipboard } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { apiFetch } from "@/lib/api"
import type { AnalysisRecord, FullAnalysisResult } from "@/lib/types"

export default function AnalysisDetailPage() {
  const params = useParams()
  const router = useRouter()
  const id = params?.id as string
  const [record, setRecord] = useState<AnalysisRecord | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    
    if (id === "demo") {
      apiFetch<any>("/analysis/demo", { method: "POST" })
        .then((data) => {
          setRecord({
            id: data.analysis_id,
            user_id: "demo",
            company: "Demo Mode - Stripe",
            recruiter_name: "Jane",
            status: "completed",
            result: data.result,
            created_at: new Date().toISOString()
          })
        })
        .finally(() => setLoading(false))
      return
    }

    apiFetch<AnalysisRecord>(`/analysis/${id}`)
      .then((data) => {
        setRecord(data)
      })
      .catch((err) => {
        toast.error("Analysis not found.")
        router.replace("/dashboard")
      })
      .finally(() => {
        setLoading(false)
      })
  }, [id, router])

  async function copy(text: string) {
    await navigator.clipboard.writeText(text)
    toast.success("Copied to clipboard.")
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoaderCircle className="size-8 animate-spin text-blue-500" />
      </div>
    )
  }

  if (!record || !record.result) {
    return (
      <div className="flex min-h-screen items-center justify-center flex-col gap-4">
        <p className="text-zinc-500">Analysis results are not available yet.</p>
        <Button asChild variant="outline">
          <Link href="/dashboard">Return to Dashboard</Link>
        </Button>
      </div>
    )
  }

  const result: FullAnalysisResult = record.result
  const match = result.match_result

  return (
    <main className="mx-auto max-w-4xl px-5 py-12">
      <Link
        href="/dashboard"
        className="mb-8 inline-flex items-center gap-2 text-sm text-zinc-400 transition hover:text-white"
      >
        <ArrowLeft className="size-4" />
        Back to Dashboard
      </Link>

      <div className="mb-8">
        <h1 className="text-2xl font-bold">{record.company || "Unnamed Role"}</h1>
        <p className="text-zinc-500 text-sm">
          Analyzed on {new Date(record.created_at).toLocaleString()}
        </p>
      </div>

      <div className="space-y-8">
        {result.errors && Object.keys(result.errors).length > 0 && (
          <div className="flex gap-3 rounded-xl border border-amber-800/60 bg-amber-950/30 p-4 text-sm text-amber-200">
            <TriangleAlert className="mt-0.5 size-4 shrink-0" />
            Some optional sections could not be generated.
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
            <CardContent className="space-y-6">
              <div>
                <h3 className="mb-2 text-sm font-semibold">Matched skills</h3>
                <div className="flex flex-wrap gap-2">
                  {match.matched_skills.map((s) => (
                    <span key={s} className="rounded-full bg-emerald-950 px-3 py-1 text-xs text-emerald-300">{s}</span>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="mb-2 text-sm font-semibold">Missing skills</h3>
                <div className="flex flex-wrap gap-2">
                  {match.missing_skills.map((s) => (
                    <span key={s} className="rounded-full bg-amber-950 px-3 py-1 text-xs text-amber-300">{s}</span>
                  ))}
                </div>
              </div>
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
              <CardDescription>Generated outreach messages.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                ["First contact", result.outreach_messages.dm_first_contact],
                ["Day 7 follow-up", result.outreach_messages.dm_follow_up],
                ["Connection note", result.outreach_messages.connection_note],
              ].map(([title, text]) => (
                <div key={title} className="rounded-xl bg-zinc-950 p-4 border border-zinc-800">
                  <div className="mb-2 flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-blue-300">{title}</h3>
                    <button onClick={() => void copy(text as string)} className="text-zinc-500 hover:text-white p-2">
                      <Clipboard className="size-4" />
                    </button>
                  </div>
                  <p className="whitespace-pre-wrap text-sm leading-6 text-zinc-300">{text}</p>
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
              <div className="rounded-xl bg-zinc-950 p-4 border border-zinc-800">
                <div className="flex justify-between items-center mb-2">
                  <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500">Suggested headline</p>
                  <button onClick={() => void copy(result.profile_improvements!.headline_after)} className="text-zinc-500 hover:text-white">
                      <Clipboard className="size-4" />
                  </button>
                </div>
                <p className="text-sm leading-6 text-zinc-200">{result.profile_improvements.headline_after}</p>
              </div>
              <div className="rounded-xl bg-zinc-950 p-4 border border-zinc-800">
                <div className="flex justify-between items-center mb-2">
                  <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500">About section</p>
                  <button onClick={() => void copy(result.profile_improvements!.about_section)} className="text-zinc-500 hover:text-white">
                      <Clipboard className="size-4" />
                  </button>
                </div>
                <p className="whitespace-pre-wrap text-sm leading-6 text-zinc-300">{result.profile_improvements.about_section}</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </main>
  )
}
