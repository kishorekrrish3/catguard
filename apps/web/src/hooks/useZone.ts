import { useQuery } from "@tanstack/react-query"
import { zonesApi } from "@/api/zones"
import { useMapStore } from "@/store/mapStore"

export function useZones() {
  return useQuery({ queryKey: ["zones"], queryFn: () => zonesApi.list({ size: 100 }), staleTime: 60_000 })
}

export function useZone(id: string | null) {
  return useQuery({ queryKey: ["zone", id], queryFn: () => zonesApi.get(id!), enabled: !!id })
}

export function useZoneSummary(id: string | null) {
  return useQuery({
    queryKey: ["zone-summary", id],
    queryFn: () => zonesApi.summary(id!),
    enabled: !!id,
    refetchInterval: 60_000,
  })
}

export function useSelectedZone() {
  const selectedZoneId = useMapStore((s) => s.selectedZoneId)
  const { data: zone } = useZone(selectedZoneId)
  return { selectedZoneId, zone }
}