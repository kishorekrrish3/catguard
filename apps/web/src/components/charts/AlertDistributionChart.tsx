import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts"
import type { AlertStats } from "@/types"

const COLORS = { critical: "#ef4444", high: "#f97316", medium: "#eab308", low: "#3b82f6" }

export function AlertDistributionChart({ stats }: { stats: AlertStats }) {
  const data = Object.entries(stats.by_severity).map(([name, value]) => ({ name, value }))
  return (
    <ResponsiveContainer width="100%" height={240}>
      <PieChart>
        <Pie data={data} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={3} dataKey="value">
          {data.map((entry) => (
            <Cell key={entry.name} fill={COLORS[entry.name as keyof typeof COLORS] ?? "#6b7280"} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  )
}