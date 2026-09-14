import { api } from "./client"
import type { TokenResponse, User } from "@/types"

export const authApi = {
  login: (email: string, password: string) =>
    api.post<TokenResponse>("/api/auth/login", { email, password }).then(r => r.data),
  refresh: (refresh_token: string) =>
    api.post<TokenResponse>("/api/auth/refresh", { refresh_token }).then(r => r.data),
  logout: (refresh_token: string) =>
    api.post("/api/auth/logout", { refresh_token }),
  me: () => api.get<User>("/api/auth/me").then(r => r.data),
  updateMe: (data: Partial<User>) => api.put<User>("/api/auth/me", data).then(r => r.data),
}