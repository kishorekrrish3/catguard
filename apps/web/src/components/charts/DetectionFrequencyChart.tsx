import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts"
import type { DetectionTimelinePoint } from "@/types"
import { formatDateShort } from "@/lib/utils"

const TYPE_COLORS: Record<string, string> = {
  illegal_logging: "#ef4444",
  encroachment: "#f97316",
  fire_risk: "#dc2626",
  vegetation_loss: "#eab308",
  suspicious_activity: "#8b5cf6",
  flood_risk: "#3b82f6",
}

export function DetectionFrequencyChart({ data }: { data: DetectionTimelinePoint[] }) {
  const allTypes = Array.from(new Set(data.flatMap((d) => Object.keys(d.by_type))))
  const formatted = data.map((d) => ({ date: formatDateShort(d.date), ...d.by_type }))
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={formatted} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} />
        <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
        <Tooltip />
        <Legend />
        {allTypes.map((type) => (
          <Bar key={type} dataKey={type} name={type.replace(/_/g, " ")} stackId="a" fill={TYPE_COLORS[type] ?? "#6b7280"} />
        ))}
      </BarChart>
    </ResponsiveContainer>
  )
}