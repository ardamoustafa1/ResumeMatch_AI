import { create } from "zustand"

import { apiFetch } from "@/lib/api"
import type { User } from "@/lib/types"

interface AuthState {
  user: User | null
  initialized: boolean
  setUser: (user: User | null) => void
  bootstrap: () => Promise<void>
  logout: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  initialized: false,
  setUser: (user) => set({ user }),
  bootstrap: async () => {
    try {
      const user = await apiFetch<User>("/auth/me")
      set({ user, initialized: true })
    } catch {
      set({ user: null, initialized: true })
    }
  },
  logout: async () => {
    try {
      await apiFetch<void>("/auth/logout", { method: "POST" }, false)
    } finally {
      set({ user: null, initialized: true })
    }
  },
}))
