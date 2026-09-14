import { useState } from "react"
import { useAuthStore } from "@/store/authStore"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { User, Bell, Shield, Palette, Save } from "lucide-react"

const TABS = [
  { key: "profile", label: "Profile", icon: User },
  { key: "notifications", label: "Notifications", icon: Bell },
  { key: "security", label: "Security", icon: Shield },
  { key: "appearance", label: "Appearance", icon: Palette },
]

export function SettingsPage() {
  const { user } = useAuthStore()
  const [activeTab, setActiveTab] = useState("profile")
  const [fullName, setFullName] = useState(user?.full_name ?? "")

  return (
    <div className="p-6 max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-forest-800">Settings</h1>
        <p className="text-muted-foreground text-sm">Manage your account and preferences</p>
      </div>

      <div className="flex flex-col md:flex-row gap-6">
        {/* Tab Nav */}
        <nav className="flex md:flex-col gap-1 md:w-48 flex-shrink-0">
          {TABS.map(({ key, label, icon: Icon }) => (
            <button key={key} onClick={() => setActiveTab(key)}
              className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm text-left transition-colors ${activeTab === key ? "bg-forest-100 text-forest-800 font-medium" : "hover:bg-muted text-muted-foreground"}`}>
              <Icon className="h-4 w-4" /> {label}
            </button>
          ))}
        </nav>

        {/* Tab Content */}
        <div className="flex-1 space-y-4">
          {activeTab === "profile" && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Profile Information</CardTitle>
                <CardDescription>Update your personal details</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-4">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-forest-700 text-white text-2xl font-bold">
                    {(user?.full_name ?? user?.username ?? "U")[0]}
                  </div>
                  <div>
                    <p className="font-semibold">{user?.full_name ?? user?.username}</p>
                    <p className="text-sm text-muted-foreground">{user?.email}</p>
                    <Badge className="mt-1" variant="secondary">{user?.role?.replace(/_/g, " ")}</Badge>
                  </div>
                </div>
                <Separator />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Full Name</label>
                    <Input value={fullName} onChange={(e) => setFullName(e.target.value)} className="mt-1" />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Email</label>
                    <Input value={user?.email ?? ""} disabled className="mt-1 opacity-60" />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Username</label>
                    <Input value={user?.username ?? ""} disabled className="mt-1 opacity-60" />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Role</label>
                    <Input value={user?.role?.replace(/_/g, " ") ?? ""} disabled className="mt-1 opacity-60 capitalize" />
                  </div>
                </div>
                <Button size="sm" className="gap-2"><Save className="h-4 w-4" /> Save Changes</Button>
              </CardContent>
            </Card>
          )}

          {activeTab === "notifications" && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Notification Preferences</CardTitle>
                <CardDescription>Configure how and when you receive alerts</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  ["Critical Alerts", "Receive immediate notifications for critical severity alerts"],
                  ["High Severity Alerts", "Get notified about high severity detections"],
                  ["Daily Summary", "Receive a daily digest of zone activity"],
                  ["Community Reports", "Get notified when new community reports are filed"],
                  ["Sensor Anomalies", "Alerts when sensors read anomalous values"],
                  ["System Health", "Notifications about system status and uptime"],
                ].map(([title, desc]) => (
                  <div key={title} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">{title}</p>
                      <p className="text-xs text-muted-foreground">{desc}</p>
                    </div>
                    <input type="checkbox" defaultChecked={title === "Critical Alerts" || title === "High Severity Alerts"} className="accent-forest-700 h-4 w-4" />
                  </div>
                ))}
                <Button size="sm" className="gap-2 mt-4"><Save className="h-4 w-4" /> Save Preferences</Button>
              </CardContent>
            </Card>
          )}

          {activeTab === "security" && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Security</CardTitle>
                <CardDescription>Manage your account security</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium">Current Password</label>
                    <Input type="password" className="mt-1" placeholder="••••••••" />
                  </div>
                  <div>
                    <label className="text-sm font-medium">New Password</label>
                    <Input type="password" className="mt-1" placeholder="••••••••" />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Confirm New Password</label>
                    <Input type="password" className="mt-1" placeholder="••••••••" />
                  </div>
                </div>
                <Button size="sm" variant="outline" className="gap-2"><Shield className="h-4 w-4" /> Change Password</Button>
                <Separator />
                <div className="space-y-2">
                  <p className="text-sm font-medium">Active Sessions</p>
                  <div className="rounded-md border p-3 flex items-center justify-between">
                    <div>
                      <p className="text-xs font-medium">Current Browser Session</p>
                      <p className="text-xs text-muted-foreground">Signed in as {user?.email}</p>
                    </div>
                    <Badge variant="default">Active</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === "appearance" && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Appearance</CardTitle>
                <CardDescription>Customize the look and feel</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm font-medium mb-2">Theme</p>
                  <div className="flex gap-3">
                    {["Light", "Dark", "System"].map((t) => (
                      <button key={t}
                        className={`px-4 py-2 rounded-md border text-sm ${t === "Light" ? "border-forest-700 text-forest-700 bg-forest-50" : "hover:bg-muted"}`}>
                        {t}
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium mb-2">Default Map Style</p>
                  <div className="flex gap-3">
                    {["Satellite", "Terrain", "Streets"].map((s) => (
                      <button key={s}
                        className={`px-4 py-2 rounded-md border text-sm ${s === "Satellite" ? "border-forest-700 text-forest-700 bg-forest-50" : "hover:bg-muted"}`}>
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
                <Button size="sm" className="gap-2 mt-2"><Save className="h-4 w-4" /> Save Preferences</Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}