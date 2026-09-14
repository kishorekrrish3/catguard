import { Routes, Route, Navigate } from "react-router-dom"
import { Shell } from "@/components/layout/Shell"
import { ProtectedRoute } from "@/components/layout/ProtectedRoute"
import { LoginPage } from "@/pages/Auth/LoginPage"
import { DashboardPage } from "@/pages/Dashboard/DashboardPage"
import { MapViewPage } from "@/pages/MapView/MapViewPage"
import { AnalyticsPage } from "@/pages/Analytics/AnalyticsPage"
import { AlertsPage } from "@/pages/Alerts/AlertsPage"
import { ReportsPage } from "@/pages/Reports/ReportsPage"
import { CommunityPage } from "@/pages/Community/CommunityPage"
import { SettingsPage } from "@/pages/Settings/SettingsPage"

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <ProtectedRoute>
            <Shell />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<DashboardPage />} />
        <Route path="/map" element={<MapViewPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/alerts" element={<AlertsPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/community" element={<CommunityPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}