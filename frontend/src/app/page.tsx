import Image from "next/image"
import Link from "next/link"
import {
  ArrowRight,
  Blocks,
  Check,
  ChevronRight,
  CircleGauge,
  Code2,
  GitFork,
  Globe2,
  LockKeyhole,
  MessagesSquare,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  TerminalSquare,
  Zap,
} from "lucide-react"

import { BrandMark } from "@/components/brand-mark"
import { ProductPreview } from "@/components/product-preview"
import { Button } from "@/components/ui/button"

const features = [
  {
    icon: ScanSearch,
    title: "Explainable matching",
    description:
      "See exactly which skills created the score, what is missing, and where your CV needs sharper evidence.",
    accent: "from-[#7181ff]/20 to-transparent",
  },
  {
    icon: MessagesSquare,
    title: "Outreach that sounds like you",
    description:
      "Turn your real experience into editable recruiter messages, connection notes, and thoughtful follow-ups.",
    accent: "from-[#a376ff]/20 to-transparent",
  },
  {
    icon: LockKeyhole,
    title: "Private by architecture",
    description:
      "Redact PII before cloud inference, or keep the entire workflow on your machine with Ollama.",
    accent: "from-[#58d0bc]/20 to-transparent",
  },
]

const stack = ["Next.js 16", "FastAPI", "PostgreSQL", "Redis", "Celery", "Groq", "Ollama"]

