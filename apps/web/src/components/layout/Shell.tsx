import { Outlet } from "react-router-dom"
import { Header } from "./Header"
import { Sidebar } from "./Sidebar"
import { useUIStore } from "@/store/uiStore"
import { useWebSocket } from "@/hooks/useWebSocket"
import { ToastContainer } from "@/components/alerts/ToastContainer"

export function Shell() {
  const { sidebarOpen, toggleSidebar } = useUIStore()
  const { status } = useWebSocket()

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-background">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar open={sidebarOpen} />
        <main className="flex-1 overflow-auto p-0">
          <Outlet />
        </main>
      </div>
      <ToastContainer />
    </div>
  )
}