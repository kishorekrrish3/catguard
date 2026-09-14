import { create } from "zustand"
import type { Alert } from "@/types"

interface AlertState {
  liveAlerts: Alert[]
  unreadCount: number
  addLiveAlert: (alert: Alert) => void
  markRead: () => void
  clearLiveAlerts: () => void
}

export const useAlertStore = create<AlertState>((set) => ({
  liveAlerts: [],
  unreadCount: 0,
  addLiveAlert: (alert) =>
    set((s) => ({ liveAlerts: [alert, ...s.liveAlerts].slice(0, 20), unreadCount: s.unreadCount + 1 })),
  markRead: () => set({ unreadCount: 0 }),
  clearLiveAlerts: () => set({ liveAlerts: [], unreadCount: 0 }),
}))