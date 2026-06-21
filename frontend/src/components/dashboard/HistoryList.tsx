import Link from "next/link"
import { History, Trash2 } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog"
import { HistoryChart } from "./HistoryChart"
import type { AnalysisRecord } from "@/lib/types"

export function HistoryList({ history, deleteAnalysis }: { history: AnalysisRecord[]; deleteAnalysis: (id: string) => Promise<void> }) {
  if (history.length === 0) return null

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <History className="size-4 text-zinc-400" /> Recent analyses
        </CardTitle>
        <HistoryChart history={history} />
      </CardHeader>
      <CardContent className="space-y-2">
        {history.map((item) => (
          <div key={item.id} className="group flex items-center justify-between rounded-lg border border-zinc-800 bg-zinc-950/50 p-3 transition hover:border-zinc-700 hover:bg-zinc-900">
            <Link href={`/dashboard/analysis/${item.id}`} className="flex-1">
              <p className="text-sm font-medium transition group-hover:text-blue-400">{item.company || "Unnamed company"}</p>
              <p className="text-xs text-zinc-500">{new Date(item.created_at).toLocaleString()}</p>
            </Link>
            <div className="flex items-center gap-3">
              <span className="rounded-full bg-zinc-800 px-2 py-1 text-xs text-zinc-300">{item.status.replace("_", " ")}</span>
              <AlertDialog>
                <AlertDialogTrigger className="text-zinc-600 opacity-0 transition hover:text-red-400 group-hover:opacity-100" title="Delete">
                  <Trash2 className="h-4 w-4" />
                </AlertDialogTrigger>
                <AlertDialogContent className="bg-zinc-950 border-zinc-800">
                  <AlertDialogHeader>
                    <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                    <AlertDialogDescription className="text-zinc-400">
                      This action cannot be undone. This will permanently delete your analysis and remove the data from our servers.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel className="bg-zinc-900 text-white border-zinc-800 hover:bg-zinc-800">Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={() => void deleteAnalysis(item.id)} className="bg-red-600 hover:bg-red-700 text-white">Delete</AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
