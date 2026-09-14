import { Bell, TreePine, ChevronDown, LogOut, User, Settings } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useAuthStore } from "@/store/authStore"
import { useAlertStore } from "@/store/alertStore"
import { useMapStore } from "@/store/mapStore"
import { useZones } from "@/hooks/useZone"
import { useNavigate } from "react-router-dom"
import { useState, useRef, useEffect } from "react"

export function Header() {
  const { user, logout } = useAuthStore()
  const { unreadCount, markRead } = useAlertStore()
  const { selectedZoneId, setSelectedZone } = useMapStore()
  const { data: zonesData } = useZones()
  const navigate = useNavigate()
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [zoneMenuOpen, setZoneMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  const zones = zonesData?.items ?? []
  const selectedZone = zones.find((z) => z.id === selectedZoneId)

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setUserMenuOpen(false)
        setZoneMenuOpen(false)
      }
    }
    document.addEventListener("mousedown", handler)
    return () => document.removeEventListener("mousedown", handler)
  }, [])

  const handleLogout = async () => {
    await logout()
    navigate("/login")
  }

  return (
    <header className="flex h-16 items-center justify-between border-b bg-white px-4 shadow-sm z-50">
      {/* Logo */}
      <div className="flex items-center gap-2">
        <TreePine className="h-7 w-7 text-forest-700" />
        <div>
          <span className="text-lg font-bold text-forest-800">CAT-Guard</span>
          <span className="ml-2 hidden text-xs text-muted-foreground sm:inline">Forest Monitoring</span>
        </div>
      </div>

      {/* Zone Selector */}
      <div className="relative" ref={menuRef}>
        <Button variant="outline" size="sm" className="gap-2" onClick={() => setZoneMenuOpen(!zoneMenuOpen)}>
          <span className="max-w-[180px] truncate">{selectedZone?.name ?? "All Zones"}</span>
          <ChevronDown className="h-4 w-4" />
        </Button>
        {zoneMenuOpen && (
          <div className="absolute left-0 top-full z-50 mt-1 min-w-[220px] rounded-md border bg-white shadow-lg">
            <button
              className="w-full px-4 py-2 text-left text-sm hover:bg-muted font-medium"
              onClick={() => { setSelectedZone(null); setZoneMenuOpen(false) }}
            >
              All Zones
            </button>
            {zones.map((z) => (
              <button
                key={z.id}
                className="w-full px-4 py-2 text-left text-sm hover:bg-muted"
                onClick={() => { setSelectedZone(z.id); setZoneMenuOpen(false) }}
              >
                {z.name}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Right: Notifications + User */}
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          className="relative"
          onClick={() => { navigate("/alerts"); markRead() }}
        >
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge className="absolute -right-1 -top-1 h-5 w-5 rounded-full p-0 text-center text-xs leading-5" variant="destructive">
              {unreadCount > 9 ? "9+" : unreadCount}
            </Badge>
          )}
        </Button>

        <div className="relative">
          <Button variant="ghost" size="sm" className="gap-2" onClick={() => setUserMenuOpen(!userMenuOpen)}>
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-forest-700 text-white text-xs font-bold">
              {user?.full_name?.[0] ?? user?.username?.[0] ?? "U"}
            </div>
            <span className="hidden sm:inline max-w-[120px] truncate">{user?.full_name ?? user?.username}</span>
            <ChevronDown className="h-4 w-4" />
          </Button>
          {userMenuOpen && (
            <div className="absolute right-0 top-full z-50 mt-1 w-48 rounded-md border bg-white shadow-lg">
              <div className="border-b px-4 py-3">
                <p className="text-sm font-medium">{user?.full_name}</p>
                <p className="text-xs text-muted-foreground">{user?.role?.replace("_", " ")}</p>
              </div>
              <button className="flex w-full items-center gap-2 px-4 py-2 text-sm hover:bg-muted" onClick={() => navigate("/settings")}>
                <Settings className="h-4 w-4" /> Settings
              </button>
              <button className="flex w-full items-center gap-2 px-4 py-2 text-sm text-destructive hover:bg-muted" onClick={handleLogout}>
                <LogOut className="h-4 w-4" /> Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}