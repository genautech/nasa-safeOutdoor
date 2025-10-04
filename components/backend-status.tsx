"use client"

import { useEffect, useState } from "react"
import { CheckCircle2, XCircle, Loader2, AlertTriangle } from "lucide-react"
import { healthCheck } from "@/lib/api"

export function BackendStatus() {
  const [status, setStatus] = useState<"checking" | "connected" | "disconnected" | "warning">("checking")
  const [message, setMessage] = useState("Checking backend connection...")
  const [details, setDetails] = useState<{ service?: string; version?: string } | null>(null)

  useEffect(() => {
    const checkConnection = async () => {
      try {
        const response = await healthCheck()
        setStatus("connected")
        setMessage("Backend connected")
        setDetails(response)
      } catch (error) {
        setStatus("disconnected")
        setMessage("Backend offline - using sample data")
        console.error("Backend health check failed:", error)
      }
    }

    checkConnection()

    // Recheck every 30 seconds
    const interval = setInterval(checkConnection, 30000)
    return () => clearInterval(interval)
  }, [])

  const getIcon = () => {
    switch (status) {
      case "checking":
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
      case "connected":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />
      case "warning":
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      case "disconnected":
        return <XCircle className="h-4 w-4 text-red-500" />
    }
  }

  const getBackgroundColor = () => {
    switch (status) {
      case "checking":
        return "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800"
      case "connected":
        return "bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800"
      case "warning":
        return "bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800"
      case "disconnected":
        return "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800"
    }
  }

  return (
    <div className={`fixed bottom-4 right-4 z-50 px-4 py-2 rounded-lg border ${getBackgroundColor()} backdrop-blur-sm`}>
      <div className="flex items-center gap-2">
        {getIcon()}
        <div className="text-sm">
          <p className="font-medium">{message}</p>
          {details && status === "connected" && (
            <p className="text-xs text-muted-foreground">
              {details.service} v{details.version}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
