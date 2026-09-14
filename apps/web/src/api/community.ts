import { api } from "./client"
import type { CommunityReport, LeaderboardEntry, PaginatedResponse } from "@/types"

export const communityApi = {
  submit: (data: Record<string, unknown>) =>
    api.post<CommunityReport>("/api/community/reports", data).then(r => r.data),
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<CommunityReport>>("/api/community/reports", { params }).then(r => r.data),
  getStatus: (id: string) =>
    api.get<CommunityReport>(`/api/community/reports/${id}`).then(r => r.data),
  updateStatus: (id: string, status: string, notes?: string) =>
    api.put(`/api/community/reports/${id}/status`, null, { params: { status, resolution_notes: notes } }),
  leaderboard: (limit = 10) =>
    api.get<LeaderboardEntry[]>("/api/community/leaderboard", { params: { limit } }).then(r => r.data),
  stats: () => api.get("/api/community/stats").then(r => r.data),
}