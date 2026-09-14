import { useEffect, useRef, useState, useCallback } from "react"
import { useAuthStore } from "@/store/authStore"
import { useAlertStore } from "@/store/alertStore"
import { useUIStore } from "@/store/uiStore"

type WsStatus = "connecting" | "connected" | "disconnected"

export function useWebSocket() {
  const [status, setStatus] = useState<WsStatus>("disconnected")
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const attemptsRef = useRef(0)
  const { accessToken } = useAuthStore()
  const { addLiveAlert } = useAlertStore()
  const { addToast } = useUIStore()

  const connect = useCallback(() => {
    if (!accessToken) return
    const wsUrl = (import.meta.env.VITE_WS_URL || "ws://localhost:8000")
    const ws = new WebSocket(`${wsUrl}/ws/alerts?token=${accessToken}`)
    wsRef.current = ws
    setStatus("connecting")

    ws.onopen = () => {
      setStatus("connected")
      attemptsRef.current = 0
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.event === "pong" || data.event === "connected") return
        if (data.id) {
          addLiveAlert(data)
          addToast({
            title: `🚨 ${data.title || "New Alert"}`,
            description: data.description || `Severity: ${data.severity}`,
            variant: data.severity === "critical" || data.severity === "high" ? "destructive" : "default",
          })
        }
      } catch {}
    }

    ws.onclose = () => {
      setStatus("disconnected")
      const delay = Math.min(1000 * 2 ** attemptsRef.current, 30000)
      attemptsRef.current++
      reconnectRef.current = setTimeout(connect, delay)
    }

    ws.onerror = () => ws.close()
  }, [accessToken, addLiveAlert, addToast])

  useEffect(() => {
    if (accessToken) connect()
    return () => {
      wsRef.current?.close()
      if (reconnectRef.current) clearTimeout(reconnectRef.current)
    }
  }, [accessToken, connect])

  const ping = useCallback(() => wsRef.current?.send("ping"), [])

  return { status, ping }
}