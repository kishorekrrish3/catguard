import { useUIStore } from "@/store/uiStore"
import { X, CheckCircle, AlertTriangle } from "lucide-react"
import { cn } from "@/lib/utils"

export function ToastContainer() {
  const { toasts, removeToast } = useUIStore()
  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 max-w-sm">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={cn(
            "flex items-start gap-3 rounded-lg border p-4 shadow-lg bg-white animate-in slide-in-from-bottom-2",
            toast.variant === "destructive" && "border-red-200 bg-red-50"
          )}
        >
          {toast.variant === "destructive"
            ? <AlertTriangle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
            : <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
          }
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold">{toast.title}</p>
            {toast.description && <p className="text-xs text-muted-foreground mt-0.5">{toast.description}</p>}
          </div>
          <button onClick={() => removeToast(toast.id)} className="text-muted-foreground hover:text-foreground">
            <X className="h-4 w-4" />
          </button>
        </div>
      ))}
    </div>
  )
}