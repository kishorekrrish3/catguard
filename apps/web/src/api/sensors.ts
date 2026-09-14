import { api } from "./client"
import type { Sensor, SensorReading, SensorHealth, PaginatedResponse } from "@/types"

export const sensorsApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Sensor>>("/api/sensors/list", { params }).then(r => r.data),
  health: (zone_id?: string) =>
    api.get<SensorHealth>("/api/sensors/health", { params: zone_id ? { zone_id } : {} }).then(r => r.data),
  readings: (id: string, params?: Record<string, unknown>) =>
    api.get<SensorReading[]>(`/api/sensors/${id}/readings`, { params }).then(r => r.data),
  calibrate: (id: string, offset: number) =>
    api.post(`/api/sensors/${id}/calibrate`, null, { params: { offset } }),
  create: (data: Record<string, unknown>) =>
    api.post<Sensor>("/api/sensors", data).then(r => r.data),
  decommission: (id: string) => api.delete(`/api/sensors/${id}`),
}