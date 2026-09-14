import { useState } from "react"
import { useAlerts, useAcknowledgeAlert, useResolveAlert } from "@/hooks/useAlerts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { timeAgo, severityBg } from "@/lib/utils"
import { CheckCircle, XCircle, AlertTriangle, Clock } from "lucide-react"
import { cn } from "@/lib/utils"

const STATUS_FILTERS = ["all", "active", "acknowledged", "resolved"]
const SEVERITY_FILTERS = ["all", "critical", "high", "medium", "low"]

export function AlertsPage() {
  const [status, setStatus] = useState("active")
  const [severity, setSeverity] = useState("all")
  const [page, setPage] = useState(1)

  const { data, isLoading } = useAlerts({
    status: status === "all" ? undefined : status,
    severity: severity === "all" ? undefined : severity,
    page, size: 20,
  })
  const acknowledge = useAcknowledgeAlert()
  const resolve = useResolveAlert()

  const alerts = data?.items ?? []

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-forest-800">Alerts</h1>
        <p className="text-muted-foreground text-sm">{data?.total ?? 0} total alerts</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <div className="flex gap-1">
          {STATUS_FILTERS.map((s) => (
            <button key={s} onClick={() => { setStatus(s); setPage(1) }}
              className={cn("px-3 py-1.5 text-sm rounded-md capitalize border", status === s ? "bg-forest-700 text-white border-forest-700" : "hover:bg-muted")}>
              {s}
            </button>
          ))}
        </div>
        <div className="flex gap-1">
          {SEVERITY_FILTERS.map((s) => (
            <button key={s} onClick={() => { setSeverity(s); setPage(1) }}
              className={cn("px-3 py-1.5 text-sm rounded-md capitalize border", severity === s ? "bg-forest-700 text-white border-forest-700" : "hover:bg-muted")}>
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Alert List */}
      <div className="space-y-2">
        {isLoading && Array(5).fill(0).map((_, i) => <Skeleton key={i} className="h-24" />)}
        {alerts.map((alert) => (
          <Card key={alert.id} className={cn("border-l-4", alert.severity === "critical" ? "border-l-red-500" : alert.severity === "high" ? "border-l-orange-500" : alert.severity === "medium" ? "border-l-yellow-500" : "border-l-blue-500")}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3 flex-1 min-w-0">
                  <AlertTriangle className={cn("h-5 w-5 flex-shrink-0 mt-0.5", alert.severity === "critical" ? "text-red-500" : alert.severity === "high" ? "text-orange-500" : "text-yellow-500")} />
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-semibold text-sm">{alert.title}</span>
                      <span className={cn("text-xs px-2 py-0.5 rounded-full border", severityBg(alert.severity))}>{alert.severity}</span>
                      <span className="text-xs text-muted-foreground capitalize">{alert.status.replace("_", " ")}</span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">{alert.description}</p>
                    <p className="text-[10px] text-muted-foreground mt-1 flex items-center gap-1"><Clock className="h-3 w-3" />{timeAgo(alert.created_at)}</p>
                  </div>
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  {alert.status === "active" && (
                    <Button size="sm" variant="outline" onClick={() => acknowledge.mutate({ id: alert.id })} disabled={acknowledge.isPending}>
                      <CheckCircle className="h-4 w-4 mr-1" /> Ack
                    </Button>
                  )}
                  {(alert.status === "active" || alert.status === "acknowledged") && (
                    <Button size="sm" onClick={() => resolve.mutate(alert.id)} disabled={resolve.isPending}>
                      <XCircle className="h-4 w-4 mr-1" /> Resolve
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
        {!isLoading && alerts.length === 0 && (
          <div className="text-center py-16 text-muted-foreground">
            <CheckCircle className="h-12 w-12 mx-auto mb-3 text-green-500 opacity-50" />
            <p>No alerts matching your filters</p>
          </div>
        )}
      </div>

      {/* Pagination */}
      {data && data.pages > 1 && (
        <div className="flex justify-center gap-2">
          <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>Previous</Button>
          <span className="text-sm self-center text-muted-foreground">Page {page} of {data.pages}</span>
          <Button variant="outline" size="sm" disabled={page === data.pages} onClick={() => setPage(p => p + 1)}>Next</Button>
        </div>
      )}
    </div>
  )
}