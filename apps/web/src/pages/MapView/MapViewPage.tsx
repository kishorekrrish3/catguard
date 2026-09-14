import { CatGuardMap } from "@/components/map/CatGuardMap"
import { useSensors } from "@/hooks/useSensorData"
import { useMapStore } from "@/store/mapStore"
import { useZones } from "@/hooks/useZone"
import { useQuery } from "@tanstack/react-query"
import { detectionsApi } from "@/api/detections"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

export function MapViewPage() {
  const { selectedZoneId, setSelectedZone } = useMapStore()
  const { data: zonesData } = useZones()
  const { data: sensorsData } = useSensors({ size: 200 })
  const zones = zonesData?.items ?? []
  const sensors = sensorsData?.items ?? []

  const { data: detectionsData } = useQuery({
    queryKey: ["detections-map", selectedZoneId],
    queryFn: () => detectionsApi.list(selectedZoneId!, { size: 100 }),
    enabled: !!selectedZoneId,
  })

  return (
    <div className="flex h-full">
      {/* Sidebar zone list */}
      <div className="w-64 flex-shrink-0 border-r bg-white overflow-y-auto">
        <div className="p-4 border-b">
          <h2 className="text-sm font-semibold">CAT Zones</h2>
          <p className="text-xs text-muted-foreground">{zones.length} zones monitored</p>
        </div>
        <div className="p-2 space-y-1">
          <button
            onClick={() => setSelectedZone(null)}
            className={cn("w-full text-left px-3 py-2 rounded-md text-sm", !selectedZoneId ? "bg-forest-100 text-forest-800 font-medium" : "hover:bg-muted")}
          >
            All Zones
          </button>
          {zones.map((z) => (
            <button
              key={z.id}
              onClick={() => setSelectedZone(z.id)}
              className={cn("w-full text-left px-3 py-2 rounded-md text-sm", selectedZoneId === z.id ? "bg-forest-100 text-forest-800 font-medium" : "hover:bg-muted")}
            >
              <div className="flex items-center justify-between">
                <span className="truncate">{z.name}</span>
                <Badge variant={z.status === "active" ? "default" : "secondary"} className="text-[10px] ml-1">{z.status}</Badge>
              </div>
            </button>
          ))}
        </div>
        <div className="p-4 border-t">
          <p className="text-xs text-muted-foreground">{sensors.length} sensors</p>
          <p className="text-xs text-muted-foreground">{detectionsData?.total ?? 0} detections</p>
        </div>
      </div>

      {/* Full map */}
      <div className="flex-1 relative">
        <CatGuardMap
          sensors={sensors}
          detections={detectionsData?.items ?? []}
          zones={zones}
          height="100%"
        />
      </div>
    </div>
  )
}