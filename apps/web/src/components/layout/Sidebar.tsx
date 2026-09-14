import { NavLink } from "react-router-dom"
import { LayoutDashboard, Map, BarChart3, Bell, FileText, Users, Settings, TreePine } from "lucide-react"
import { cn } from "@/lib/utils"
import { useAlertStore } from "@/store/alertStore"
import { Badge } from "@/components/ui/badge"

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/map", icon: Map, label: "Map View" },
  { to: "/analytics", icon: BarChart3, label: "Analytics" },
  { to: "/alerts", icon: Bell, label: "Alerts", showBadge: true },
  { to: "/reports", icon: FileText, label: "Reports" },
  { to: "/community", icon: Users, label: "Community" },
  { to: "/settings", icon: Settings, label: "Settings" },
]

export function Sidebar({ open }: { open: boolean }) {
  const { unreadCount } = useAlertStore()
  return (
    <aside className={cn(
      "flex flex-col border-r bg-forest-800 text-white transition-all duration-200",
      open ? "w-56" : "w-16"
    )}>
      <nav className="flex-1 py-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label, showBadge }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) => cn(
              "flex items-center gap-3 px-4 py-3 mx-2 rounded-lg text-sm font-medium transition-colors",
              isActive
                ? "bg-forest-600 text-white"
                : "text-forest-100 hover:bg-forest-700 hover:text-white"
            )}
          >
            <div className="relative flex-shrink-0">
              <Icon className="h-5 w-5" />
              {showBadge && unreadCount > 0 && (
                <span className="absolute -right-2 -top-2 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold">
                  {unreadCount > 9 ? "9+" : unreadCount}
                </span>
              )}
            </div>
            {open && <span className="truncate">{label}</span>}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-forest-700 px-4 py-3">
        {open && <p className="text-xs text-forest-400">CAT-Guard v1.0</p>}
      </div>
    </aside>
  )
}