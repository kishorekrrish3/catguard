export type UserRole = "forest_manager" | "field_officer" | "data_analyst" | "community_reporter" | "administrator"
export type AlertSeverity = "critical" | "high" | "medium" | "low"
export type AlertStatus = "active" | "acknowledged" | "resolved" | "false_positive"
export type DetectionType = "illegal_logging" | "encroachment" | "fire_risk" | "vegetation_loss" | "suspicious_activity" | "flood_risk"
export type SensorType = "soil_moisture" | "soil_temperature" | "soil_ph" | "air_temperature" | "humidity" | "precipitation" | "motion" | "camera" | "air_quality"
export type ReportType = "illegal_logging" | "encroachment" | "fire" | "poaching" | "waste_dumping" | "other"
export type ReportStatus = "pending" | "under_review" | "verified" | "resolved" | "rejected"

export interface User {
  id: string
  username: string
  email: string
  full_name: string | null
  role: UserRole
  zone_id: string | null
  is_active: boolean
  last_login: string | null
  created_at: string
}

export interface Zone {
  id: string
  name: string
  description: string | null
  status: string
  area_hectares: number | null
  created_at: string
}

export interface ZoneSummary {
  zone: Zone
  ndvi_mean: number | null
  ndvi_trend: number | null
  active_alerts: number
  total_sensors: number
  healthy_sensors: number
  recent_detections: number
}

export interface Alert {
  id: string
  zone_id: string
  alert_type: string
  severity: AlertSeverity
  title: string
  description: string | null
  status: AlertStatus
  source_type: string
  acknowledged_at: string | null
  resolved_at: string | null
  created_at: string
}

export interface AlertRule {
  id: string
  name: string
  description: string | null
  zone_id: string | null
  alert_type: string
  condition_field: string
  condition_operator: string
  condition_value: number
  severity: string
  is_active: boolean
  cooldown_minutes: number
  created_at: string
}

export interface Detection {
  id: string
  zone_id: string
  detection_type: DetectionType
  confidence: number
  severity: AlertSeverity
  location: { lat: number; lng: number } | null
  image_url: string | null
  verified: boolean
  notes: string | null
  timestamp: string
  model_version: string
}

export interface Sensor {
  id: string
  zone_id: string
  sensor_type: SensorType
  name: string
  protocol: string
  battery_level: number | null
  is_active: boolean
  last_reading_at: string | null
  last_value: number | null
  installed_at: string
}

export interface SensorReading {
  id: string
  sensor_id: string
  timestamp: string
  value: number
  unit: string | null
  quality_flag: string
}

export interface SatelliteImagery {
  id: string
  zone_id: string
  acquisition_date: string
  cloud_cover_percent: number | null
  ndvi_mean: number | null
  ndvi_min: number | null
  ndvi_max: number | null
  savi_mean: number | null
  source: string
  processing_status: string
  created_at: string
}

export interface CommunityReport {
  id: string
  zone_id: string | null
  report_type: ReportType
  description: string
  status: ReportStatus
  is_anonymous: boolean
  photo_urls: string[]
  submitted_at: string
  updated_at: string | null
  resolution_notes: string | null
}

export interface LeaderboardEntry {
  rank: number
  user_id: string
  username: string
  full_name: string | null
  total_reports: number
  verified_reports: number
  score: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user_id: string
  role: string
}

export interface AlertStats {
  total: number
  by_severity: Record<string, number>
  by_status: Record<string, number>
  by_type: Record<string, number>
}

export interface SensorHealth {
  total: number
  active: number
  offline: number
  low_battery: number
  by_type: Record<string, number>
}

export interface DetectionTimelinePoint {
  date: string
  count: number
  by_type: Record<string, number>
}