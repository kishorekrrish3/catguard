import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { formatDistanceToNow, format } from "date-fns"
import type { AlertSeverity } from "@/types"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  return format(new Date(date), "MMM d, yyyy HH:mm")
}

export function formatDateShort(date: string | Date): string {
  return format(new Date(date), "MMM d")
}

export function timeAgo(date: string | Date): string {
  return formatDistanceToNow(new Date(date), { addSuffix: true })
}

export function formatNumber(n: number, decimals = 1): string {
  return n.toFixed(decimals)
}

export function formatPercent(n: number): string {
  return `${(n * 100).toFixed(1)}%`
}

export function severityColor(severity: AlertSeverity): string {
  switch (severity) {
    case "critical": return "text-red-600"
    case "high": return "text-orange-500"
    case "medium": return "text-yellow-500"
    case "low": return "text-blue-500"
  }
}

export function severityBg(severity: AlertSeverity): string {
  switch (severity) {
    case "critical": return "bg-red-100 text-red-800 border-red-200"
    case "high": return "bg-orange-100 text-orange-800 border-orange-200"
    case "medium": return "bg-yellow-100 text-yellow-800 border-yellow-200"
    case "low": return "bg-blue-100 text-blue-800 border-blue-200"
  }
}

export function statusColor(status: string): string {
  switch (status) {
    case "active": return "text-red-600"
    case "acknowledged": return "text-yellow-600"
    case "resolved": return "text-green-600"
    case "false_positive": return "text-gray-500"
    default: return "text-gray-600"
  }
}

export function sensorTypeIcon(type: string): string {
  const icons: Record<string, string> = {
    soil_moisture: "💧",
    soil_temperature: "🌡️",
    soil_ph: "⚗️",
    air_temperature: "🌤️",
    humidity: "💨",
    precipitation: "🌧️",
    motion: "🔍",
    camera: "📷",
    air_quality: "🌿",
  }
  return icons[type] || "📡"
}

export function ndviHealthLabel(ndvi: number): string {
  if (ndvi > 0.6) return "Excellent"
  if (ndvi > 0.4) return "Good"
  if (ndvi > 0.2) return "Fair"
  return "Poor"
}

export function ndviColor(ndvi: number): string {
  if (ndvi > 0.6) return "text-green-600"
  if (ndvi > 0.4) return "text-yellow-600"
  if (ndvi > 0.2) return "text-orange-500"
  return "text-red-600"
}