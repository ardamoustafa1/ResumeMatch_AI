"use client"

import { useEffect, useState } from "react"
import { Users } from "lucide-react"
import { apiFetch } from "@/lib/api"
import { toast } from "sonner"

export function WorkspaceSwitcher() {
  const [workspaces, setWorkspaces] = useState<any[]>([])
  const [activeId, setActiveId] = useState<string>("personal")

  useEffect(() => {
    let active = true
    apiFetch<{ items: any[] }>("/workspaces")
      .then((data) => {
        if (active) {
          setWorkspaces(data.items || [])
          const saved = localStorage.getItem("activeWorkspace")
          if (saved) {
            setActiveId(saved)
          }
        }
      })
      .catch(console.error)
    return () => { active = false }
  }, [])

  const handleSwitch = (id: string) => {
    if (id === "create") {
      createWorkspace()
      return
    }
    setActiveId(id)
    if (id === "personal") {
      localStorage.removeItem("activeWorkspace")
    } else {
      localStorage.setItem("activeWorkspace", id)
    }
    window.location.reload()
  }

  const createWorkspace = async () => {
    const name = prompt("Enter new workspace name:")
    if (!name) {
      setActiveId(activeId) 
      return
    }
    try {
      const data = await apiFetch<any>("/workspaces", {
        method: "POST",
        body: JSON.stringify({ name }),
      })
      setWorkspaces([...workspaces, { id: data.id, name: data.name, role: "owner" }])
      handleSwitch(data.id)
      toast.success("Workspace created")
    } catch (e) {
      toast.error("Failed to create workspace")
      setActiveId(activeId)
    }
  }

  return (
    <div className="flex items-center gap-2 bg-black/40 border border-white/[0.1] rounded-md px-3 py-1.5 hover:bg-black/60 transition-colors">
      <Users className="size-4 text-blue-400" />
      <select
        value={activeId}
        onChange={(e) => handleSwitch(e.target.value)}
        className="bg-transparent text-sm font-medium text-zinc-300 focus:outline-none appearance-none cursor-pointer pr-4"
        style={{ backgroundImage: `url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23A1A1AA%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E")`, backgroundRepeat: "no-repeat", backgroundPosition: "right 0.1rem top 50%", backgroundSize: "0.65rem auto" }}
      >
        <option value="personal">Personal Workspace</option>
        {workspaces.map(w => (
          <option key={w.id} value={w.id}>{w.name}</option>
        ))}
        <option value="create" className="text-blue-400">+ Create Workspace</option>
      </select>
    </div>
  )
}
