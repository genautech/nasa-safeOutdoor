"use client"

import { useEffect, useState } from "react"

export function useServiceWorkerRegistration() {
  const [status, setStatus] = useState<"idle" | "registered" | "error">("idle")

  useEffect(() => {
    if (!("serviceWorker" in navigator)) {
      return
    }

    const register = async () => {
      try {
        const registration = await navigator.serviceWorker.register("/sw.js", { scope: "/" })
        if (registration.installing || registration.waiting || registration.active) {
          setStatus("registered")
        }
      } catch (error) {
        console.error("Service worker registration failed", error)
        setStatus("error")
      }
    }

    register()
  }, [])

  return status
}
