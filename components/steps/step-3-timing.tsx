"use client"

import { motion } from "framer-motion"
import { Clock, MapPin, AlertTriangle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { MetricBadge } from "@/components/metric-badge"
import type { AdventureContext, SafetyAnalysis } from "@/lib/types"

interface Step3TimingProps {
  onNext: () => void
  onBack: () => void
  adventureContext: AdventureContext | null
  safetyAnalysis: SafetyAnalysis | null
}

export function Step3Timing({ onNext, onBack, adventureContext, safetyAnalysis }: Step3TimingProps) {
  if (!safetyAnalysis) return null

  const { weather, recommendedTime, healthData, environmentalMetrics, satelliteData } = safetyAnalysis

  const locationDisplay =
    adventureContext?.location?.mode === "single"
      ? adventureContext.location.single?.city
      : `Route (${adventureContext?.location?.route?.totalDistance.toFixed(1)} km)`

  const isRoute = adventureContext?.location?.mode === "route"

  return (
    <div className="min-h-screen bg-gradient-to-b from-nature-sky via-nature-mint to-nature-forest flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-4xl"
      >
        <div className="text-center mb-8">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-2">Smart Timing</h2>
          <p className="text-white/90">
            Best time for {adventureContext?.activity} in {locationDisplay}
          </p>
        </div>

        <Card className="p-8 space-y-6">
          <div className="flex items-center gap-4 pb-6 border-b">
            <div className="flex-shrink-0 w-16 h-16 rounded-lg bg-muted overflow-hidden">
              <div className="w-full h-full bg-gradient-to-br from-nature-forest to-nature-mint flex items-center justify-center">
                <MapPin className="w-8 h-8 text-white" />
              </div>
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <Clock className="w-4 h-4 text-primary" />
                <p className="text-sm text-muted-foreground">Best Time</p>
              </div>
              <p className="text-xl font-bold text-foreground">
                {recommendedTime.date} {recommendedTime.startTime} - {recommendedTime.endTime}
              </p>
              {isRoute && (
                <p className="text-sm text-muted-foreground mt-1">Conditions vary along route - see details below</p>
              )}
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="font-semibold text-sm text-muted-foreground">Environmental Conditions</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <MetricBadge
                  label="Air Quality"
                  value={`AQI ${environmentalMetrics.airQuality.aqi} (${environmentalMetrics.airQuality.status})`}
                  status="excellent"
                  icon="wind"
                />
                <div className="text-xs text-muted-foreground pl-4">
                  PM2.5: {environmentalMetrics.airQuality.pm25} µg/m³ • NO₂: {environmentalMetrics.airQuality.no2} ppb
                </div>

                <MetricBadge label="UV Index" value={`${healthData.uvExposure} (High)`} status="moderate" icon="sun" />
                <div className="text-xs text-muted-foreground pl-4">Sun protection recommended</div>

                <MetricBadge
                  label="Cloud Cover"
                  value={`${satelliteData.goes16.cloudCover}% (mostly clear)`}
                  status="excellent"
                  icon="cloud"
                />
              </div>

              <div className="space-y-3">
                <MetricBadge
                  label="Wildfire Risk"
                  value={satelliteData.firms.activeFiresNearby ? "Detected" : "None detected"}
                  status={satelliteData.firms.activeFiresNearby ? "warning" : "excellent"}
                  icon="flame"
                />

                <MetricBadge
                  label="Visibility"
                  value={`${healthData.visibilityKm}km (${satelliteData.modis.visibility})`}
                  status="excellent"
                  icon="eye"
                />

                <MetricBadge
                  label="Weather"
                  value={`${weather.condition}, ${weather.temp}°F`}
                  status="excellent"
                  icon="thermometer"
                />
              </div>
            </div>
          </div>

          <div className="space-y-4 pt-4 border-t">
            <h3 className="font-semibold text-sm text-muted-foreground">Health Considerations</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 rounded-lg bg-muted/50">
                <p className="text-xs text-muted-foreground mb-1">Respiratory Risk</p>
                <Badge className="bg-success/10 text-success border-success/20 capitalize">
                  {healthData.respiratoryRisk}
                </Badge>
              </div>
              <div className="text-center p-3 rounded-lg bg-muted/50">
                <p className="text-xs text-muted-foreground mb-1">Heat Stress</p>
                <Badge className="bg-warning/10 text-warning border-warning/20 capitalize">
                  {healthData.heatStress}
                </Badge>
              </div>
              <div className="text-center p-3 rounded-lg bg-muted/50">
                <p className="text-xs text-muted-foreground mb-1">Pollen Level</p>
                <Badge className="bg-success/10 text-success border-success/20 capitalize">
                  {healthData.pollenLevel}
                </Badge>
              </div>
              <div className="text-center p-3 rounded-lg bg-muted/50">
                <p className="text-xs text-muted-foreground mb-1">Altitude Effect</p>
                <Badge className="bg-muted/10 text-foreground border-muted/20 capitalize">
                  {healthData.altitudeEffect}
                </Badge>
              </div>
            </div>
          </div>

          {isRoute && safetyAnalysis.routeSegments && (
            <div className="space-y-4 pt-4 border-t">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-warning" />
                <h3 className="font-semibold text-sm text-muted-foreground">Route Conditions</h3>
              </div>
              <div className="space-y-2">
                {safetyAnalysis.routeSegments.map((segment) => (
                  <div key={segment.segmentId} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                    <div className="flex-1">
                      <p className="text-sm font-medium">{segment.name}</p>
                      <p className="text-xs text-muted-foreground">{segment.time}</p>
                      {segment.warnings.length > 0 && (
                        <p className="text-xs text-warning mt-1">{segment.warnings[0]}</p>
                      )}
                    </div>
                    <div className="flex gap-3 text-xs">
                      <Badge variant="outline" className={segment.aqi > 60 ? "border-warning text-warning" : ""}>
                        AQI {segment.aqi}
                      </Badge>
                      <Badge variant="outline" className={segment.uvIndex > 7 ? "border-warning text-warning" : ""}>
                        UV {segment.uvIndex}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex gap-4 pt-4">
            <Button variant="outline" onClick={onBack} size="lg" className="flex-1 bg-transparent">
              Back
            </Button>
            <Button onClick={onNext} size="lg" className="flex-1 bg-primary hover:bg-primary/90">
              Next
            </Button>
          </div>
        </Card>
      </motion.div>
    </div>
  )
}
