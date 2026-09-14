import { useQuery } from "@tanstack/react-query"
import { sensorsApi } from "@/api/sensors"

export function useSensors(params?: Record<string, unknown>) {
  return useQuery({
    queryKey: ["sensors", params],
    queryFn: () => sensorsApi.list(params),
    refetchInterval: 60_000,
  })
}

export function useSensorHealth(zone_id?: string) {
  return useQuery({
    queryKey: ["sensor-health", zone_id],
    queryFn: () => sensorsApi.health(zone_id),
    refetchInterval: 60_000,
  })
}

export function useSensorReadings(id: string | null, params?: Record<string, unknown>) {
  return useQuery({
    queryKey: ["sensor-readings", id, params],
    queryFn: () => sensorsApi.readings(id!, params),
    enabled: !!id,
    refetchInterval: 60_000,
  })
}