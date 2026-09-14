import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { reportsApi } from "@/api/reports"
import { Download, FileText, Loader2 } from "lucide-react"

interface Template { id: string; name: string; description: string; formats: string[] }

export function ReportsPage() {
  const [generating, setGenerating] = useState<string | null>(null)
  const [format, setFormat] = useState<Record<string, string>>({})
  const { data: templates = [] } = useQuery<Template[]>({ queryKey: ["report-templates"], queryFn: reportsApi.templates })

  const generate = async (templateId: string) => {
    setGenerating(templateId)
    try {
      const fmt = format[templateId] ?? "csv"
      const res = await reportsApi.generate({ template_id: templateId, format: fmt })
      const blob = new Blob([res.data], { type: (res.headers["content-type"] as string) || undefined })
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url; a.download = `catguard_${templateId}.${fmt}`; a.click()
      URL.revokeObjectURL(url)
    } finally {
      setGenerating(null)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-forest-800">Reports</h1>
        <p className="text-muted-foreground text-sm">Generate and download monitoring reports</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {templates.map((t) => (
          <Card key={t.id} className="flex flex-col">
            <CardHeader>
              <div className="flex items-start gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-forest-100">
                  <FileText className="h-5 w-5 text-forest-700" />
                </div>
                <div>
                  <CardTitle className="text-sm">{t.name}</CardTitle>
                  <CardDescription className="text-xs mt-1">{t.description}</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="mt-auto space-y-3">
              <div className="flex gap-1">
                {t.formats.map((f) => (
                  <button key={f} onClick={() => setFormat((prev) => ({ ...prev, [t.id]: f }))}
                    className={`px-2 py-1 text-xs rounded border uppercase font-mono ${(format[t.id] ?? t.formats[0]) === f ? "bg-forest-700 text-white" : "hover:bg-muted"}`}>
                    {f}
                  </button>
                ))}
              </div>
              <Button size="sm" className="w-full" onClick={() => generate(t.id)} disabled={generating === t.id}>
                {generating === t.id ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Download className="h-4 w-4 mr-2" />}
                Generate
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}