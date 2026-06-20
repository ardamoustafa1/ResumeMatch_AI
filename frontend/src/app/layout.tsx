import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "ResumeMatch AI",
    template: "%s · ResumeMatch AI",
  },
  description:
    "Private, AI-assisted CV matching and personalized recruiter outreach.",
  openGraph: {
    title: "ResumeMatch AI",
    description: "Private, AI-assisted CV matching and personalized recruiter outreach.",
    url: "https://resumematch.ai",
    siteName: "ResumeMatch AI",
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "ResumeMatch AI",
    description: "Turn a job description into a focused conversation with AI.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        {children}
        <Toaster />
      </body>
    </html>
  );
}
