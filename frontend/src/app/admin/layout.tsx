"use client"

import { useEffect } from "react"
import { useRouter, usePathname } from "next/navigation"
import Link from "next/link"
import { LayoutDashboard, Users, Activity, ShieldAlert, Sparkles, ArrowLeft } from "lucide-react"

import { useAuthStore } from "@/stores/authStore"
import { ThemeToggle } from "@/components/theme-toggle"

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()
  const { user, initialized, bootstrap } = useAuthStore()

  useEffect(() => {
    if (!initialized) void bootstrap()
  }, [bootstrap, initialized])

  useEffect(() => {
    if (initialized) {
      if (!user) {
        router.replace("/login")
      } else if (!user.is_superuser) {
        router.replace("/dashboard")
      }
    }
  }, [initialized, user, router])

  if (!initialized || !user || !user.is_superuser) {
    return (
      <main className="grid min-h-screen place-items-center bg-black">
        <div className="size-8 animate-spin rounded-full border-4 border-blue-400 border-t-transparent" />
      </main>
    )
  }

  const navItems = [
    { name: "Overview", href: "/admin", icon: LayoutDashboard },
    { name: "Users", href: "/admin/users", icon: Users },
    { name: "Telemetry", href: "/admin/telemetry", icon: Activity },
  ]

  return (
    <div className="min-h-screen bg-zinc-950 text-white flex flex-col md:flex-row">
      {/* Sidebar */}
      <aside className="w-full md:w-64 border-r border-white/10 bg-black/50 p-6 flex flex-col gap-8">
        <div className="flex items-center gap-2 font-bold tracking-tight text-lg">
          <ShieldAlert className="size-5 text-red-500" />
          Admin Console
        </div>
        <nav className="flex-1 space-y-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                  isActive ? "bg-white/10 text-white font-medium" : "text-zinc-400 hover:bg-white/5 hover:text-zinc-200"
                }`}
              >
                <item.icon className="size-4" />
                {item.name}
              </Link>
            )
          })}
        </nav>
        <div className="mt-auto pt-6 border-t border-white/10 space-y-4">
          <Link href="/dashboard" className="flex items-center gap-2 text-sm text-zinc-400 hover:text-white transition">
            <ArrowLeft className="size-4" />
            Back to App
          </Link>
          <div className="flex items-center gap-4">
            <ThemeToggle />
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto bg-black selection:bg-red-500/30">
        <header className="border-b border-white/5 p-6 bg-zinc-900/20 backdrop-blur">
          <h1 className="text-xl font-semibold">NetworkForge Administration</h1>
          <p className="text-sm text-zinc-500">Manage your enterprise deployment.</p>
        </header>
        <div className="p-6">
          {children}
        </div>
      </main>
    </div>
  )
}
