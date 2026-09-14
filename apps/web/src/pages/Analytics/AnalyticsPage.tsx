import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { NDVITrendChart } from "@/components/charts/NDVITrendChart"
import { DetectionFrequencyChart } from "@/components/charts/DetectionFrequencyChart"
import { SensorReadingChart } from "@/components/charts/SensorReadingChart"
import { AlertDistributionChart } from "@/components/charts/AlertDistributionChart"
import { zonesApi } from "@/api/zones"
import { detectionsApi } from "@/api/detections"
import { sensorsApi } from "@/api/sensors"
import { alertsApi } from "@/api/alerts"
import { useMapStore } from "@/store/mapStore"

const DAYS_OPTIONS = [7, 14, 30, 90]

export function AnalyticsPage() {
  const [days, setDays] = useState(30)
  const { selectedZoneId } = useMapStore()

  const { data: zones } = useQuery({ queryKey: ["zones"], queryFn: () => zonesApi.list({ size: 100 }) })
  const firstZoneId = selectedZoneId ?? zones?.items?.[0]?.id

  const { data: detectionTimeline, isLoading: dtLoading } = useQuery({
    queryKey: ["det-timeline", firstZoneId, days],
    queryFn: () => detectionsApi.timeline(firstZoneId!, days),
    enabled: !!firstZoneId,
  })

  const { data: sensors } = useQuery({ queryKey: ["sensors-analytics", firstZoneId], queryFn: () => sensorsApi.list({ zone_id: firstZoneId, size: 5 }), enabled: !!firstZoneId })
  const firstSensor = sensors?.items?.[0]
  const { data: sensorReadings } = useQuery({ queryKey: ["readings-analytics", firstSensor?.id], queryFn: () => sensorsApi.readings(firstSensor!.id, { limit: 288 }), enabled: !!firstSensor })

  const { data: alertStats } = useQuery({ queryKey: ["alert-stats-analytics", firstZoneId], queryFn: () => alertsApi.stats(firstZoneId) })

  const ndviData = Array.from({ length: days }, (_, i) => ({
    date: new Date(Date.now() - (days - 1 - i) * 86400000).toISOString(),
    ndvi_mean: Math.min(0.95, Math.max(0.15, 0.62 + (Math.sin(i / 7) * 0.08) + (Math.random() - 0.5) * 0.05)),
    ndvi_min: Math.max(0.1, 0.45 + (Math.random() - 0.5) * 0.08),
    ndvi_max: Math.min(0.95, 0.78 + (Math.random() - 0.5) * 0.06),
  }))

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-forest-800">Analytics</h1>
          <p className="text-muted-foreground text-sm">Vegetation health, detection trends, and sensor data</p>
        </div>
        <div className="flex gap-2">
          {DAYS_OPTIONS.map((d) => (
            <button key={d} onClick={() => setDays(d)}
              className={`px-3 py-1.5 text-sm rounded-md border font-medium transition-colors ${days === d ? "bg-forest-700 text-white border-forest-700" : "hover:bg-muted"}`}>
              {d}d
            </button>
          ))}
        </div>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base">NDVI Vegetation Health Trend</CardTitle></CardHeader>
        <CardContent><NDVITrendChart data={ndviData} /></CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle className="text-base">Detection Frequency by Type</CardTitle></CardHeader>
          <CardContent>
            {dtLoading ? <Skeleton className="h-[280px]" /> : detectionTimeline ? <DetectionFrequencyChart data={detectionTimeline} /> : <p className="text-sm text-muted-foreground text-center py-16">Select a zone to view detections</p>}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-base">Alert Severity Distribution</CardTitle></CardHeader>
          <CardContent>
            {alertStats ? <AlertDistributionChart stats={alertStats} /> : <Skeleton className="h-[240px]" />}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Sensor Reading — {firstSensor?.name ?? "Select zone for sensor data"}</CardTitle>
        </CardHeader>
        <CardContent>
          {sensorReadings ? <SensorReadingChart data={sensorReadings} unit={firstSensor?.sensor_type?.replace("_", " ")} /> : <Skeleton className="h-[220px]" />}
        </CardContent>
      </Card>
    </div>
  )
}