"use client"

import { useEffect, useState } from "react"
import { Activity, Database, Server, Users } from "lucide-react"
import { apiFetch } from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function AdminOverviewPage() {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchStats() {
      try {
        const data = await apiFetch<any>("/admin/system")
        setStats(data.stats)
      } catch (err) {
        console.error("Failed to load stats", err)
      } finally {
        setLoading(false)
      }
    }
    fetchStats()
  }, [])

  if (loading) {
    return <div className="text-zinc-500 animate-pulse">Loading system statistics...</div>
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-6 md:grid-cols-3">
        <Card className="bg-zinc-900/50 border-white/10">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400">Total Users</CardTitle>
            <Users className="size-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats?.total_users || 0}</div>
          </CardContent>
        </Card>
        
        <Card className="bg-zinc-900/50 border-white/10">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400">Total Analyses</CardTitle>
            <Database className="size-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats?.total_analyses || 0}</div>
          </CardContent>
        </Card>

        <Card className="bg-zinc-900/50 border-white/10">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400">Analyses (24h)</CardTitle>
            <Activity className="size-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats?.analyses_24h || 0}</div>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-zinc-900/50 border-white/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="size-5 text-zinc-400" />
            System Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between p-4 rounded-lg bg-black/40 border border-white/5">
              <div className="flex items-center gap-3">
                <div className="size-2.5 rounded-full bg-emerald-500 animate-pulse" />
                <span className="font-medium">PostgreSQL Database</span>
              </div>
              <span className="text-xs text-zinc-500">Healthy</span>
            </div>
            <div className="flex items-center justify-between p-4 rounded-lg bg-black/40 border border-white/5">
              <div className="flex items-center gap-3">
                <div className="size-2.5 rounded-full bg-emerald-500 animate-pulse" />
                <span className="font-medium">Redis Cache & Queues</span>
              </div>
              <span className="text-xs text-zinc-500">Healthy</span>
            </div>
            <div className="flex items-center justify-between p-4 rounded-lg bg-black/40 border border-white/5">
              <div className="flex items-center gap-3">
                <div className="size-2.5 rounded-full bg-emerald-500 animate-pulse" />
                <span className="font-medium">Celery Workers</span>
              </div>
              <span className="text-xs text-zinc-500">Online</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
