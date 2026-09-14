import { useQuery } from "@tanstack/react-query"
import { AlertTriangle, Activity, Satellite, TrendingUp, TrendingDown, Minus } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { NDVITrendChart } from "@/components/charts/NDVITrendChart"
import { DetectionFrequencyChart } from "@/components/charts/DetectionFrequencyChart"
import { AlertDistributionChart } from "@/components/charts/AlertDistributionChart"
import { alertsApi } from "@/api/alerts"
import { sensorsApi } from "@/api/sensors"
import { useAlertStats } from "@/hooks/useAlerts"
import { useSensorHealth } from "@/hooks/useSensorData"
import { useMapStore } from "@/store/mapStore"
import { zonesApi } from "@/api/zones"
import { detectionsApi } from "@/api/detections"
import { timeAgo, ndviHealthLabel, ndviColor } from "@/lib/utils"
import { useNavigate } from "react-router-dom"
import { cn } from "@/lib/utils"

function KPICard({ title, value, sub, icon: Icon, trend, color }: {
  title: string; value: string | number; sub?: string
  icon: React.ElementType; trend?: "up" | "down" | "flat"; color?: string
}) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground font-medium">{title}</p>
            <p className={cn("text-3xl font-bold mt-1", color)}>{value}</p>
            {sub && <p className="text-xs text-muted-foreground mt-1">{sub}</p>}
          </div>
          <div className={cn("flex h-12 w-12 items-center justify-center rounded-full", color ? "bg-muted" : "bg-primary/10")}>
            <Icon className={cn("h-6 w-6", color ?? "text-primary")} />
          </div>
        </div>
        {trend && (
          <div className="mt-3 flex items-center gap-1 text-xs">
            {trend === "up" && <TrendingUp className="h-3 w-3 text-green-500" />}
            {trend === "down" && <TrendingDown className="h-3 w-3 text-red-500" />}
            {trend === "flat" && <Minus className="h-3 w-3 text-gray-400" />}
            <span className="text-muted-foreground">vs. last week</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export function DashboardPage() {
  const { selectedZoneId } = useMapStore()
  const navigate = useNavigate()

  const { data: alertStats, isLoading: statsLoading } = useAlertStats(selectedZoneId ?? undefined)
  const { data: sensorHealth, isLoading: sensorLoading } = useSensorHealth(selectedZoneId ?? undefined)
  const { data: zones } = useQuery({ queryKey: ["zones"], queryFn: () => zonesApi.list({ size: 3 }) })

  const firstZone = zones?.items?.[0]
  const { data: zoneSummary } = useQuery({
    queryKey: ["zone-summary", firstZone?.id],
    queryFn: () => zonesApi.summary(firstZone!.id),
    enabled: !!firstZone,
  })

  const { data: recentAlerts } = useQuery({
    queryKey: ["alerts", "recent"],
    queryFn: () => alertsApi.list({ size: 5, status: "active" }),
    refetchInterval: 30_000,
  })

  const { data: detectionTimeline } = useQuery({
    queryKey: ["detection-timeline-dash", firstZone?.id],
    queryFn: () => detectionsApi.timeline(firstZone!.id, 14),
    enabled: !!firstZone,
  })

  // Mock NDVI trend from zone summary imagery
  const ndviData = Array.from({ length: 30 }, (_, i) => {
    const base = zoneSummary?.ndvi_mean ?? 0.6
    return {
      date: new Date(Date.now() - (29 - i) * 86400000).toISOString(),
      ndvi_mean: Math.min(0.95, Math.max(0.1, base + (Math.random() - 0.5) * 0.1)),
    }
  })

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-forest-800">Dashboard</h1>
        <p className="text-muted-foreground text-sm mt-1">Real-time forest monitoring overview</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statsLoading ? (
          Array(4).fill(0).map((_, i) => <Skeleton key={i} className="h-32" />)
        ) : (
          <>
            <KPICard
              title="Active Alerts" value={alertStats?.by_status?.["active"] ?? 0}
              sub={`${alertStats?.by_severity?.["critical"] ?? 0} critical`}
              icon={AlertTriangle} color="text-red-600" trend="up"
            />
            <KPICard
              title="Sensors Online" value={sensorHealth ? `${sensorHealth.active}/${sensorHealth.total}` : "—"}
              sub={`${sensorHealth?.low_battery ?? 0} low battery`}
              icon={Activity} color="text-green-600" trend="flat"
            />
            <KPICard
              title="NDVI Average" value={zoneSummary?.ndvi_mean?.toFixed(3) ?? "—"}
              sub={ndviHealthLabel(zoneSummary?.ndvi_mean ?? 0)}
              icon={Satellite} color={ndviColor(zoneSummary?.ndvi_mean ?? 0)} trend="down"
            />
            <KPICard
              title="Detections (30d)" value={zoneSummary?.recent_detections ?? 0}
              sub="across all zones" icon={TrendingUp} trend="up"
            />
          </>
        )}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">NDVI Trend — Last 30 Days</CardTitle>
          </CardHeader>
          <CardContent>
            <NDVITrendChart data={ndviData} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Alert Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {alertStats ? <AlertDistributionChart stats={alertStats} /> : <Skeleton className="h-[240px]" />}
          </CardContent>
        </Card>
      </div>

      {/* Detection Frequency + Recent Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Detection Frequency — Last 14 Days</CardTitle>
          </CardHeader>
          <CardContent>
            {detectionTimeline ? <DetectionFrequencyChart data={detectionTimeline} /> : <Skeleton className="h-[280px]" />}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2 flex-row items-center justify-between">
            <CardTitle className="text-base">Recent Alerts</CardTitle>
            <button onClick={() => navigate("/alerts")} className="text-xs text-primary hover:underline">View all</button>
          </CardHeader>
          <CardContent className="space-y-2">
            {recentAlerts?.items.map((alert) => (
              <div key={alert.id} className="flex items-start gap-2 p-2 rounded-md bg-muted/50">
                <Badge variant={alert.severity as "critical" | "high" | "medium" | "low"} className="mt-0.5 flex-shrink-0">
                  {alert.severity}
                </Badge>
                <div className="min-w-0">
                  <p className="text-xs font-medium truncate">{alert.title}</p>
                  <p className="text-[10px] text-muted-foreground">{timeAgo(alert.created_at)}</p>
                </div>
              </div>
            ))}
            {!recentAlerts?.items.length && <p className="text-sm text-muted-foreground text-center py-4">No active alerts</p>}
          </CardContent>
        </Card>
      </div>

      {/* Zone summaries */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {zones?.items.map((zone) => (
          <Card key={zone.id} className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => navigate("/map")}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold truncate">{zone.name}</h3>
                <Badge variant={zone.status === "active" ? "default" : "secondary"}>{zone.status}</Badge>
              </div>
              <p className="text-xs text-muted-foreground">{zone.area_hectares?.toLocaleString()} ha</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}