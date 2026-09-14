import { create } from "zustand"
import { persist } from "zustand/middleware"
import type { User } from "@/types"
import { authApi } from "@/api/auth"

interface AuthState {
  user: User | null
  accessToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  setUser: (user: User) => void
  setTokens: (access: string, refresh: string) => void
  initialize: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: false,

      setUser: (user) => set({ user }),
      setTokens: (access, refresh) => {
        localStorage.setItem("access_token", access)
        localStorage.setItem("refresh_token", refresh)
        set({ accessToken: access, isAuthenticated: true })
      },

      login: async (email, password) => {
        set({ isLoading: true })
        try {
          const tokens = await authApi.login(email, password)
          localStorage.setItem("access_token", tokens.access_token)
          localStorage.setItem("refresh_token", tokens.refresh_token)
          const user = await authApi.me()
          set({ user, accessToken: tokens.access_token, isAuthenticated: true, isLoading: false })
        } catch (err) {
          set({ isLoading: false })
          throw err
        }
      },

      logout: async () => {
        const refreshToken = localStorage.getItem("refresh_token")
        if (refreshToken) {
          try { await authApi.logout(refreshToken) } catch {}
        }
        localStorage.removeItem("access_token")
        localStorage.removeItem("refresh_token")
        set({ user: null, accessToken: null, isAuthenticated: false })
      },

      initialize: async () => {
        const token = localStorage.getItem("access_token")
        if (token && !get().user) {
          try {
            const user = await authApi.me()
            set({ user, accessToken: token, isAuthenticated: true })
          } catch {
            localStorage.removeItem("access_token")
            localStorage.removeItem("refresh_token")
            set({ isAuthenticated: false })
          }
        }
      },
    }),
    { name: "catguard-auth", partialize: (s) => ({ accessToken: s.accessToken, isAuthenticated: s.isAuthenticated }) }
  )
)