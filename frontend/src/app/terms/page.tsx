import Link from "next/link"
import { ArrowLeft } from "lucide-react"

export default function TermsPage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-20 text-zinc-300">
      <Link href="/" className="mb-8 inline-flex items-center gap-2 text-sm text-zinc-500 hover:text-white transition">
        <ArrowLeft className="size-4" /> Back
      </Link>
      <h1 className="text-4xl font-bold text-white mb-8">Terms of Service</h1>
      <div className="space-y-6 leading-relaxed">
        <p>By using ResumeMatch AI, you agree to these terms.</p>
        <h2 className="text-2xl font-semibold text-white mt-8">1. Service Description</h2>
        <p>ResumeMatch AI is an AI-powered career assistant. The generated outreach messages and match scores are suggestions based on LLM outputs and do not guarantee employment.</p>
        <h2 className="text-2xl font-semibold text-white mt-8">2. User Responsibilities</h2>
        <p>You are responsible for ensuring that the data you provide does not violate any third-party confidentiality agreements. You agree not to misuse the Chrome Extension to scrape LinkedIn automatically.</p>
        <h2 className="text-2xl font-semibold text-white mt-8">3. Open Source</h2>
        <p>This software is provided &quot;as is&quot;, without warranty of any kind. You are free to self-host and modify the source code under the MIT License.</p>
      </div>
    </main>
  )
}
