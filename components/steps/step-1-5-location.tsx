/**
 * IMPORTANT: This file is step-1-5-location.tsx (with HYPHENS)
 * Do NOT create step-1.5-location.tsx (with PERIOD)
 * The import in app/page.tsx uses the hyphen version
 */

"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { MapPin, Route, Info, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { LocationData } from "@/lib/types"
import { LocationSearch } from "@/components/location-search"
import dynamic from "next/dynamic"

// Import map dynamically to avoid SSR issues
const LocationMap = dynamic(
  () => import("@/components/location-map").then((mod) => mod.LocationMap),
  { ssr: false, loading: () => <div className="w-full h-full bg-muted animate-pulse rounded-lg" /> }
)

interface Location {
  name: string
  displayName: string
  lat: number
  lon: number
  type: string
}

interface Step1_5LocationProps {
  onNext: () => void
  onBack: () => void
  onLocationSelect: (data: LocationData) => void
}

export function Step1_5Location({ onNext, onBack, onLocationSelect }: Step1_5LocationProps) {
  const [mode, setMode] = useState<"single" | "route">("single")
  const [selectedLocation, setSelectedLocation] = useState<Location>({
    name: "New York, Central Park",
    displayName: "Central Park, New York, NY, USA",
    lat: 40.7829,
    lon: -73.9654,
    type: "park"
  })
  const [routeStart, setRouteStart] = useState<Location | null>(null)
  const [routeEnd, setRouteEnd] = useState<Location | null>(null)

  const handleModeChange = (newMode: "single" | "route") => {
    setMode(newMode)
  }

  const calculateDistance = (start: Location, end: Location): string => {
    const R = 6371 // Earth radius in km
    const dLat = (end.lat - start.lat) * Math.PI / 180
    const dLon = (end.lon - start.lon) * Math.PI / 180
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(start.lat * Math.PI / 180) * Math.cos(end.lat * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2)
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
    return (R * c).toFixed(1)
  }

  const handleNext = () => {
    if (mode === "single") {
      // Create LocationData for single location
      const locationData: LocationData = {
        mode: "single",
        single: {
          id: "selected-location",
          city: selectedLocation.name,
          address: selectedLocation.displayName,
          lat: selectedLocation.lat,
          lon: selectedLocation.lon,
        }
      }
      onLocationSelect(locationData)
    } else {
      // Create LocationData for route
      if (routeStart && routeEnd) {
        const distance = parseFloat(calculateDistance(routeStart, routeEnd))
        const locationData: LocationData = {
          mode: "route",
          route: {
            waypoints: [
              {
                id: "start",
                city: routeStart.name,
                address: routeStart.displayName,
                lat: routeStart.lat,
                lon: routeStart.lon,
                order: 0,
              },
              {
                id: "end",
                city: routeEnd.name,
                address: routeEnd.displayName,
                lat: routeEnd.lat,
                lon: routeEnd.lon,
                order: 1,
              }
            ],
            totalDistance: distance,
            estimatedDuration: Math.round(distance * 3), // 3 min per km estimate
          }
        }
    onLocationSelect(locationData)
      }
    }
    onNext()
  }

  const isValid = mode === "single" ? 
    (selectedLocation.lat !== 0 && selectedLocation.lon !== 0) : 
    (routeStart !== null && routeEnd !== null)

  return (
    <div className="min-h-screen bg-gradient-to-br from-forest-50 via-sky-50 to-forest-50 dark:from-forest-950 dark:via-sky-950 dark:to-forest-950">
      <div className="lg:hidden">
        <div className="container max-w-2xl mx-auto px-4 py-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="space-y-6"
          >
            <div className="text-center space-y-2">
              <h1 className="text-3xl font-bold text-balance">Where's Your Adventure?</h1>
              <p className="text-muted-foreground text-balance">We'll analyze air quality conditions along your path</p>
            </div>

            <div className="inline-flex items-center gap-1 p-1 bg-gray-100 dark:bg-gray-800 rounded-full w-full">
              <button
                onClick={() => handleModeChange("single")}
                className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-full font-semibold text-sm transition-all duration-200 ${
                  mode === "single"
                    ? "bg-black text-white shadow-md"
                    : "bg-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                }`}
              >
                <MapPin className="h-4 w-4" />
                Location
              </button>
              <button
                onClick={() => handleModeChange("route")}
                className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-full font-semibold text-sm transition-all duration-200 ${
                  mode === "route"
                    ? "bg-black text-white shadow-md"
                    : "bg-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                }`}
              >
                <Route className="h-4 w-4" />
                Route
              </button>
            </div>

            {mode === "single" ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
                className="space-y-4"
              >
                <LocationSearch
                  onLocationSelect={setSelectedLocation}
                  defaultValue={selectedLocation.displayName}
                />

                <div className="h-[calc(100vh-400px)] min-h-[300px]">
                  <LocationMap
                    lat={selectedLocation.lat}
                    lon={selectedLocation.lon}
                    locationName={selectedLocation.name}
                    onMapClick={(lat, lon) => {
                      setSelectedLocation({
                        name: "Custom Location",
                        displayName: `${lat.toFixed(4)}, ${lon.toFixed(4)}`,
                        lat,
                        lon,
                        type: "custom"
                      })
                    }}
                  />
                </div>

                <div className="bg-card rounded-xl p-4 border border-border space-y-2 hover:border-green-500/50 transition-colors duration-200">
                  <h3 className="font-semibold">{selectedLocation.name}</h3>
                  <p className="text-sm text-muted-foreground">{selectedLocation.displayName}</p>
                  <p className="text-xs text-muted-foreground">
                    {selectedLocation.lat.toFixed(4)}, {selectedLocation.lon.toFixed(4)}
                  </p>
                </div>
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
                className="space-y-4"
              >
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium mb-1 block">Starting Point</label>
                    <LocationSearch
                      onLocationSelect={setRouteStart}
                      defaultValue={routeStart?.displayName}
                    />
                  </div>

                  <div>
                    <label className="text-sm font-medium mb-1 block">Destination</label>
                    <LocationSearch
                      onLocationSelect={setRouteEnd}
                      defaultValue={routeEnd?.displayName}
                    />
                  </div>
                </div>

                {routeStart && routeEnd && (
                  <>
                    <div className="h-[calc(100vh-500px)] min-h-[300px]">
                      <LocationMap
                        lat={(routeStart.lat + routeEnd.lat) / 2}
                        lon={(routeStart.lon + routeEnd.lon) / 2}
                        locationName={`Route: ${routeStart.name} → ${routeEnd.name}`}
                      />
                    </div>

                    <div className="bg-card rounded-xl p-4 border border-border">
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                          <p className="text-2xl font-bold text-forest-600">{calculateDistance(routeStart, routeEnd)}</p>
                      <p className="text-xs text-muted-foreground">km</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-sky-600">
                            {Math.floor(parseFloat(calculateDistance(routeStart, routeEnd)) * 3 / 60)}h{" "}
                            {Math.round(parseFloat(calculateDistance(routeStart, routeEnd)) * 3 % 60)}m
                      </p>
                      <p className="text-xs text-muted-foreground">duration</p>
                    </div>
                    <div>
                          <p className="text-2xl font-bold text-forest-600">5</p>
                      <p className="text-xs text-muted-foreground">checkpoints</p>
                    </div>
                  </div>
                </div>
                  </>
                )}
              </motion.div>
            )}

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-sky-100 dark:bg-sky-950 rounded-xl p-4 border border-sky-200 dark:border-sky-800"
            >
              <div className="flex gap-3">
                <Info className="h-5 w-5 text-sky-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-sky-900 dark:text-sky-100">
                  {mode === "single"
                    ? "We'll analyze air quality at your selected location and nearby areas"
                    : "We'll analyze air quality at multiple points along your route and warn if conditions worsen"}
                </p>
              </div>
            </motion.div>

            <div className="flex justify-center gap-3 pt-4">
              <Button 
                variant="outline" 
                onClick={onBack} 
                className="flex-1 max-w-[200px]"
              >
                Back
              </Button>
              <Button 
                onClick={handleNext} 
                disabled={!isValid} 
                className="flex-1 max-w-[200px] bg-black text-white hover:bg-black/90 disabled:bg-gray-300 disabled:text-gray-500"
              >
                Next
              </Button>
            </div>
          </motion.div>
        </div>
      </div>

      <div className="hidden lg:block h-screen">
        <div className="grid grid-cols-[60%_40%] h-full">
          <div className="relative h-full">
            <div className="absolute inset-0">
              {mode === "single" ? (
                <LocationMap
                  lat={selectedLocation.lat}
                  lon={selectedLocation.lon}
                  locationName={selectedLocation.name}
                  onMapClick={(lat, lon) => {
                    setSelectedLocation({
                      name: "Custom Location",
                      displayName: `${lat.toFixed(4)}, ${lon.toFixed(4)}`,
                      lat,
                      lon,
                      type: "custom"
                    })
                  }}
                />
              ) : routeStart && routeEnd ? (
                <LocationMap
                  lat={(routeStart.lat + routeEnd.lat) / 2}
                  lon={(routeStart.lon + routeEnd.lon) / 2}
                  locationName={`Route: ${routeStart.name} → ${routeEnd.name}`}
                />
              ) : (
                <div className="w-full h-full bg-muted flex items-center justify-center">
                  <p className="text-muted-foreground">Select start and end points to see route</p>
                </div>
              )}
            </div>
            <div className="absolute top-4 right-4 z-10 bg-white dark:bg-gray-800 px-4 py-2 rounded-full shadow-lg">
              <span className="text-sm font-medium">Step 2 of 5</span>
            </div>
          </div>

          <div className="bg-background border-l border-border overflow-y-auto">
            <div className="p-6 space-y-6">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold">Where's Your Adventure?</h1>
                <p className="text-muted-foreground">We'll analyze air quality conditions along your path</p>
              </div>

              <div className="inline-flex items-center gap-1 p-1 bg-gray-100 dark:bg-gray-800 rounded-full w-full">
                <button
                  onClick={() => handleModeChange("single")}
                  className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-full font-semibold text-sm transition-all duration-200 ${
                    mode === "single"
                      ? "bg-black text-white shadow-md"
                      : "bg-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                  }`}
                >
                  <MapPin className="h-4 w-4" />
                  Location
                </button>
                <button
                  onClick={() => handleModeChange("route")}
                  className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-full font-semibold text-sm transition-all duration-200 ${
                    mode === "route"
                      ? "bg-black text-white shadow-md"
                      : "bg-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                  }`}
                >
                  <Route className="h-4 w-4" />
                  Route
                </button>
              </div>

              {mode === "single" ? (
                <div className="space-y-4">
                  <LocationSearch
                    onLocationSelect={setSelectedLocation}
                    defaultValue={selectedLocation.displayName}
                  />

                  <div className="bg-card rounded-xl p-4 border border-border space-y-2 hover:border-green-500/50 transition-colors duration-200">
                    <h3 className="font-semibold text-lg">{selectedLocation.name}</h3>
                    <p className="text-sm text-muted-foreground">{selectedLocation.displayName}</p>
                  <p className="text-xs text-muted-foreground">
                      {selectedLocation.lat.toFixed(4)}, {selectedLocation.lon.toFixed(4)}
                  </p>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-medium mb-1 block">Starting Point</label>
                      <LocationSearch
                        onLocationSelect={setRouteStart}
                        defaultValue={routeStart?.displayName}
                      />
                    </div>

                    <div>
                      <label className="text-sm font-medium mb-1 block">Destination</label>
                      <LocationSearch
                        onLocationSelect={setRouteEnd}
                        defaultValue={routeEnd?.displayName}
                      />
                    </div>
                  </div>

                  {routeStart && routeEnd && (
                  <div className="bg-card rounded-xl p-6 border border-border">
                    <h3 className="font-semibold mb-4">Route Statistics</h3>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">Total Distance</span>
                          <span className="text-lg font-bold text-forest-600">{calculateDistance(routeStart, routeEnd)} km</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">Estimated Duration</span>
                        <span className="text-lg font-bold text-sky-600">
                            {Math.floor(parseFloat(calculateDistance(routeStart, routeEnd)) * 3 / 60)}h{" "}
                            {Math.round(parseFloat(calculateDistance(routeStart, routeEnd)) * 3 % 60)}m
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">Air Quality Checkpoints</span>
                          <span className="text-lg font-bold text-forest-600">5</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              <div className="bg-sky-100 dark:bg-sky-950 rounded-xl p-4 border border-sky-200 dark:border-sky-800">
                <div className="flex gap-3">
                  <Info className="h-5 w-5 text-sky-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-sky-900 dark:text-sky-100">
                    {mode === "single"
                      ? "We'll analyze air quality at your selected location and nearby areas"
                      : "We'll analyze air quality at multiple points along your route and warn if conditions worsen"}
                  </p>
                </div>
              </div>

              <div className="flex justify-center gap-3 pt-4">
                <Button 
                  variant="outline" 
                  onClick={onBack} 
                  className="flex-1 max-w-[200px]"
                >
                  Back
                </Button>
                <Button 
                  onClick={handleNext} 
                  disabled={!isValid} 
                  className="flex-1 max-w-[200px] bg-black text-white hover:bg-black/90 disabled:bg-gray-300 disabled:text-gray-500"
                >
                  Next
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}