import { Check, Clipboard, TriangleAlert, Printer, Sparkles, Target, WandSparkles } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { motion } from "framer-motion"
import { RadialGauge } from "./RadialGauge"
import type { FullAnalysisResult } from "@/lib/types"

export function CopyButton({ text, copy }: { text: string; copy: (value: string) => Promise<void> }) {
  return (
    <button
      onClick={() => void copy(text)}
      className="rounded-lg border border-transparent p-2 text-zinc-600 transition hover:border-white/[0.08] hover:bg-white/[0.05] hover:text-white"
      aria-label="Copy text"
    >
      <Clipboard className="size-4" />
    </button>
  )
}

function SkillList({ title, items, positive = false }: { title: string; items: string[]; positive?: boolean }) {
  return (
    <div>
      <h3 className="mb-3 text-xs font-semibold text-zinc-400">{title}</h3>
      <motion.div 
        initial="hidden" 
        animate="show" 
        variants={{
          hidden: { opacity: 0 },
          show: { opacity: 1, transition: { staggerChildren: 0.05 } }
        }}
        className="flex flex-wrap gap-2"
      >
        {items.length ? (
          items.map((item) => (
            <motion.span
              key={item}
              variants={{
                hidden: { opacity: 0, scale: 0.8 },
                show: { opacity: 1, scale: 1 }
              }}
              whileHover={{ scale: 1.05 }}
              className={
                positive
                  ? "rounded-full border border-emerald-400/10 bg-emerald-400/[0.07] px-3 py-1.5 text-[11px] text-emerald-300"
                  : "rounded-full border border-amber-400/10 bg-amber-400/[0.07] px-3 py-1.5 text-[11px] text-amber-300"
              }
            >
              {item}
            </motion.span>
          ))
        ) : (
          <span className="text-sm text-zinc-500">None identified</span>
        )}
      </motion.div>
    </div>
  )
}

export function ResultsPanel({ result, copy }: { result: FullAnalysisResult; copy: (value: string) => Promise<void> }) {
  const match = result.match_result
  return (
    <div className="space-y-5">
      {result.errors && Object.keys(result.errors).length > 0 && (
        <div className="flex gap-3 rounded-xl border border-amber-800/60 bg-amber-950/30 p-4 text-sm text-amber-200">
          <TriangleAlert className="mt-0.5 size-4 shrink-0" />
          Some optional sections could not be generated. The available results are shown below.
        </div>
      )}
      {match && (
        <Card className="overflow-hidden border-[#7483ff]/20">
          <CardHeader className="flex flex-row items-start justify-between border-b border-white/[0.07]">
            <CardTitle className="flex items-center gap-5">
              <RadialGauge score={match.score} size={88} strokeWidth={7} />
              <span>
                <span className="eyebrow block text-[#8995ff]">Opportunity intelligence</span>
                <span className="mt-2 block text-xl text-zinc-200">Role match</span>
                <span className="mt-1 block text-xs font-normal tracking-normal text-zinc-600">Evidence-backed, not a black-box score</span>
              </span>
            </CardTitle>
            <button 
              onClick={() => window.print()}
              className="no-print flex items-center gap-2 rounded-lg border border-white/[0.08] bg-white/[0.04] px-3 py-2 text-[11px] text-zinc-400 transition hover:bg-white/[0.08] hover:text-white"
            >
              <Printer className="size-3.5" /> Export
            </button>
          </CardHeader>
          <CardContent className="space-y-6 pt-6">
            <div className="grid gap-5 sm:grid-cols-2">
              <SkillList title="Strong signals" items={match.matched_skills} positive />
              <SkillList title="Opportunity gaps" items={match.missing_skills} />
            </div>
            <div className="rounded-2xl border border-white/[0.07] bg-black/20 p-4">
              <h3 className="mb-3 flex items-center gap-2 text-xs font-semibold text-zinc-300">
                <Target className="size-3.5 text-[#8f9aff]" /> Highest-impact improvements
              </h3>
              <ul className="space-y-3 text-xs leading-5 text-zinc-400">
                {match.improvement_suggestions.map((item) => (
                  <li key={item} className="flex gap-2">
                    <Check className="mt-0.5 size-3.5 shrink-0 text-emerald-400" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
      )}

      {result.outreach_messages && (
        <Card className="overflow-hidden">
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Sparkles className="size-4 text-violet-300" /> Outreach drafts</CardTitle>
            <CardDescription>Review and personalize these drafts before sending.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {[
              ["First contact", result.outreach_messages.dm_first_contact],
              ["Day 7 follow-up", result.outreach_messages.dm_follow_up],
              ["Connection note", result.outreach_messages.connection_note],
            ].map(([title, text]) => (
              <div key={title} className="rounded-xl border border-white/[0.07] bg-black/20 p-4">
                <div className="mb-2 flex items-center justify-between">
                  <h3 className="text-xs font-semibold text-[#a8b1ff]">{title}</h3>
                  <CopyButton text={text} copy={copy} />
                </div>
                <p className="whitespace-pre-wrap text-sm leading-6 text-zinc-400">{text}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {result.profile_improvements && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><WandSparkles className="size-4 text-cyan-300" /> Profile improvements</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-xl border border-white/[0.07] bg-black/20 p-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500">Suggested headline</p>
              <div className="mt-2 flex items-start justify-between gap-3">
                <p className="text-sm leading-6 text-zinc-200">{result.profile_improvements.headline_after}</p>
                <CopyButton text={result.profile_improvements.headline_after} copy={copy} />
              </div>
            </div>
            <div className="rounded-xl border border-white/[0.07] bg-black/20 p-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500">About section</p>
              <div className="mt-2 flex items-start justify-between gap-3">
                <p className="whitespace-pre-wrap text-sm leading-6 text-zinc-300">{result.profile_improvements.about_section}</p>
                <CopyButton text={result.profile_improvements.about_section} copy={copy} />
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
