import {
  ArrowUpRight,
  Check,
  FileText,
  LockKeyhole,
  MessageSquareText,
  Sparkles,
} from "lucide-react"

export function ProductPreview() {
  return (
    <div className="product-window">
      <div className="product-window-bar">
        <div className="flex gap-1.5" aria-hidden="true">
          <span className="window-dot bg-[#ff5f57]" />
          <span className="window-dot bg-[#febc2e]" />
          <span className="window-dot bg-[#28c840]" />
        </div>
        <div className="window-address">
          <LockKeyhole className="size-3" />
          app.networkforge.dev
        </div>
        <div className="w-12" />
      </div>

      <div className="grid min-h-[440px] lg:grid-cols-[240px_1fr]">
        <aside className="hidden border-r border-white/[0.07] bg-[#0b0d12] p-5 lg:block">
          <div className="mb-8 flex items-center gap-2.5">
            <span className="flex size-7 items-center justify-center rounded-lg bg-[#6c7cff] text-white">
              <Sparkles className="size-3.5" />
            </span>
            <span className="text-xs font-semibold">NetworkForge</span>
          </div>
          <p className="eyebrow mb-3">Workspace</p>
          <div className="space-y-1.5">
            <div className="preview-nav preview-nav-active">
              <FileText className="size-3.5" /> New analysis
            </div>
            <div className="preview-nav">
              <MessageSquareText className="size-3.5" /> Outreach
            </div>
          </div>
          <div className="mt-8 rounded-xl border border-white/[0.07] bg-white/[0.025] p-3">
            <div className="mb-2 flex items-center gap-2 text-[10px] font-medium text-zinc-300">
              <LockKeyhole className="size-3 text-emerald-400" />
              Privacy shield
            </div>
            <div className="h-1 overflow-hidden rounded-full bg-white/5">
              <div className="h-full w-[88%] rounded-full bg-emerald-400" />
            </div>
            <p className="mt-2 text-[9px] leading-4 text-zinc-600">PII redaction active</p>
          </div>
        </aside>

        <div className="bg-[#090b10] p-4 sm:p-6 lg:p-7">
          <div className="mb-6 flex items-start justify-between gap-4">
            <div>
              <p className="eyebrow">Analysis / Senior product engineer</p>
              <h3 className="mt-2 text-lg font-semibold tracking-tight text-white">
                Your opportunity map
              </h3>
            </div>
            <span className="rounded-full border border-emerald-400/20 bg-emerald-400/[0.08] px-2.5 py-1 text-[10px] font-medium text-emerald-300">
              Complete
            </span>
          </div>

          <div className="grid gap-3 sm:grid-cols-[0.85fr_1.15fr]">
            <div className="preview-panel flex flex-col justify-between">
              <div>
                <p className="eyebrow">Role match</p>
                <div className="mt-4 flex items-end gap-2">
                  <span className="text-5xl font-semibold tracking-[-0.06em] text-white">92</span>
                  <span className="mb-1.5 text-lg text-zinc-500">/100</span>
                </div>
                <p className="mt-2 text-[11px] leading-5 text-zinc-500">
                  Excellent fit. Your backend depth is the strongest signal.
                </p>
              </div>
              <div className="mt-6 flex items-end gap-1">
                {[35, 48, 43, 64, 58, 78, 71, 92].map((height, index) => (
                  <span
                    key={height}
                    className={index === 7 ? "preview-bar preview-bar-active" : "preview-bar"}
                    style={{ height: `${height * 0.44}px` }}
                  />
                ))}
              </div>
            </div>

            <div className="preview-panel">
              <div className="flex items-center justify-between">
                <p className="eyebrow">Signal breakdown</p>
                <ArrowUpRight className="size-3.5 text-zinc-600" />
              </div>
              <div className="mt-5 space-y-4">
                {[
                  ["Core skills", 96, "bg-[#7887ff]"],
                  ["Experience", 91, "bg-[#9b7cff]"],
                  ["Domain", 84, "bg-[#6dd6c7]"],
                ].map(([label, score, color]) => (
                  <div key={label}>
                    <div className="mb-2 flex justify-between text-[10px]">
                      <span className="text-zinc-400">{label}</span>
                      <span className="font-mono text-zinc-500">{score}%</span>
                    </div>
                    <div className="h-1 overflow-hidden rounded-full bg-white/[0.06]">
                      <div className={`h-full rounded-full ${color}`} style={{ width: `${score}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="preview-panel mt-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="eyebrow">Recommended positioning</p>
                <p className="mt-1 text-xs font-medium text-zinc-200">
                  Lead with systems ownership, not just implementation.
                </p>
              </div>
              <span className="flex size-7 items-center justify-center rounded-lg bg-[#6c7cff]/15 text-[#9aa5ff]">
                <Sparkles className="size-3.5" />
              </span>
            </div>
            <div className="mt-4 grid gap-2 sm:grid-cols-3">
              {["FastAPI", "PostgreSQL", "Distributed systems"].map((skill) => (
                <div key={skill} className="flex items-center gap-2 rounded-lg bg-white/[0.035] px-3 py-2 text-[10px] text-zinc-300">
                  <Check className="size-3 text-emerald-400" />
                  {skill}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
