import type { Metadata, Viewport } from "next";
import { Toaster } from "@/components/ui/sonner";
import { ThemeProvider } from "@/components/theme-provider";
import "./globals.css";

export const viewport: Viewport = {
  themeColor: "#080a0f",
};

export const metadata: Metadata = {
  metadataBase: new URL("https://networkforge.dev"),
  title: {
    default: "NetworkForge — Private Career Intelligence",
    template: "%s · NetworkForge",
  },
  manifest: "/manifest.json",
  description:
    "Open-source, privacy-first CV matching, opportunity intelligence, and personalized recruiter outreach.",
  openGraph: {
    title: "NetworkForge",
    description: "Turn a CV and job description into an explainable opportunity map, sharper positioning, and personal outreach.",
    url: "https://github.com/ardamoustafa1/NetworkForge",
    siteName: "NetworkForge",
    images: [
      {
        url: "/brand/networkforge-hero.png",
        width: 1200,
        height: 630,
        alt: "NetworkForge Dashboard",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "NetworkForge",
    description: "Open-source, privacy-first career intelligence.",
    images: ["/brand/networkforge-hero.png"],
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
      className="h-full antialiased"
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col">
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem={false}
          disableTransitionOnChange
        >
          {children}
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  );
}
