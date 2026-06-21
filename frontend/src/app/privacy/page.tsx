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
        <p>Last Updated: June 21, 2026</p>
        <p>Your privacy is our primary concern. NetworkForge operates on a local-first philosophy and is designed to minimize data exposure. This Privacy Policy describes how we collect, use, and handle your information when you use our Service.</p>

        <h2 className="text-2xl font-semibold text-white mt-8">1. Information We Collect</h2>
        <p>We collect information that you provide directly to us:</p>
        <ul className="list-disc pl-6 space-y-2">
            <li><strong>Account Information:</strong> We collect your email address and a securely hashed password to create and manage your account.</li>
            <li><strong>Analysis Data:</strong> We collect the CV texts, Job Descriptions, company names, and recruiter names you submit to generate match scores and outreach templates.</li>
            <li><strong>Technical Data:</strong> We may collect standard technical information such as IP addresses and browser types for security and rate-limiting purposes, stored temporarily in standard audit logs.</li>
        </ul>

        <h2 className="text-2xl font-semibold text-white mt-8">2. Data Usage & AI Processing</h2>
        <p>The core functionality of NetworkForge requires processing your data through Large Language Models (LLMs).</p>
        <ul className="list-disc pl-6 space-y-2">
            <li><strong>PII Redaction:</strong> Before any text data (CVs or Job Descriptions) is sent to external AI providers (such as Groq or OpenAI), our system actively runs regex-based filters to strip out common Personally Identifiable Information (PII) including email addresses, phone numbers, and physical addresses.</li>
            <li><strong>Local Providers:</strong> If you configure a local provider like Ollama in a self-hosted environment, your data never leaves your infrastructure.</li>
            <li>We do NOT use your private data to train our own models, nor do we sell your data to third parties.</li>
        </ul>

        <h2 className="text-2xl font-semibold text-white mt-8">3. Data Retention and Deletion</h2>
        <p>We believe in data minimization. All analysis data is considered ephemeral.</p>
        <ul className="list-disc pl-6 space-y-2">
            <li><strong>Automated Purging:</strong> We run automated retention jobs that permanently purge historical analyses and associated outputs after 30 days.</li>
            <li><strong>Manual Deletion:</strong> You may delete specific analyses or your entire account and all associated data at any time directly from the dashboard.</li>
        </ul>

        <h2 className="text-2xl font-semibold text-white mt-8">4. Data Security</h2>
        <p>We implement strict security measures including HttpOnly secure cookies for authentication, robust Content Security Policies (CSP), and AES encryption for sensitive data at rest where applicable. While we strive to use commercially acceptable means to protect your Personal Data, we cannot guarantee its absolute security.</p>

        <h2 className="text-2xl font-semibold text-white mt-8">5. Contact Us</h2>
        <p>If you have any questions about this Privacy Policy or our privacy practices, please contact our security team at security@networkforge.ai.</p>
      </div>
    </main>
  )
}
