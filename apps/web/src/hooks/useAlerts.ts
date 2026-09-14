import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { alertsApi } from "@/api/alerts"

export function useAlerts(params?: Record<string, unknown>) {
  return useQuery({
    queryKey: ["alerts", params],
    queryFn: () => alertsApi.list(params),
    refetchInterval: 30_000,
  })
}

export function useAlertStats(zone_id?: string) {
  return useQuery({
    queryKey: ["alert-stats", zone_id],
    queryFn: () => alertsApi.stats(zone_id),
    refetchInterval: 30_000,
  })
}

export function useAcknowledgeAlert() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, notes }: { id: string; notes?: string }) => alertsApi.acknowledge(id, notes),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["alerts"] }),
  })
}

export function useResolveAlert() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => alertsApi.resolve(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["alerts"] }),
  })
}