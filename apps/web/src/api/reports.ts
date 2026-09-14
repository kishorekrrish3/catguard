import { api } from "./client"

export const reportsApi = {
  templates: () => api.get("/api/reports/templates").then(r => r.data),
  generate: (params: Record<string, unknown>) =>
    api.get("/api/reports/generate", { params, responseType: "blob" }),
  schedule: (data: Record<string, unknown>) =>
    api.post("/api/reports/schedule", null, { params: data }).then(r => r.data),
}