export default function Home() {
  return (
    <main className="overflow-hidden bg-[#080a0f] text-white">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-[940px] overflow-hidden">
        <div className="marketing-grid absolute inset-0" />
        <div className="hero-glow absolute inset-0" />
      </div>

      <nav className="fixed inset-x-0 top-0 z-50 px-4 pt-4">
        <div className="glass-nav mx-auto flex h-[58px] max-w-6xl items-center justify-between rounded-2xl px-4 sm:px-5">
          <Link href="/" aria-label="NetworkForge home">
            <BrandMark />
          </Link>
          <div className="hidden items-center gap-7 text-[13px] text-zinc-400 md:flex">
            <a href="#product" className="transition hover:text-white">Product</a>
            <a href="#privacy" className="transition hover:text-white">Privacy</a>
            <a href="#open-source" className="transition hover:text-white">Open source</a>
          </div>
          <div className="flex items-center gap-1.5 sm:gap-2">
            <Button asChild variant="ghost" size="sm" className="hidden sm:inline-flex">
              <Link href="/login">Sign in</Link>
            </Button>
            <Button asChild size="sm" className="rounded-lg px-3.5">
              <Link href="/login">
                Start free <ArrowRight className="size-3.5" />
              </Link>
            </Button>
          </div>
        </div>
      </nav>

      <section className="relative mx-auto max-w-7xl px-5 pb-20 pt-36 sm:px-8 sm:pb-28 sm:pt-44">
        <div className="mx-auto max-w-4xl text-center">
          <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5 text-[12px] font-medium text-zinc-300 shadow-2xl shadow-black/20 backdrop-blur">
            <span className="relative flex size-2">
              <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-50" />
              <span className="relative inline-flex size-2 rounded-full bg-emerald-400" />
            </span>
            Open source · Local-first · Built for real job searches
          </div>
          <h1 className="text-balance text-[3.2rem] font-semibold leading-[0.98] tracking-[-0.065em] text-[#f7f7f8] sm:text-7xl lg:text-[5.65rem]">
            Make your experience
            <span className="block bg-gradient-to-r from-[#aeb7ff] via-[#7d8cff] to-[#ad7eff] bg-clip-text text-transparent">
              impossible to overlook.
            </span>
          </h1>
          <p className="text-balance mx-auto mt-7 max-w-2xl text-base leading-7 text-zinc-400 sm:text-lg sm:leading-8">
            NetworkForge turns a CV and job description into a precise opportunity map—then helps you close the gap with better positioning and personal outreach.
          </p>
          <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Button asChild size="lg" className="w-full px-7 sm:w-auto">
              <Link href="/login">
                Analyze your first role <ArrowRight className="size-4" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="w-full px-7 sm:w-auto">
              <Link href="/dashboard/analysis/demo">
                Explore the demo <ChevronRight className="size-4" />
              </Link>
            </Button>
          </div>
          <p className="mt-4 flex items-center justify-center gap-2 text-[11px] text-zinc-600">
            <ShieldCheck className="size-3.5 text-emerald-500" />
            Self-host in minutes. Your career data stays under your control.
          </p>
        </div>

        <div id="product" className="relative mx-auto mt-20 max-w-6xl sm:mt-24">
          <div className="absolute -inset-20 -z-10 bg-[radial-gradient(circle,rgba(88,104,238,.18),transparent_62%)] blur-2xl" />
          <ProductPreview />
        </div>
      </section>

      <section className="border-y border-white/[0.07] bg-white/[0.018]">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-5 px-6 py-7 sm:flex-row">
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-zinc-600">Built on a serious stack</p>
          <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-3">
            {stack.map((item) => (
              <span key={item} className="text-xs font-medium text-zinc-400">{item}</span>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 py-28 sm:px-8 sm:py-36">
        <div className="grid items-end gap-8 lg:grid-cols-[1fr_.7fr]">
          <div>
            <p className="eyebrow text-[#8390ff]">The unfair clarity advantage</p>
            <h2 className="text-balance mt-4 max-w-2xl text-4xl font-semibold leading-[1.06] tracking-[-0.05em] sm:text-5xl">
              Not another black-box AI score.
            </h2>
          </div>
          <p className="max-w-xl text-sm leading-7 text-zinc-500 lg:pb-1">
            Every output is grounded in your source material. NetworkForge separates extraction, scoring, and generation so you can understand—and edit—every recommendation.
          </p>
        </div>

        <div className="mt-14 grid gap-4 lg:grid-cols-3">
          {features.map((feature) => (
            <article
              key={feature.title}
              className="group relative min-h-[280px] overflow-hidden rounded-[1.35rem] border border-white/[0.08] bg-[#0e1118] p-7 transition duration-300 hover:-translate-y-1 hover:border-white/[0.15]"
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${feature.accent} opacity-55 transition group-hover:opacity-100`} />
              <div className="relative flex h-full flex-col">
                <span className="flex size-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.055] text-zinc-200">
                  <feature.icon className="size-4.5" />
                </span>
                <div className="mt-auto pt-20">
                  <h3 className="text-lg font-semibold tracking-[-0.025em]">{feature.title}</h3>
                  <p className="mt-3 text-sm leading-6 text-zinc-500">{feature.description}</p>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section id="privacy" className="relative border-y border-white/[0.07] bg-[#0a0c11]">
        <div className="mx-auto grid max-w-6xl items-center gap-12 px-5 py-24 sm:px-8 sm:py-32 lg:grid-cols-2">
          <div className="relative overflow-hidden rounded-[1.5rem] border border-white/[0.09] bg-[#0d1016]">
            <div className="absolute inset-0">
              <Image
                src="/brand/networkforge-hero.png"
                alt=""
                fill
                sizes="(max-width: 1024px) 100vw, 50vw"
                className="object-cover opacity-75"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#0d1016] via-transparent to-transparent" />
            </div>
            <div className="relative flex min-h-[470px] flex-col justify-end p-7 sm:p-9">
              <div className="max-w-sm rounded-2xl border border-white/10 bg-black/40 p-5 shadow-2xl backdrop-blur-xl">
                <div className="mb-4 flex items-center justify-between">
                  <span className="flex items-center gap-2 text-xs font-medium text-zinc-200">
                    <ShieldCheck className="size-4 text-emerald-400" />
                    Privacy pipeline
                  </span>
                  <span className="font-mono text-[10px] text-emerald-400">ACTIVE</span>
                </div>
                {["Parse locally", "Redact personal data", "Route to your provider"].map((item, index) => (
                  <div key={item} className="flex items-center gap-3 border-t border-white/[0.07] py-3 text-xs text-zinc-400">
                    <span className="flex size-5 items-center justify-center rounded-full bg-emerald-400/10 text-[9px] text-emerald-300">
                      {index + 1}
                    </span>
                    {item}
                    <Check className="ml-auto size-3.5 text-emerald-400" />
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div>
            <p className="eyebrow text-emerald-400">Privacy is a feature</p>
            <h2 className="text-balance mt-4 text-4xl font-semibold leading-[1.05] tracking-[-0.05em] sm:text-5xl">
              Your CV is not training data.
            </h2>
            <p className="mt-6 max-w-xl text-base leading-8 text-zinc-400">
              Run locally with Ollama, choose Groq for speed, and keep ownership of every byte. PII redaction happens before cloud inference—not after.
            </p>
            <div className="mt-8 space-y-4">
              {[
                [TerminalSquare, "Local Ollama inference"],
                [ShieldCheck, "PII redaction before LLM calls"],
                [Code2, "Auditable, MIT-licensed source"],
              ].map(([Icon, label]) => {
                const ItemIcon = Icon
                return (
                  <div key={label as string} className="flex items-center gap-3 text-sm text-zinc-300">
                    <span className="flex size-8 items-center justify-center rounded-lg bg-white/[0.05]">
                      <ItemIcon className="size-4 text-zinc-400" />
                    </span>
                    {label as string}
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </section>

      <section id="open-source" className="mx-auto max-w-6xl px-5 py-28 sm:px-8 sm:py-36">
        <div className="overflow-hidden rounded-[1.75rem] border border-white/[0.09] bg-gradient-to-br from-[#151927] via-[#10131b] to-[#0c0e13]">
          <div className="grid lg:grid-cols-[1.1fr_.9fr]">
            <div className="p-8 sm:p-12 lg:p-14">
              <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5 text-xs text-zinc-400">
                <GitFork className="size-3.5" /> Made in public
              </div>
              <h2 className="text-balance max-w-xl text-4xl font-semibold leading-[1.05] tracking-[-0.05em] sm:text-5xl">
                Own the engine behind your next move.
              </h2>
              <p className="mt-6 max-w-xl text-sm leading-7 text-zinc-400">
                Inspect it, self-host it, extend it. NetworkForge is an open foundation for privacy-first career intelligence—not a subscription-shaped black box.
              </p>
              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Button asChild size="lg">
                  <a href="https://github.com/ardamoustafa1/NetworkForge" target="_blank" rel="noreferrer">
                    <GitFork className="size-4" /> Star on GitHub
                  </a>
                </Button>
                <Button asChild variant="outline" size="lg">
                  <a href="https://github.com/ardamoustafa1/NetworkForge#-quick-start" target="_blank" rel="noreferrer">
                    Read the docs
                  </a>
                </Button>
              </div>
            </div>
            <div className="relative min-h-[360px] border-t border-white/[0.07] bg-black/20 p-7 lg:border-l lg:border-t-0">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_20%,rgba(108,124,255,.2),transparent_42%)]" />
              <div className="relative rounded-2xl border border-white/[0.09] bg-[#080a0f]/90 p-5 shadow-2xl">
                <div className="mb-5 flex items-center gap-2 border-b border-white/[0.07] pb-4 text-[11px] text-zinc-500">
                  <TerminalSquare className="size-3.5" /> terminal
                </div>
                <pre className="overflow-x-auto font-mono text-[11px] leading-6 text-zinc-400">
                  <code>
                    <span className="text-[#91a0ff]">$</span> git clone networkforge{"\n"}
                    <span className="text-[#91a0ff]">$</span> cp .env.example .env{"\n"}
                    <span className="text-[#91a0ff]">$</span> docker compose up --build{"\n\n"}
                    <span className="text-emerald-400">✓</span> frontend ready :3000{"\n"}
                    <span className="text-emerald-400">✓</span> api ready      :8000{"\n"}
                    <span className="text-emerald-400">✓</span> worker online{"\n"}
                  </code>
                </pre>
              </div>
              <div className="relative mt-4 grid grid-cols-2 gap-3">
                {[
                  [Blocks, "Modular"],
                  [CircleGauge, "Observable"],
                  [Globe2, "Multilingual"],
                  [Zap, "Fast"],
                ].map(([Icon, label]) => {
                  const ItemIcon = Icon
                  return (
                    <div key={label as string} className="flex items-center gap-2 rounded-xl border border-white/[0.07] bg-white/[0.025] p-3 text-xs text-zinc-400">
                      <ItemIcon className="size-3.5 text-[#8e9aff]" />
                      {label as string}
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-t border-white/[0.07] px-5 py-24 text-center sm:px-8 sm:py-28">
        <div className="mx-auto max-w-3xl">
          <Sparkles className="mx-auto size-6 text-[#8e9aff]" />
          <h2 className="text-balance mt-6 text-4xl font-semibold tracking-[-0.05em] sm:text-5xl">
            Your next application deserves better than guesswork.
          </h2>
          <p className="mx-auto mt-5 max-w-xl text-sm leading-7 text-zinc-500">
            Bring one role. Leave with clarity, positioning, and a message worth replying to.
          </p>
          <Button asChild size="lg" className="mt-8">
            <Link href="/login">
              Start with NetworkForge <ArrowRight className="size-4" />
            </Link>
          </Button>
        </div>
      </section>

      <footer className="border-t border-white/[0.07]">
        <div className="mx-auto flex max-w-6xl flex-col gap-6 px-5 py-9 sm:flex-row sm:items-center sm:justify-between sm:px-8">
          <BrandMark />
          <div className="flex flex-wrap gap-5 text-xs text-zinc-600">
            <Link href="/privacy" className="transition hover:text-zinc-300">Privacy</Link>
            <Link href="/terms" className="transition hover:text-zinc-300">Terms</Link>
            <a href="mailto:security@networkforge.io" className="transition hover:text-zinc-300">Security</a>
            <span>© {new Date().getFullYear()} NetworkForge</span>
          </div>
        </div>
      </footer>
    </main>
  )
}
