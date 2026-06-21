import { ChevronDown, FileText, FileUp, LoaderCircle, LockKeyhole, Sparkles, Target } from "lucide-react"
import { Button } from "@/components/ui/button"

interface AnalysisFormProps {
  company: string
  setCompany: (v: string) => void
  recruiterName: string
  setRecruiterName: (v: string) => void
  provider: string
  setProvider: (v: string) => void
  language: string
  setLanguage: (v: string) => void
  scoringStrategy: string
  setScoringStrategy: (v: string) => void
  cvText: string
  setCvText: (v: string) => void
  jdText: string
  setJdText: (v: string) => void
  uploading: boolean
  analyzing: boolean
  uploadCv: (file: File | undefined) => Promise<void>
  startAnalysis: () => Promise<void>
}

export function AnalysisForm({
  company, setCompany, recruiterName, setRecruiterName,
  provider, setProvider, language, setLanguage,
  scoringStrategy, setScoringStrategy,
  cvText, setCvText, jdText, setJdText,
  uploading, analyzing, uploadCv, startAnalysis
}: AnalysisFormProps) {
  const cvProgress = Math.min(100, Math.round((cvText.trim().length / 100) * 100))
  const jdProgress = Math.min(100, Math.round((jdText.trim().length / 50) * 100))

  return (
    <section className="dashboard-card overflow-hidden">
      <div className="flex items-start justify-between gap-4 border-b border-white/[0.07] p-5 sm:p-6">
        <div>
          <div className="mb-2 flex items-center gap-2">
            <span className="eyebrow text-[#8995ff]">New opportunity</span>
            <span className="size-1 rounded-full bg-zinc-700" />
            <span className="text-[10px] text-zinc-600">~45 seconds</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-[-0.045em] text-white">Build your opportunity map</h1>
          <p className="mt-2 max-w-xl text-sm leading-6 text-zinc-500">
            Add your experience and the role. NetworkForge will show where you stand and what to do next.
          </p>
        </div>
        <span className="hidden size-10 shrink-0 items-center justify-center rounded-xl border border-white/[0.08] bg-white/[0.04] text-[#8e9aff] sm:flex">
          <Sparkles className="size-4.5" />
        </span>
      </div>

      <div className="space-y-5 p-5 sm:p-6">
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="group block">
            <span className="mb-2 block text-xs font-medium text-zinc-400">Company <span className="text-zinc-700">optional</span></span>
            <input value={company} onChange={(e) => setCompany(e.target.value)} className="field" placeholder="e.g. Linear" />
          </label>
          <label className="group block">
            <span className="mb-2 block text-xs font-medium text-zinc-400">Recruiter <span className="text-zinc-700">optional</span></span>
            <input value={recruiterName} onChange={(e) => setRecruiterName(e.target.value)} className="field" placeholder="e.g. Maya" />
          </label>
        </div>

        <div className="grid gap-3 lg:grid-cols-2">
          <div className="rounded-2xl border border-white/[0.075] bg-black/20 p-4">
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="flex size-7 items-center justify-center rounded-lg bg-[#6c7cff]/10 text-[#8f9aff]">
                  <FileText className="size-3.5" />
                </span>
                <span className="text-xs font-semibold text-zinc-300">Your experience</span>
              </div>
              <span className="font-mono text-[9px] text-zinc-600">{cvText.length} chars</span>
            </div>
            <textarea
              value={cvText}
              onChange={(e) => setCvText(e.target.value)}
              className="field min-h-56 resize-y text-sm leading-6"
              placeholder="Paste your CV or résumé text here…"
            />
            <div className="mt-3 flex items-center gap-3">
              <label className="flex flex-1 cursor-pointer items-center justify-center gap-2 rounded-xl border border-dashed border-white/[0.1] bg-white/[0.02] px-3 py-2.5 text-[11px] text-zinc-500 transition hover:border-[#7887ff]/50 hover:bg-[#6c7cff]/5 hover:text-zinc-300">
                {uploading ? <LoaderCircle className="size-3.5 animate-spin" /> : <FileUp className="size-3.5" />}
                {uploading ? "Extracting…" : "Upload PDF or image"}
                <input type="file" accept=".pdf,.png,.jpg,.jpeg" className="sr-only" onChange={(e) => void uploadCv(e.target.files?.[0])} disabled={uploading} />
              </label>
              <span className={cvProgress >= 100 ? "text-[10px] text-emerald-400" : "text-[10px] text-zinc-600"}>
                {cvProgress >= 100 ? "Ready" : "100+ chars"}
              </span>
            </div>
          </div>

          <div className="rounded-2xl border border-white/[0.075] bg-black/20 p-4">
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="flex size-7 items-center justify-center rounded-lg bg-violet-400/10 text-violet-300">
                  <Target className="size-3.5" />
                </span>
                <span className="text-xs font-semibold text-zinc-300">Target role</span>
              </div>
              <span className="font-mono text-[9px] text-zinc-600">{jdText.length} chars</span>
            </div>
            <textarea
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              className="field min-h-[17.25rem] resize-y text-sm leading-6"
              placeholder="Paste the full job description here…"
            />
            <div className="mt-3 flex justify-end">
              <span className={jdProgress >= 100 ? "text-[10px] text-emerald-400" : "text-[10px] text-zinc-600"}>
                {jdProgress >= 100 ? "Ready" : "50+ chars"}
              </span>
            </div>
          </div>
        </div>

        <details className="group rounded-xl border border-white/[0.07] bg-white/[0.018]">
          <summary className="flex cursor-pointer list-none items-center justify-between px-4 py-3 text-xs font-medium text-zinc-400">
            <span>Analysis preferences</span>
            <ChevronDown className="size-3.5 transition group-open:rotate-180" />
          </summary>
          <div className="grid gap-3 border-t border-white/[0.07] p-4 sm:grid-cols-2">
            <label className="block">
              <span className="mb-2 block text-[11px] text-zinc-500">AI provider</span>
              <select value={provider} onChange={(e) => setProvider(e.target.value)} className="field appearance-none">
                <option value="auto">Auto · fastest available</option>
                <option value="groq">Groq · fast cloud</option>
                <option value="ollama">Ollama · private local</option>
                <option value="openai">OpenAI · GPT-4o (if configured)</option>
                <option value="anthropic">Anthropic · Claude 3 (if configured)</option>
              </select>
            </label>
            <label className="block">
              <span className="mb-2 block text-[11px] text-zinc-500">Output language</span>
              <select value={language} onChange={(e) => setLanguage(e.target.value)} className="field appearance-none">
                <option value="English">English</option>
                <option value="Turkish">Turkish</option>
                <option value="Spanish">Spanish</option>
                <option value="French">French</option>
                <option value="German">German</option>
              </select>
            </label>
            <label className="block sm:col-span-2">
              <span className="mb-2 block text-[11px] text-zinc-500">Scoring Strategy</span>
              <select value={scoringStrategy} onChange={(e) => setScoringStrategy(e.target.value)} className="field appearance-none">
                <option value="default">Default · Standard Math Curve Penalty</option>
                <option value="strict_keyword">Strict Keyword · Harsh Missing Penalty</option>
              </select>
            </label>
          </div>
        </details>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="flex items-center gap-2 text-[10px] leading-5 text-zinc-600">
            <LockKeyhole className="size-3.5 text-emerald-500" />
            Personal identifiers are redacted before cloud inference.
          </p>
          <Button onClick={() => void startAnalysis()} disabled={analyzing} className="h-11 px-5 sm:min-w-48">
            {analyzing ? <LoaderCircle className="size-4 animate-spin" /> : <Sparkles className="size-4" />}
            {analyzing ? "Building your map…" : "Analyze opportunity"}
          </Button>
        </div>
      </div>
    </section>
  )
}
