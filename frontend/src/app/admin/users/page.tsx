"use client"

import { useEffect, useState } from "react"
import { toast } from "sonner"
import { UserX, UserCheck } from "lucide-react"

import { apiFetch } from "@/lib/api"
import { Button } from "@/components/ui/button"

export default function AdminUsersPage() {
  const [users, setUsers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  async function fetchUsers() {
    try {
      const data = await apiFetch<any>("/admin/users?limit=50")
      setUsers(data.items)
    } catch (err) {
      toast.error("Failed to load users")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers()
  }, [])

  async function toggleStatus(userId: string, currentStatus: boolean) {
    try {
      await apiFetch(`/admin/users/${userId}/status`, {
        method: "PATCH",
        body: JSON.stringify({ is_active: !currentStatus }),
      })
      toast.success(`User has been ${!currentStatus ? 'activated' : 'suspended'}.`)
      fetchUsers()
    } catch (err) {
      toast.error("Failed to update user status")
    }
  }

  if (loading) return <div className="animate-pulse text-zinc-500">Loading users...</div>

  return (
    <div className="rounded-xl border border-white/10 bg-zinc-900/50 overflow-hidden">
      <table className="w-full text-left text-sm">
        <thead className="bg-black/40 border-b border-white/10 text-zinc-400">
          <tr>
            <th className="px-6 py-4 font-medium">Email</th>
            <th className="px-6 py-4 font-medium">Status</th>
            <th className="px-6 py-4 font-medium">Role</th>
            <th className="px-6 py-4 font-medium text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {users.map((u) => (
            <tr key={u.id} className="hover:bg-white/[0.02] transition-colors">
              <td className="px-6 py-4">{u.email}</td>
              <td className="px-6 py-4">
                {u.is_active ? (
                  <span className="inline-flex items-center rounded-full bg-emerald-500/10 px-2 py-1 text-xs text-emerald-400 ring-1 ring-emerald-500/20">Active</span>
                ) : (
                  <span className="inline-flex items-center rounded-full bg-red-500/10 px-2 py-1 text-xs text-red-400 ring-1 ring-red-500/20">Suspended</span>
                )}
              </td>
              <td className="px-6 py-4">
                {u.is_superuser ? (
                  <span className="text-blue-400 text-xs font-semibold">Admin</span>
                ) : (
                  <span className="text-zinc-500 text-xs">User</span>
                )}
              </td>
              <td className="px-6 py-4 text-right">
                {!u.is_superuser && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className={u.is_active ? "text-red-400 hover:text-red-300 hover:bg-red-500/10" : "text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10"}
                    onClick={() => toggleStatus(u.id, u.is_active)}
                  >
                    {u.is_active ? (
                      <><UserX className="size-4 mr-2" /> Suspend</>
                    ) : (
                      <><UserCheck className="size-4 mr-2" /> Activate</>
                    )}
                  </Button>
                )}
              </td>
            </tr>
          ))}
          {users.length === 0 && (
            <tr>
              <td colSpan={4} className="px-6 py-8 text-center text-zinc-500">
                No users found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
