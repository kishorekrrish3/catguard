import { api } from "./client"
import type { Zone, ZoneSummary, PaginatedResponse } from "@/types"

export const zonesApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Zone>>("/api/zones", { params }).then(r => r.data),
  get: (id: string) => api.get<Zone>(`/api/zones/${id}`).then(r => r.data),
  summary: (id: string) => api.get<ZoneSummary>(`/api/zones/${id}/summary`).then(r => r.data),
  create: (data: Partial<Zone> & { geojson?: object }) =>
    api.post<Zone>("/api/zones", data).then(r => r.data),
  update: (id: string, data: Partial<Zone>) =>
    api.put<Zone>(`/api/zones/${id}`, data).then(r => r.data),
  delete: (id: string) => api.delete(`/api/zones/${id}`),
}