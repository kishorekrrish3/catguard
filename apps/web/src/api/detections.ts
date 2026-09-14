import { api } from "./client"
import type { Detection, DetectionTimelinePoint, PaginatedResponse } from "@/types"

export const detectionsApi = {
  list: (zone_id: string, params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Detection>>(`/api/detections/zone/${zone_id}`, { params }).then(r => r.data),
  timeline: (zone_id: string, days = 30) =>
    api.get<DetectionTimelinePoint[]>(`/api/detections/timeline/${zone_id}`, { params: { days } }).then(r => r.data),
  feedback: (detection_id: string, verified: boolean, notes?: string) =>
    api.post("/api/detections/feedback", { detection_id, verified, notes }),
  accuracy: (zone_id?: string) =>
    api.get("/api/detections/accuracy", { params: zone_id ? { zone_id } : {} }).then(r => r.data),
}