import Link from "next/link"
import { ArrowRight, Lock, Sparkles, Target, Extension, Layers } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function Home() {
  return (
    <main className="min-h-screen bg-black text-white selection:bg-blue-500/30">
      {/* Navbar */}
      <nav className="fixed inset-x-0 top-0 z-50 border-b border-white/[0.08] bg-black/50 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
          <div className="flex items-center gap-2 font-semibold tracking-tight">
            <Sparkles className="size-5 text-blue-500" />
            ResumeMatch AI
          </div>
          <div className="flex items-center gap-4">
            <Link
              href="/login"
              className="text-sm font-medium text-zinc-400 transition-colors hover:text-white"
            >
              Sign in
            </Link>
            <Button asChild className="rounded-full bg-white text-black hover:bg-zinc-200">
              <Link href="/register">Get Started</Link>
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 sm:pt-40 sm:pb-24">
        <div className="mx-auto max-w-7xl px-6 text-center">
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-1000">
            <div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-sm font-medium text-zinc-300">
              <Lock className="size-3.5" />
              Local-first. Privacy-obsessed.
            </div>
            <h1 className="mx-auto max-w-4xl font-sans text-5xl font-bold tracking-tight sm:text-7xl">
              The Private Career Copilot{" "}
              <span className="bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
                for Top Performers.
              </span>
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-zinc-400 sm:text-xl">
              Stop guessing if your CV matches the job. ResumeMatch AI runs entirely on your private instances to analyze job descriptions, pinpoint missing skills, and draft hyper-personalized outreach.
            </p>
            <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Button
                asChild
                size="lg"
                className="h-12 w-full rounded-full bg-white px-8 text-base text-black hover:bg-zinc-200 sm:w-auto"
              >
                <Link href="/register">
                  Start Analyzing Now <ArrowRight className="ml-2 size-4" />
                </Link>
              </Button>
              <Button
                asChild
                variant="outline"
                size="lg"
                className="h-12 w-full rounded-full border-white/20 bg-transparent px-8 text-base text-white hover:bg-white/10 sm:w-auto"
              >
                <Link href="#features">View Demo</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Product Image Mockup */}
      <section className="relative mx-auto max-w-7xl px-6 pb-32">
        <div className="relative rounded-2xl border border-white/10 bg-black p-2 shadow-2xl ring-1 ring-white/10 animate-in fade-in zoom-in-95 duration-1000 delay-200 sm:p-4">
          <div className="absolute inset-0 -z-10 bg-gradient-to-b from-blue-500/20 to-transparent blur-3xl" />
          <div className="overflow-hidden rounded-xl border border-white/10 bg-zinc-950">
            {/* Fake Browser Top Bar */}
            <div className="flex h-12 items-center gap-2 border-b border-white/5 bg-zinc-900/50 px-4">
              <div className="flex gap-1.5">
                <div className="size-3 rounded-full bg-red-500/20 border border-red-500/50" />
                <div className="size-3 rounded-full bg-yellow-500/20 border border-yellow-500/50" />
                <div className="size-3 rounded-full bg-green-500/20 border border-green-500/50" />
              </div>
            </div>
            {/* Fake Dashboard Content */}
            <div className="grid aspect-video grid-cols-1 md:grid-cols-3 gap-px bg-white/5">
              <div className="col-span-1 bg-zinc-950 p-6 flex flex-col gap-4">
                <div className="h-8 w-32 rounded bg-white/10" />
                <div className="h-32 w-full rounded-lg bg-white/5 border border-white/5" />
                <div className="h-32 w-full rounded-lg bg-white/5 border border-white/5" />
                <div className="h-10 w-full rounded-full bg-blue-600/50" />
              </div>
              <div className="col-span-2 bg-zinc-950 p-8 flex flex-col gap-6">
                <div className="flex items-end gap-4">
                  <div className="text-6xl font-bold text-blue-400">92%</div>
                  <div className="text-zinc-500 pb-2">role match</div>
                </div>
                <div className="flex flex-wrap gap-2">
                  <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-sm text-emerald-400">React</span>
                  <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-sm text-emerald-400">FastAPI</span>
                  <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-sm text-emerald-400">PostgreSQL</span>
                </div>
                <div className="flex-1 rounded-xl bg-white/5 border border-white/5 p-6 space-y-3">
                  <div className="h-4 w-1/4 rounded bg-white/20" />
                  <div className="h-4 w-full rounded bg-white/10" />
                  <div className="h-4 w-5/6 rounded bg-white/10" />
                  <div className="h-4 w-4/6 rounded bg-white/10" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="bg-zinc-950 py-32">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mb-16 max-w-2xl">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Everything you need to secure the interview.
            </h2>
            <p className="mt-4 text-zinc-400 text-lg">
              We process your professional history to output highly targeted data, not generic ChatGPT responses.
            </p>
          </div>
          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {[
              {
                title: "Deep Semantic Matching",
                description: "Compares your CV against the Job Description to calculate a real match percentage.",
                icon: Target,
              },
              {
                title: "Drafted Outreach",
                description: "Generates personalized LinkedIn DMs and emails for the recruiter based on your unique strengths.",
                icon: Sparkles,
              },
              {
                title: "Chrome Extension",
                description: "Analyze any job post instantly on LinkedIn without leaving the browser tab.",
                icon: Extension, // Lucide doesn't have an Extension icon natively that matches, but we'll use Layers
              },
            ].map((feature) => (
              <div
                key={feature.title}
                className="group relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-8 transition hover:bg-white/[0.07]"
              >
                <div className="mb-4 inline-flex rounded-xl bg-blue-500/20 p-3 text-blue-400 ring-1 ring-blue-500/50">
                  <feature.icon className="size-6" />
                </div>
                <h3 className="mb-2 text-lg font-semibold">{feature.title}</h3>
                <p className="text-sm leading-relaxed text-zinc-400">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-10">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-6 sm:flex-row text-zinc-500 text-sm">
          <p>© {new Date().getFullYear()} ResumeMatch AI. All rights reserved.</p>
          <div className="flex gap-6">
            <Link href="/privacy" className="hover:text-white transition">Privacy</Link>
            <Link href="/terms" className="hover:text-white transition">Terms</Link>
          </div>
        </div>
      </footer>
    </main>
  )
}
