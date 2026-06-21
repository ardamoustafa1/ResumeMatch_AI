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
        <p>Last Updated: June 21, 2026</p>
        <p>These terms (&quot;Terms&quot;) govern your use of the NetworkForge web app and Chrome extension. By using our service, you agree to be bound by these Terms of Service. If you disagree with any part of the terms, then you do not have permission to access the Service.</p>

        <h2 className="text-2xl font-semibold text-white mt-8">1. Service Description</h2>
        <p>NetworkForge is an AI-powered career assistant. The generated outreach messages, match scores, and profile improvements are automated suggestions based on Large Language Model (LLM) outputs and your provided data. They do not constitute professional career advice and do not guarantee employment, interviews, or any specific outcome.</p>

        <h2 className="text-2xl font-semibold text-white mt-8">2. User Responsibilities</h2>
        <p>You are solely responsible for the content, CVs, and Job Descriptions you submit. You agree that:</p>
        <ul className="list-disc pl-6 space-y-2">
            <li>You have the right to upload the provided data and it does not violate any third-party confidentiality agreements, NDAs, or proprietary rights.</li>
            <li>You will not misuse the Chrome Extension to aggressively scrape LinkedIn or violate LinkedIn&apos;s User Agreement.</li>
            <li>You will use the Service for lawful purposes only and not engage in any activity that interferes with or disrupts the Service.</li>
        </ul>

        <h2 className="text-2xl font-semibold text-white mt-8">3. Accounts and Security</h2>
        <p>When you create an account with us, you must provide information that is accurate and complete. You are responsible for safeguarding the password and API keys that you use to access the Service. You agree not to disclose your password or API keys to any third party. You must notify us immediately upon becoming aware of any breach of security or unauthorized use of your account.</p>

        <h2 className="text-2xl font-semibold text-white mt-8">4. Open Source and Self-Hosting</h2>
        <p>NetworkForge is an open-source project provided under the MIT License. You are free to self-host, modify, and distribute the source code in accordance with the license. To the maximum extent permitted by law, NetworkForge is provided &quot;as is&quot; without warranty of any kind. We are not responsible for any missed job opportunities, rejected applications, or data loss.</p>

        <h2 className="text-2xl font-semibold text-white mt-8">5. Limitation of Liability</h2>
        <p>In no event shall NetworkForge, nor its directors, employees, partners, agents, suppliers, or affiliates, be liable for any indirect, incidental, special, consequential or punitive damages, including without limitation, loss of profits, data, use, goodwill, or other intangible losses, resulting from your access to or use of or inability to access or use the Service.</p>

        <h2 className="text-2xl font-semibold text-white mt-8">6. Changes</h2>
        <p>You retain all rights to your resume/CV and the job descriptions you analyze. We do not claim ownership. By submitting them, you grant us a temporary license solely to process them using our AI engine to provide you with match scores and drafts. We reserve the right, at our sole discretion, to modify or replace these Terms at any time. We will try to provide at least 30 days notice prior to any new terms taking effect.</p>

        <h2 className="text-2xl font-semibold text-white mt-8">7. Contact Us</h2>
        <p>If you have any questions about these Terms, please contact us at legal@networkforge.ai.</p>
      </div>
    </main>
  )
}
