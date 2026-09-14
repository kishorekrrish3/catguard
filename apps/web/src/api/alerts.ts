import { api } from "./client"
import type { Alert, AlertRule, AlertStats, PaginatedResponse } from "@/types"

export const alertsApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Alert>>("/api/alerts", { params }).then(r => r.data),
  stats: (zone_id?: string) =>
    api.get<AlertStats>("/api/alerts/stats", { params: zone_id ? { zone_id } : {} }).then(r => r.data),
  acknowledge: (id: string, notes?: string) =>
    api.post(`/api/alerts/${id}/acknowledge`, { notes }),
  resolve: (id: string) => api.post(`/api/alerts/${id}/resolve`),
  markFalsePositive: (id: string) => api.post(`/api/alerts/${id}/false-positive`),
  listRules: (zone_id?: string) =>
    api.get<AlertRule[]>("/api/alerts/rules", { params: zone_id ? { zone_id } : {} }).then(r => r.data),
  createRule: (data: Partial<AlertRule>) =>
    api.post<AlertRule>("/api/alerts/rules", data).then(r => r.data),
  updateRule: (id: string, data: Partial<AlertRule>) =>
    api.put<AlertRule>(`/api/alerts/rules/${id}`, data).then(r => r.data),
  deleteRule: (id: string) => api.delete(`/api/alerts/rules/${id}`),
}