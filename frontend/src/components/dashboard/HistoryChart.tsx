"use client"

import { useTheme } from "next-themes"
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import type { AnalysisRecord } from "@/lib/types"

export function HistoryChart({ history }: { history: AnalysisRecord[] }) {
  const { theme } = useTheme()
  const isDark = theme === "dark" || theme === "system"

  // Filter completed and map to chart data
  const data = history
    .filter((h) => h.status === "completed" && h.result?.match_result)
    .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
    .map((h) => ({
      name: h.company || "Unknown",
      score: h.result!.match_result!.score,
      date: new Date(h.created_at).toLocaleDateString()
    }))

  if (data.length < 2) return null

  return (
    <div className="h-[200px] w-full mt-4">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <XAxis 
            dataKey="name" 
            stroke={isDark ? "#52525b" : "#a1a1aa"} 
            fontSize={12} 
            tickLine={false} 
            axisLine={false}
          />
          <YAxis 
            stroke={isDark ? "#52525b" : "#a1a1aa"} 
            fontSize={12} 
            tickLine={false} 
            axisLine={false} 
            tickFormatter={(value) => `${value}%`}
            domain={[0, 100]}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: isDark ? "#09090b" : "#ffffff", 
              border: isDark ? "1px solid #27272a" : "1px solid #e4e4e7",
              borderRadius: "8px"
            }} 
            labelStyle={{ color: isDark ? "#a1a1aa" : "#52525b", marginBottom: "4px" }}
          />
          <Line 
            type="monotone" 
            dataKey="score" 
            stroke="#3b82f6" 
            strokeWidth={2} 
            activeDot={{ r: 6, fill: "#3b82f6" }} 
            dot={{ r: 4, fill: "#1d4ed8", strokeWidth: 0 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
