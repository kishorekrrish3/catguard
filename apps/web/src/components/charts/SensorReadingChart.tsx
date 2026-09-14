import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import type { SensorReading } from "@/types"
import { format } from "date-fns"

export function SensorReadingChart({ data, unit }: { data: SensorReading[]; unit?: string }) {
  const formatted = data.map((r) => ({ time: format(new Date(r.timestamp), "MM/dd HH:mm"), value: r.value }))
  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={formatted} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <defs>
          <linearGradient id="sensorGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#16a34a" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#16a34a" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey="time" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
        <YAxis tick={{ fontSize: 11 }} />
        <Tooltip formatter={(v: number) => [`${v.toFixed(2)} ${unit ?? ""}`, "Value"]} />
        <Area type="monotone" dataKey="value" stroke="#16a34a" fill="url(#sensorGrad)" strokeWidth={2} dot={false} />
      </AreaChart>
    </ResponsiveContainer>
  )
}