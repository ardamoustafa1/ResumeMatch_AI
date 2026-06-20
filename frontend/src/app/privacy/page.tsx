import Link from "next/link"
import { ArrowLeft } from "lucide-react"

export default function PrivacyPage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-20 text-zinc-300">
      <Link href="/" className="mb-8 inline-flex items-center gap-2 text-sm text-zinc-500 hover:text-white transition">
        <ArrowLeft className="size-4" /> Back
      </Link>
      <h1 className="text-4xl font-bold text-white mb-8">Privacy Policy</h1>
      <div className="space-y-6 leading-relaxed">
        <p>Your privacy is our primary concern. ResumeMatch AI operates on a local-first philosophy.</p>
        <h2 className="text-2xl font-semibold text-white mt-8">1. Data Collection</h2>
        <p>We collect your email address for account creation. We process uploaded CVs and job descriptions exclusively to generate match scores and outreach templates.</p>
        <h2 className="text-2xl font-semibold text-white mt-8">2. Data Usage & AI Processing</h2>
        <p>Before any data is sent to external AI providers (such as Groq or OpenAI), we actively strip out personally identifiable information (PII) including email addresses and phone numbers. If you configure a local provider like Ollama, your data never leaves your environment.</p>
        <h2 className="text-2xl font-semibold text-white mt-8">3. Data Retention</h2>
        <p>All analysis data is ephemeral. We run automated retention jobs that purge historical analyses after 30 days. You may also delete your data manually at any time via the dashboard.</p>
      </div>
    </main>
  )
}
