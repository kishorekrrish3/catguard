import { Navigate } from "react-router-dom"
import { useAuthStore } from "@/store/authStore"
import { useEffect } from "react"

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, initialize } = useAuthStore()

  useEffect(() => { initialize() }, [initialize])

  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}