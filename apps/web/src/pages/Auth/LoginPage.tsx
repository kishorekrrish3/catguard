import { useState, FormEvent } from "react"
import { useNavigate } from "react-router-dom"
import { TreePine, Lock, Mail, Eye, EyeOff } from "lucide-react"
import { useAuthStore } from "@/store/authStore"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"

export function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState("")
  const { login, isLoading } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError("")
    try {
      await login(email, password)
      navigate("/")
    } catch {
      setError("Invalid email or password. Please try again.")
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-forest-800 to-forest-600 p-4">
      <Card className="w-full max-w-md shadow-2xl">
        <CardHeader className="text-center space-y-3 pb-6">
          <div className="flex justify-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-forest-700">
              <TreePine className="h-9 w-9 text-white" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-forest-800">CAT-Guard</CardTitle>
          <CardDescription>Catchment Area Treatment Forest Monitoring System</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  type="email"
                  placeholder="manager@catguard.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10"
                  required
                />
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  type={showPassword ? "text" : "password"}
                  placeholder="Your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-10 pr-10"
                  required
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>
            {error && <p className="text-sm text-destructive bg-red-50 border border-red-200 rounded p-2">{error}</p>}
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Signing in..." : "Sign In"}
            </Button>
          </form>
          <div className="mt-6 rounded-md bg-muted p-3">
            <p className="text-xs font-medium text-muted-foreground mb-2">Demo credentials (password: CatGuard@123)</p>
            {[
              ["Forest Manager", "manager@catguard.com"],
              ["Field Officer", "officer@catguard.com"],
              ["Data Analyst", "analyst@catguard.com"],
            ].map(([role, em]) => (
              <button key={em} onClick={() => { setEmail(em); setPassword("CatGuard@123") }}
                className="block text-xs text-forest-700 hover:underline">
                {role}: {em}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}