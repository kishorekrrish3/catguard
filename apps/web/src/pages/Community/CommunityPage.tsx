import { useState, FormEvent } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { communityApi } from "@/api/community"
import { timeAgo } from "@/lib/utils"
import { Trophy, Send, MapPin } from "lucide-react"

const TABS = ["Submit Report", "My Reports", "Leaderboard"]
const REPORT_TYPES = ["illegal_logging", "encroachment", "fire", "poaching", "waste_dumping", "other"]

export function CommunityPage() {
  const [activeTab, setActiveTab] = useState(0)
  const [form, setForm] = useState({ report_type: "illegal_logging", description: "", lat: "", lng: "", is_anonymous: false })
  const [submitted, setSubmitted] = useState<string | null>(null)
  const qc = useQueryClient()

  const { data: myReports } = useQuery({ queryKey: ["my-reports"], queryFn: () => communityApi.list({ size: 20 }) })
  const { data: leaderboard } = useQuery({ queryKey: ["leaderboard"], queryFn: () => communityApi.leaderboard() })

  const submit = useMutation({
    mutationFn: () => communityApi.submit({ ...form, lat: parseFloat(form.lat), lng: parseFloat(form.lng) }),
    onSuccess: (data) => { setSubmitted(data.id); qc.invalidateQueries({ queryKey: ["my-reports"] }) },
  })

  const useMyLocation = () => {
    navigator.geolocation?.getCurrentPosition((pos) => {
      setForm((f) => ({ ...f, lat: pos.coords.latitude.toFixed(6), lng: pos.coords.longitude.toFixed(6) }))
    })
  }

  const handleSubmit = (e: FormEvent) => { e.preventDefault(); submit.mutate() }

  const STATUS_COLORS: Record<string, string> = { pending: "secondary", under_review: "outline", verified: "default", resolved: "default", rejected: "destructive" }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-forest-800">Community Portal</h1>
        <p className="text-muted-foreground text-sm">Report forest threats and track community activity</p>
      </div>

      <div className="flex gap-2 border-b">
        {TABS.map((tab, i) => (
          <button key={tab} onClick={() => setActiveTab(i)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === i ? "border-forest-700 text-forest-700" : "border-transparent text-muted-foreground hover:text-foreground"}`}>
            {tab}
          </button>
        ))}
      </div>

      {activeTab === 0 && (
        <Card className="max-w-xl">
          <CardHeader><CardTitle className="text-base">Submit a Field Report</CardTitle></CardHeader>
          <CardContent>
            {submitted ? (
              <div className="text-center py-8 space-y-3">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-green-100 mx-auto"><Send className="h-8 w-8 text-green-600" /></div>
                <p className="font-semibold">Report submitted!</p>
                <p className="text-sm text-muted-foreground">Report ID: <span className="font-mono text-xs">{submitted.slice(0,8)}...</span></p>
                <Button size="sm" variant="outline" onClick={() => { setSubmitted(null); setForm({ report_type: "illegal_logging", description: "", lat: "", lng: "", is_anonymous: false }) }}>Submit another</Button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Report Type</label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {REPORT_TYPES.map((t) => (
                      <button key={t} type="button" onClick={() => setForm((f) => ({ ...f, report_type: t }))}
                        className={`px-3 py-1.5 text-xs rounded-full border capitalize ${form.report_type === t ? "bg-forest-700 text-white" : "hover:bg-muted"}`}>
                        {t.replace(/_/g, " ")}
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium">Description</label>
                  <textarea
                    value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                    className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    rows={3} placeholder="Describe what you observed..." required minLength={10}
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-sm font-medium">Latitude</label>
                    <Input value={form.lat} onChange={(e) => setForm((f) => ({ ...f, lat: e.target.value }))} placeholder="11.0456" required type="number" step="any" />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Longitude</label>
                    <Input value={form.lng} onChange={(e) => setForm((f) => ({ ...f, lng: e.target.value }))} placeholder="76.4523" required type="number" step="any" />
                  </div>
                </div>
                <Button type="button" variant="outline" size="sm" onClick={useMyLocation} className="gap-2">
                  <MapPin className="h-4 w-4" /> Use My Location
                </Button>
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input type="checkbox" checked={form.is_anonymous} onChange={(e) => setForm((f) => ({ ...f, is_anonymous: e.target.checked }))} />
                  Submit anonymously
                </label>
                <Button type="submit" className="w-full" disabled={submit.isPending}>
                  {submit.isPending ? "Submitting..." : "Submit Report"}
                </Button>
              </form>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 1 && (
        <div className="space-y-2">
          {myReports?.items.map((r) => (
            <Card key={r.id}>
              <CardContent className="p-4 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium capitalize">{r.report_type.replace(/_/g, " ")}</p>
                  <p className="text-xs text-muted-foreground">{timeAgo(r.submitted_at)}</p>
                </div>
                <Badge variant={STATUS_COLORS[r.status] as "default" | "secondary" | "outline" | "destructive"}>{r.status.replace(/_/g, " ")}</Badge>
              </CardContent>
            </Card>
          ))}
          {!myReports?.items.length && <p className="text-center text-muted-foreground py-16">No reports yet. Submit your first report!</p>}
        </div>
      )}

      {activeTab === 2 && (
        <Card>
          <CardHeader><CardTitle className="text-base flex items-center gap-2"><Trophy className="h-5 w-5 text-yellow-500" /> Top Contributors</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-3">
              {leaderboard?.map((entry) => (
                <div key={entry.user_id} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className={`text-sm font-bold w-6 ${entry.rank === 1 ? "text-yellow-500" : entry.rank === 2 ? "text-gray-400" : entry.rank === 3 ? "text-amber-600" : "text-muted-foreground"}`}>#{entry.rank}</span>
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-forest-100 text-forest-800 text-xs font-bold">
                      {(entry.full_name ?? entry.username)[0]}
                    </div>
                    <div>
                      <p className="text-sm font-medium">{entry.full_name ?? entry.username}</p>
                      <p className="text-xs text-muted-foreground">{entry.verified_reports} verified reports</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-forest-700">{entry.score} pts</p>
                    <p className="text-xs text-muted-foreground">{entry.total_reports} total</p>
                  </div>
                </div>
              ))}
              {!leaderboard?.length && <p className="text-center text-muted-foreground py-8">No contributors yet</p>}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}