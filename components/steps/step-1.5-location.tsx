"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { MapPin, Route, Search, Navigation, Plus, Info, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { MapPreview } from "@/components/map-preview"
import { WaypointItem } from "@/components/waypoint-item"
import type { LocationData } from "@/lib/types"
import { mockLocationData, mockRouteData } from "@/lib/mock-data"

interface Step1_5LocationProps {
  onNext: () => void
  onBack: () => void
  onLocationSelect: (data: LocationData) => void
}

export function Step1_5Location({ onNext, onBack, onLocationSelect }: Step1_5LocationProps) {
  const [mode, setMode] = useState<"single" | "route">("single")
  const [locationData, setLocationData] = useState<LocationData>(mockLocationData)
  const [searchQuery, setSearchQuery] = useState("")

  const handleModeChange = (newMode: "single" | "route") => {
    setMode(newMode)
    if (newMode === "single") {
      setLocationData(mockLocationData)
    } else {
      setLocationData(mockRouteData)
    }
  }

  const handleNext = () => {
    onLocationSelect(locationData)
    onNext()
  }

  const handleRemoveWaypoint = (id: string) => {
    if (locationData.mode === "route" && locationData.route) {
      const updatedWaypoints = locationData.route.waypoints.filter((w) => w.id !== id)
      setLocationData({
        ...locationData,
        route: {
          ...locationData.route,
          waypoints: updatedWaypoints,
        },
      })
    }
  }

  const isValid = mode === "single" ? !!locationData.single : (locationData.route?.waypoints.length ?? 0) >= 2

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
                    ? "bg-green-500 text-white shadow-md"
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
                    ? "bg-green-500 text-white shadow-md"
                    : "bg-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                }`}
              >
                <Route className="h-4 w-4" />
                Route
              </button>
            </div>

            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              <Input
                placeholder={mode === "single" ? "Search city or address..." : "Add waypoint..."}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-12 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <Button
                size="icon"
                variant="ghost"
                className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8"
                title="Use current location"
              >
                <Navigation className="h-4 w-4" />
              </Button>
            </div>

            {mode === "single" && locationData.single && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
                className="space-y-4"
              >
                <MapPreview mode="single" location={locationData.single} className="h-[200px]" />

                <div className="bg-card rounded-xl p-4 border border-border space-y-2 hover:border-green-500/50 transition-colors duration-200 cursor-pointer">
                  <h3 className="font-semibold">{locationData.single.city}</h3>
                  <p className="text-sm text-muted-foreground">{locationData.single.address}</p>
                  <p className="text-xs text-muted-foreground">
                    {locationData.single.lat.toFixed(4)}, {locationData.single.lon.toFixed(4)}
                  </p>
                </div>
              </motion.div>
            )}

            {mode === "route" && locationData.route && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
                className="space-y-4"
              >
                <MapPreview mode="route" waypoints={locationData.route.waypoints} className="h-[200px]" />

                <div className="space-y-2">
                  {locationData.route.waypoints
                    .sort((a, b) => a.order - b.order)
                    .map((waypoint, index) => (
                      <WaypointItem
                        key={waypoint.id}
                        waypoint={waypoint}
                        isFirst={index === 0}
                        isLast={index === locationData.route!.waypoints.length - 1}
                        onRemove={() => handleRemoveWaypoint(waypoint.id)}
                      />
                    ))}
                </div>

                <Button variant="outline" className="w-full bg-transparent" disabled>
                  <Plus className="h-4 w-4 mr-2" />
                  Add waypoint
                </Button>

                <div className="bg-card rounded-xl p-4 border border-border">
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-2xl font-bold text-forest-600">{locationData.route.totalDistance}</p>
                      <p className="text-xs text-muted-foreground">km</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-sky-600">
                        {Math.floor(locationData.route.estimatedDuration / 60)}h{" "}
                        {locationData.route.estimatedDuration % 60}m
                      </p>
                      <p className="text-xs text-muted-foreground">duration</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-forest-600">{locationData.route.waypoints.length + 3}</p>
                      <p className="text-xs text-muted-foreground">checkpoints</p>
                    </div>
                  </div>
                </div>
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

            <div className="flex gap-3 pt-4">
              <Button variant="outline" onClick={onBack} className="flex-1 bg-transparent">
                Back
              </Button>
              <Button 
                onClick={handleNext} 
                disabled={!isValid} 
                className={`flex-1 gap-2 font-bold transition-all duration-200 ${
                  !isValid 
                    ? "bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed hover:bg-gray-300 dark:hover:bg-gray-700" 
                    : "bg-green-500 hover:bg-green-600 text-white shadow-md hover:shadow-lg"
                }`}
              >
                Next
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </motion.div>
        </div>
      </div>

      <div className="hidden lg:block h-screen">
        <div className="grid grid-cols-[60%_40%] h-full">
          <div className="relative">
            <MapPreview
              mode={mode}
              location={mode === "single" ? locationData.single : undefined}
              waypoints={mode === "route" ? locationData.route?.waypoints : undefined}
              className="h-full rounded-none"
            />
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
                      ? "bg-green-500 text-white shadow-md"
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
                      ? "bg-green-500 text-white shadow-md"
                      : "bg-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                  }`}
                >
                  <Route className="h-4 w-4" />
                  Route
                </button>
              </div>

              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <Input
                  placeholder={mode === "single" ? "Search city or address..." : "Add waypoint..."}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-12 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <Button
                  size="icon"
                  variant="ghost"
                  className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8"
                  title="Use current location"
                >
                  <Navigation className="h-4 w-4" />
                </Button>
              </div>

              {mode === "single" && locationData.single && (
                <div className="bg-card rounded-xl p-4 border border-border space-y-2 hover:border-green-500/50 transition-colors duration-200 cursor-pointer">
                  <h3 className="font-semibold text-lg">{locationData.single.city}</h3>
                  <p className="text-sm text-muted-foreground">{locationData.single.address}</p>
                  <p className="text-xs text-muted-foreground">
                    {locationData.single.lat.toFixed(4)}, {locationData.single.lon.toFixed(4)}
                  </p>
                </div>
              )}

              {mode === "route" && locationData.route && (
                <div className="space-y-4">
                  <div className="space-y-2">
                    {locationData.route.waypoints
                      .sort((a, b) => a.order - b.order)
                      .map((waypoint, index) => (
                        <WaypointItem
                          key={waypoint.id}
                          waypoint={waypoint}
                          isFirst={index === 0}
                          isLast={index === locationData.route!.waypoints.length - 1}
                          onRemove={() => handleRemoveWaypoint(waypoint.id)}
                        />
                      ))}
                  </div>

                  <Button variant="outline" className="w-full bg-transparent" disabled>
                    <Plus className="h-4 w-4 mr-2" />
                    Add waypoint
                  </Button>

                  <div className="bg-card rounded-xl p-6 border border-border">
                    <h3 className="font-semibold mb-4">Route Statistics</h3>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">Total Distance</span>
                        <span className="text-lg font-bold text-forest-600">{locationData.route.totalDistance} km</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">Estimated Duration</span>
                        <span className="text-lg font-bold text-sky-600">
                          {Math.floor(locationData.route.estimatedDuration / 60)}h{" "}
                          {locationData.route.estimatedDuration % 60}m
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">Air Quality Checkpoints</span>
                        <span className="text-lg font-bold text-forest-600">
                          {locationData.route.waypoints.length + 3}
                        </span>
                      </div>
                    </div>
                  </div>
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

              <div className="flex gap-3 pt-4">
                <Button variant="outline" onClick={onBack} className="w-full bg-transparent lg:w-auto lg:px-8">
                  Back
                </Button>
                <Button 
                  onClick={handleNext} 
                  disabled={!isValid} 
                  className={`gap-2 font-bold transition-all duration-200 w-full lg:w-52 ${
                    !isValid 
                      ? "bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed hover:bg-gray-300 dark:hover:bg-gray-700" 
                      : "bg-green-500 hover:bg-green-600 text-white shadow-md hover:shadow-lg"
                  }`}
                >
                  Next
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
