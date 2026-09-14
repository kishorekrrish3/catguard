import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Legend } from "recharts"
import { formatDateShort } from "@/lib/utils"

interface NDVIDataPoint { date: string; ndvi_mean: number; ndvi_min?: number; ndvi_max?: number }

export function NDVITrendChart({ data }: { data: NDVIDataPoint[] }) {
  const formatted = data.map((d) => ({ ...d, date: formatDateShort(d.date) }))
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={formatted} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} />
        <YAxis domain={[0, 1]} tickFormatter={(v) => v.toFixed(1)} tick={{ fontSize: 11 }} />
        <Tooltip formatter={(v: number) => [v.toFixed(3), "NDVI"]} />
        <Legend />
        <ReferenceLine y={0.3} stroke="#f59e0b" strokeDasharray="4 4" label={{ value: "0.3 threshold", fontSize: 10, fill: "#f59e0b" }} />
        <ReferenceLine y={0.6} stroke="#16a34a" strokeDasharray="4 4" label={{ value: "0.6 healthy", fontSize: 10, fill: "#16a34a" }} />
        <Line type="monotone" dataKey="ndvi_mean" name="NDVI Mean" stroke="#16a34a" strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="ndvi_min" name="NDVI Min" stroke="#86efac" strokeWidth={1} dot={false} strokeDasharray="3 3" />
        <Line type="monotone" dataKey="ndvi_max" name="NDVI Max" stroke="#15803d" strokeWidth={1} dot={false} strokeDasharray="3 3" />
      </LineChart>
    </ResponsiveContainer>
  )
}