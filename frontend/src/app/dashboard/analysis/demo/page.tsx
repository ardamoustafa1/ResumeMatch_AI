"use client"

import Link from "next/link"
import { ArrowLeft } from "lucide-react"
import { ResultsPanel } from "@/components/dashboard/ResultsPanel"
import { BrandMark } from "@/components/brand-mark"
import type { FullAnalysisResult } from "@/lib/types"

const MOCK_RESULT: FullAnalysisResult = {
  match_result: {
    score: 85,
    matched_skills: ["Python", "FastAPI", "React", "PostgreSQL", "Docker", "AWS"],
    missing_skills: ["Kubernetes", "GraphQL"],
    improvement_suggestions: [
      "Highlight your recent experience migrating to AWS ECS since Kubernetes is missing.",
      "Add any GraphQL hobby projects to bridge the gap."
    ]
  },
  outreach_messages: {
    dm_first_contact: "Hi there, I noticed TechCorp is looking for a Senior Backend Engineer. With 5 years of experience building scalable systems using Python and FastAPI, I'm confident I can make an immediate impact.",
    dm_follow_up: "Hi again, just bubbling this up! Would love to chat about the backend role.",
    connection_note: "Hi! I'm a Senior Backend Engineer experienced in Python/React and saw the opening at TechCorp. I'd love to connect!"
  },
  profile_improvements: {
    headline_before: "Software Engineer",
    headline_after: "Senior Full Stack Engineer | Python, React, AWS",
    about_section: "I am a results-oriented Senior Backend Engineer with a passion for building robust APIs and scalable microservices. With over 5 years of experience working heavily in the Python ecosystem..."
  },
  errors: {}
}

export default function DemoPage() {
  async function copy(text: string) {
    await navigator.clipboard.writeText(text)
  }

  return (
    <main className="dashboard-shell text-white">
      <header className="border-b border-white/[0.07] bg-[#080a0f]/80 backdrop-blur-2xl">
        <div className="mx-auto flex h-[68px] max-w-7xl items-center justify-between px-5 sm:px-6">
          <div className="flex items-center gap-3">
            <BrandMark />
            <span className="rounded-full border border-[#7483ff]/20 bg-[#7483ff]/10 px-2 py-0.5 text-[10px] font-medium text-[#9ba6ff]">Demo</span>
          </div>
          <Link href="/" className="flex items-center gap-2 text-xs text-zinc-500 transition hover:text-white">
            <ArrowLeft className="size-4" /> Back to Home
          </Link>
        </div>
      </header>
      <div className="mx-auto max-w-4xl px-5 py-12 sm:px-6 sm:py-16">
        <div className="mb-9 text-center">
          <p className="eyebrow text-[#8995ff]">Live product preview</p>
          <h1 className="mt-3 text-4xl font-semibold tracking-[-0.05em]">See the signal, not just the score.</h1>
          <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-zinc-500">A representative NetworkForge result using sample career data.</p>
        </div>
        <ResultsPanel result={MOCK_RESULT} copy={copy} />
      </div>
    </main>
  )
}
