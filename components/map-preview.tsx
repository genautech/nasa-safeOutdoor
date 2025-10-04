"use client"

import { useState, useEffect } from "react"
import { MapPin, ZoomIn, ZoomOut } from "lucide-react"
import { Button } from "@/components/ui/button"
import { motion } from "framer-motion"

interface MapPreviewProps {
  mode: "single" | "route"
  location?: { lat: number; lon: number }
  waypoints?: Array<{ lat: number; lon: number; order: number }>
  className?: string
}

export function MapPreview({ mode, location, waypoints, className = "" }: MapPreviewProps) {
  const [zoom, setZoom] = useState(12)
  const [showPin, setShowPin] = useState(false)

  // Calculate center point
  const center =
    mode === "single" && location
      ? location
      : waypoints && waypoints.length > 0
        ? {
            lat: waypoints.reduce((sum, w) => sum + w.lat, 0) / waypoints.length,
            lon: waypoints.reduce((sum, w) => sum + w.lon, 0) / waypoints.length,
          }
        : { lat: 40.7829, lon: -73.9654 }

  // Animate pin drop
  useEffect(() => {
    if (mode === "single" && location) {
      setShowPin(false)
      const timer = setTimeout(() => setShowPin(true), 200)
      return () => clearTimeout(timer)
    }
  }, [location, mode])

  // Convert lat/lon to tile coordinates for OpenStreetMap
  const getTileUrl = (z: number, lat: number, lon: number) => {
    const x = Math.floor(((lon + 180) / 360) * Math.pow(2, z))
    const y = Math.floor(
      ((1 - Math.log(Math.tan((lat * Math.PI) / 180) + 1 / Math.cos((lat * Math.PI) / 180)) / Math.PI) / 2) *
        Math.pow(2, z),
    )
    return `https://tile.openstreetmap.org/${z}/${x}/${y}.png`
  }

  return (
    <div className={`relative rounded-xl overflow-hidden bg-gradient-to-br from-blue-400 via-green-300 to-green-400 ${className}`}>
      {/* Enhanced gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-200 via-green-200 to-green-200 dark:from-blue-900 dark:via-green-900 dark:to-green-900" />

      {/* Decorative elements - trees and buildings */}
      <div className="absolute inset-0 opacity-20">
        <svg className="w-full h-full" viewBox="0 0 400 300">
          {/* Trees */}
          <g>
            <polygon points="50,220 40,240 60,240" fill="currentColor" className="text-green-700" />
            <rect x="47" y="240" width="6" height="10" fill="currentColor" className="text-amber-800" />
          </g>
          <g>
            <polygon points="350,200 340,220 360,220" fill="currentColor" className="text-green-700" />
            <rect x="347" y="220" width="6" height="10" fill="currentColor" className="text-amber-800" />
          </g>
          <g>
            <polygon points="100,260 90,280 110,280" fill="currentColor" className="text-green-700" />
            <rect x="97" y="280" width="6" height="10" fill="currentColor" className="text-amber-800" />
          </g>
          {/* Buildings */}
          <rect x="280" y="220" width="30" height="40" fill="currentColor" className="text-gray-600" />
          <rect x="320" y="210" width="25" height="50" fill="currentColor" className="text-gray-700" />
          <rect x="150" y="240" width="35" height="35" fill="currentColor" className="text-gray-600" />
        </svg>
      </div>

      {/* Subtle grid overlay */}
      <div className="absolute inset-0 opacity-10">
        <svg className="w-full h-full" viewBox="0 0 400 300">
          {Array.from({ length: 10 }).map((_, i) => (
            <line
              key={`h-${i}`}
              x1="0"
              y1={i * 30}
              x2="400"
              y2={i * 30}
              stroke="currentColor"
              strokeWidth="1"
              className="text-gray-700"
            />
          ))}
          {Array.from({ length: 14 }).map((_, i) => (
            <line
              key={`v-${i}`}
              x1={i * 30}
              y1="0"
              x2={i * 30}
              y2="300"
              stroke="currentColor"
              strokeWidth="1"
              className="text-gray-700"
            />
          ))}
        </svg>
      </div>

      {/* Simplified map representation */}
      <div className="relative w-full h-full flex items-center justify-center">
        {/* Location pins or route */}
        {mode === "single" && location && (
          <motion.div 
            className="relative z-10"
            initial={{ y: -50, opacity: 0, scale: 0.5 }}
            animate={showPin ? { y: 0, opacity: 1, scale: 1 } : {}}
            transition={{ 
              type: "spring", 
              stiffness: 300, 
              damping: 20,
              delay: 0.1 
            }}
          >
            <MapPin className="w-16 h-16 text-red-600 fill-red-600 drop-shadow-2xl" strokeWidth={2.5} />
            <motion.div
              className="absolute top-0 left-1/2 -translate-x-1/2 w-16 h-16"
              initial={{ scale: 1, opacity: 0.5 }}
              animate={{ scale: 1.5, opacity: 0 }}
              transition={{ duration: 1, repeat: Infinity }}
            >
              <div className="w-full h-full rounded-full bg-red-600/30" />
            </motion.div>
          </motion.div>
        )}

        {mode === "route" && waypoints && waypoints.length > 0 && (
          <div className="relative z-10 w-full h-full">
            <svg className="w-full h-full" viewBox="0 0 400 300">
              {/* Route line */}
              {waypoints.length > 1 && (
                <polyline
                  points={waypoints
                    .sort((a, b) => a.order - b.order)
                    .map((w, i) => {
                      const x = 100 + i * 100
                      const y = 150 + (i % 2 === 0 ? -30 : 30)
                      return `${x},${y}`
                    })
                    .join(" ")}
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="3"
                  strokeDasharray="5,5"
                  className="text-forest-500"
                />
              )}

              {/* Waypoint markers */}
              {waypoints.map((w, i) => {
                const x = 100 + i * 100
                const y = 150 + (i % 2 === 0 ? -30 : 30)
                return (
                  <g key={w.order}>
                    <circle cx={x} cy={y} r="12" fill="currentColor" className="text-forest-500" />
                    <text
                      x={x}
                      y={y + 5}
                      textAnchor="middle"
                      className="text-xs font-bold fill-white"
                      style={{ fontSize: "12px" }}
                    >
                      {i + 1}
                    </text>
                  </g>
                )
              })}
            </svg>
          </div>
        )}
      </div>

      {/* Zoom controls */}
      <div className="absolute bottom-4 right-4 flex flex-col gap-2">
        <Button
          size="icon"
          variant="secondary"
          className="h-8 w-8 bg-background/80 backdrop-blur-sm"
          onClick={() => setZoom((z) => Math.min(z + 1, 18))}
        >
          <ZoomIn className="h-4 w-4" />
        </Button>
        <Button
          size="icon"
          variant="secondary"
          className="h-8 w-8 bg-background/80 backdrop-blur-sm"
          onClick={() => setZoom((z) => Math.max(z - 1, 8))}
        >
          <ZoomOut className="h-4 w-4" />
        </Button>
      </div>

      {/* Zoom level indicator */}
      <div className="absolute top-4 right-4 bg-background/80 backdrop-blur-sm px-3 py-1.5 rounded-full text-xs font-medium">
        Zoom: {zoom}
      </div>

      {/* Map preview watermark */}
      <div className="absolute bottom-2 left-2 text-xs text-muted-foreground bg-background/70 backdrop-blur-sm px-3 py-1.5 rounded-full font-medium">
        Map Preview
      </div>
    </div>
  )
}
