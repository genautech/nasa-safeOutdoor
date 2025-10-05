"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { LoadingItem } from "@/components/loading-item"
import { SafetyScore } from "@/components/safety-score"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { AlertCircle } from "lucide-react"
import { getLoadingItems, getMockSafetyAnalysis } from "@/lib/mock-data"
import { analyzeAdventure, type AnalyzeRequest, type AnalyzeResponse } from "@/lib/api"
import type { AdventureContext, SafetyAnalysis } from "@/lib/types"

interface Step2AnalysisProps {
  onNext: () => void
  onBack: () => void
  adventureContext: AdventureContext | null
  onAnalysisComplete: (analysis: SafetyAnalysis) => void
}

export function Step2Analysis({ onNext, onBack, adventureContext, onAnalysisComplete }: Step2AnalysisProps) {
  const [progress, setProgress] = useState<Record<string, number>>({})
  const [showScore, setShowScore] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [analysisData, setAnalysisData] = useState<AnalyzeResponse | null>(null)

  const loadingItems = getLoadingItems(adventureContext?.location || null)

  // Convert backend response to SafetyAnalysis type
  const convertToSafetyAnalysis = (data: AnalyzeResponse): SafetyAnalysis => {
    console.log('🔍 Converting backend data to SafetyAnalysis:', data)
    console.log('🧠 AI Summary from backend:', data.ai_summary)
    console.log('📊 AI Summary length:', data.ai_summary?.length || 0)
    
    return {
      score: Math.round(data.risk_score * 10), // Convert 0-10 to 0-100 scale
      category: data.category,
      ai_summary: data.ai_summary, // ✅ PRESERVE AI SUMMARY
      overallSafety: data.overallSafety,
      weather: {
        condition: data.weather_forecast[0]?.temp_c ? `${Math.round(data.weather_forecast[0].temp_c)}°C` : "Clear",
        temp: data.weather_forecast[0]?.temp_c || 20,
        humidity: data.weather_forecast[0]?.humidity || 50,
        windSpeed: data.weather_forecast[0]?.wind_speed_kmh || 10,
      },
      recommendedTime: {
        date: "Today",
        startTime: "7:00 AM",
        endTime: "11:00 AM",
        reason: data.ai_summary || "Optimal conditions for your activity",
      },
      healthData: {
        uvExposure: data.weather_forecast[0]?.uv_index || 5,
        respiratoryRisk: data.air_quality.aqi > 100 ? "moderate" : "low",
        heatStress: data.weather_forecast[0]?.temp_c > 30 ? "moderate" : "low",
        pollenLevel: "low",
        altitudeEffect: data.elevation?.terrain_type || "none",
        visibilityKm: 10,
      },
      environmentalMetrics: {
        airQuality: {
          aqi: data.air_quality.aqi,
          status: data.air_quality.category,
          pm25: data.air_quality.pm25,
          no2: data.air_quality.no2,
        },
      },
      satelliteData: {
        goes16: {
          cloudCover: data.weather_forecast[0]?.cloud_cover || 20,
          uv_index: data.weather_forecast[0]?.uv_index || 5,
        },
        modis: {
          visibility: "excellent",
        },
        firms: {
          activeFiresNearby: false,
        },
      },
    }
  }

  useEffect(() => {
    let isMounted = true

    const fetchAnalysis = async () => {
      if (!adventureContext?.location) {
        setError("Location data is missing")
        setIsLoading(false)
        return
      }

      try {
        setIsLoading(true)
        setError(null)

        // Get coordinates from location
        let lat: number, lon: number
        if (adventureContext.location.mode === "single" && adventureContext.location.single) {
          lat = adventureContext.location.single.lat
          lon = adventureContext.location.single.lon
        } else if (adventureContext.location.mode === "route" && adventureContext.location.route) {
          // Use first waypoint for route
          lat = adventureContext.location.route.waypoints[0].lat
          lon = adventureContext.location.route.waypoints[0].lon
        } else {
          throw new Error("Invalid location data")
        }

        // Prepare API request
        const request: AnalyzeRequest = {
          activity: adventureContext.activity || "hiking",
          lat,
          lon,
          duration_hours: 4,
          start_time: new Date().toISOString(),
        }

        console.log("Calling backend API with:", request)

        // Call real backend API
        const data = await analyzeAdventure(request)

        if (!isMounted) return

        console.log("Backend response:", data)
        setAnalysisData(data)

        // Convert to SafetyAnalysis format
        const safetyAnalysis = convertToSafetyAnalysis(data)
        
        // Wait a moment to show the loading animation
        setTimeout(() => {
          if (isMounted) {
            setShowScore(true)
            onAnalysisComplete(safetyAnalysis)
            setIsLoading(false)
          }
        }, 2000)

      } catch (err) {
        console.error("Analysis failed:", err)
        
        if (!isMounted) return

        // Fall back to mock data on error
        const mockAnalysis = getMockSafetyAnalysis(
          adventureContext?.activity || "Hiking",
          adventureContext?.location || null
        )
        
        setError(err instanceof Error ? err.message : "Failed to connect to backend. Using sample data.")
        setShowScore(true)
        onAnalysisComplete(mockAnalysis)
        setIsLoading(false)
      }
    }

    // Simulate loading progress for UI
    loadingItems.forEach((item, index) => {
      const startDelay = index * 800
      const interval = setInterval(() => {
        setProgress((prev) => {
          const current = prev[item.id] || 0
          if (current >= 100) {
            clearInterval(interval)
            return prev
          }
          return { ...prev, [item.id]: Math.min(current + 5, 100) }
        })
      }, item.duration / 20)

      setTimeout(() => clearInterval(interval), startDelay + item.duration)
    })

    // Start fetching real data
    fetchAnalysis()

    return () => {
      isMounted = false
    }
  }, [adventureContext])

  const locationText =
    adventureContext?.location?.mode === "single"
      ? adventureContext.location.single?.city
      : `${adventureContext?.location?.route?.waypoints.length || 0} waypoints`

  return (
    <div className="min-h-screen bg-gradient-to-br from-nature-sky via-background to-nature-forest/10 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-2xl"
      >
        <Card className="p-8 md:p-12 backdrop-blur-sm bg-card/95">
          <div className="text-center mb-8">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-2">AI Safety Analysis</h2>
            <p className="text-muted-foreground">
              Watch SafeOutdoor analyze real-time conditions
              {locationText && <span className="block text-sm mt-1">for {locationText}</span>}
            </p>
          </div>

          <div className="mb-12">
            {loadingItems.map((item, index) => (
              <LoadingItem
                key={item.id}
                label={item.label}
                sublabel={item.sublabel}
                icon={item.icon}
                delay={index * 0.8}
                progress={progress[item.id] || 0}
              />
            ))}
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mb-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg"
            >
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-yellow-600 dark:text-yellow-500 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-yellow-900 dark:text-yellow-200">
                    Connection Issue
                  </p>
                  <p className="text-xs text-yellow-700 dark:text-yellow-300 mt-1">
                    {error}
                  </p>
                </div>
              </div>
            </motion.div>
          )}

          {showScore && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="space-y-8"
            >
              <SafetyScore 
                score={analysisData ? analysisData.risk_score : getMockSafetyAnalysis(adventureContext?.activity || "Hiking", adventureContext?.location || null).score} 
                showAnimation 
              />

              {analysisData && (
                <div className="text-center space-y-2">
                  <p className="text-sm font-medium text-muted-foreground">
                    Air Quality: AQI {analysisData.air_quality.aqi} ({analysisData.air_quality.category})
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {analysisData.data_sources.join(" • ")}
                  </p>
                </div>
              )}

              <p className="text-center text-sm text-muted-foreground">Tap Next to see detailed analysis</p>

              <div className="flex gap-4 justify-center">
                <Button variant="outline" onClick={onBack} size="lg">
                  Back
                </Button>
                <Button onClick={onNext} size="lg" className="min-w-[200px] bg-primary hover:bg-primary/90">
                  Next
                </Button>
              </div>
            </motion.div>
          )}
        </Card>
      </motion.div>
    </div>
  )
}