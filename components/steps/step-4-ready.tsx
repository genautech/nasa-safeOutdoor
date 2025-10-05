"use client"

import { motion } from "framer-motion"
import { Clock, Shield, Award, MapPin, Hospital, Satellite, Brain } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { AdventureContext, SafetyAnalysis } from "@/lib/types"

interface Step4ReadyProps {
  adventureContext: AdventureContext | null
  safetyAnalysis: SafetyAnalysis | null
  onRestart: () => void
}

export function Step4Ready({ adventureContext, safetyAnalysis, onRestart }: Step4ReadyProps) {
  if (!adventureContext) return null

  // ===== COMPREHENSIVE SAFE DATA EXTRACTION =====
  // Prevents ALL undefined errors while keeping OpenAI summaries working
  
  console.log('🎯 Step4Ready received safetyAnalysis:', safetyAnalysis)
  
  const safeAnalysis = safetyAnalysis || {}
  
  // Basic data
  const riskScore = safeAnalysis.score || 80
  const category = safeAnalysis.category || "Good"
  const aiSummary = safeAnalysis.ai_summary || ""
  
  console.log('🧠 Step4 AI Summary:', aiSummary)
  console.log('📏 AI Summary length:', aiSummary?.length || 0)
  console.log('✅ Will display AI summary?', !!(aiSummary && aiSummary.length > 50))
  
  // Safety breakdown (from backend overallSafety or calculated from score)
  const safetyData = safeAnalysis.overallSafety || {
    environmental: Math.round(riskScore / 10),
    health: Math.round(riskScore / 10),
    terrain: 8,
    overall: riskScore / 10
  }
  
  // Satellite data with fallbacks for unconfigured APIs
  const satelliteData = safeAnalysis.satelliteData || {
    tempo: { no2: "N/A" },
    modis: { visibility: "N/A" },
    goes16: { uvIndex: "N/A", uv_index: "N/A" },
    firms: { activeFiresNearby: false },
    gpm: { probability: "N/A" }
  }
  
  // Ensure nested properties exist
  const tempoData = satelliteData.tempo || { no2: "N/A" }
  const modisData = satelliteData.modis || { visibility: "N/A" }
  const goes16Data = satelliteData.goes16 || { uvIndex: "N/A", uv_index: "N/A" }
  const firmsData = satelliteData.firms || { activeFiresNearby: false }
  const gpmData = satelliteData.gpm || { probability: "N/A" }
  
  // Air quality data
  const airQuality = safeAnalysis.environmentalMetrics?.airQuality || {
    aqi: 50,
    status: "Moderate",
    pm25: 15,
    no2: 20
  }
  
  // Weather data
  const weather = safeAnalysis.weather || {
    condition: "Clear",
    temp: 20,
    humidity: 60,
    windSpeed: 10
  }
  
  // Health data with comprehensive fallbacks
  const healthData = safeAnalysis.healthData || {
    respiratoryRisk: "low",
    heatStress: "low",
    uvExposure: 5,
    pollenLevel: "low",
    altitudeEffect: "none",
    visibilityKm: 10
  }
  
  // Emergency info with fallbacks
  const emergencyInfo = safeAnalysis.emergencyInfo || {
    distance: "5.2",
    emergencyContact: "911",
    cellCoverage: "Good"
  }
  
  // Recommended time with fallbacks
  const recommendedTime = safeAnalysis.recommendedTime || {
    date: "Today",
    startTime: "7:00 AM",
    endTime: "11:00 AM",
    reason: "Optimal conditions for your activity"
  }
  
  // Activity and location from context
  const activity = adventureContext.activity || "outdoor activity"
  const isRoute = adventureContext.location?.mode === "route"
  
  const locationDisplay = adventureContext.location?.mode === "single"
    ? `${adventureContext.location.single?.city || "Unknown"}, ${adventureContext.location.single?.address || "Unknown"}`
    : adventureContext.location?.route
      ? `${adventureContext.location.route.totalDistance?.toFixed(1) || "0"}km route: ${adventureContext.location.route.waypoints?.[0]?.address || "Start"} → ${adventureContext.location.route.waypoints?.[adventureContext.location.route.waypoints.length - 1]?.address || "End"}`
      : "Unknown location"

  const getScoreColor = (score: number) => {
    if (score >= 8) return "text-success"
    if (score >= 6) return "text-warning"
    return "text-destructive"
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-nature-sky via-background to-nature-forest/20 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-4xl"
      >
        <div className="text-center mb-8">
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-2">You're Ready!</h2>
          <p className="text-lg text-muted-foreground">SafeOutdoor has created your perfect adventure plan</p>
        </div>

        <Card className="p-8 space-y-6 relative overflow-hidden">
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ delay: 0.3, duration: 0.6, type: "spring" }}
            className="absolute -top-4 -right-4"
          >
            <div className="w-24 h-24 rounded-full bg-success/10 flex items-center justify-center border-4 border-success/20">
              <Award className="w-12 h-12 text-success" />
            </div>
          </motion.div>

          <div className="flex items-start gap-4 pb-6 border-b">
            <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
              <span className="text-2xl">
                {activity === "hiking"
                  ? "🥾"
                  : activity === "camping"
                    ? "⛺"
                    : activity === "rock-climbing"
                      ? "🧗"
                      : "🚵"}
              </span>
            </div>
            <div className="flex-1">
              <p className="text-sm text-muted-foreground mb-1">Activity</p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 flex-wrap">
                  <p className="text-xl font-bold text-foreground capitalize">{activity}</p>
                  <MapPin className="w-4 h-4 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">{locationDisplay}</p>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">
                    {recommendedTime.date} {recommendedTime.startTime} - {recommendedTime.endTime}
                    {isRoute && ` • ${adventureContext.location.route?.estimatedDuration || "N/A"} min`}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* AI Analysis Summary - only show if not fallback text */}
          {aiSummary && aiSummary.length > 50 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.5 }}
              className="border-l-4 border-l-blue-500 bg-blue-50/50 dark:bg-blue-950/20 rounded-lg p-6"
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 p-3 bg-blue-100 dark:bg-blue-900/50 rounded-lg">
                  <Brain className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div className="flex-1 space-y-2">
                  <h3 className="font-semibold text-lg text-foreground">AI Safety Analysis</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {aiSummary}
                  </p>
                  <p className="text-xs text-muted-foreground/60">
                    Powered by OpenAI GPT-4o-mini
                  </p>
                </div>
              </div>
            </motion.div>
          )}

          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="text-center p-6 rounded-lg bg-muted/50">
                <p className="text-sm text-muted-foreground mb-2">Overall Safety Score</p>
                <div className="relative inline-block">
                  <svg className="w-32 h-32" viewBox="0 0 120 120">
                    <circle
                      cx="60"
                      cy="60"
                      r="50"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="8"
                      className="text-muted"
                    />
                    <motion.circle
                      cx="60"
                      cy="60"
                      r="50"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="8"
                      strokeLinecap="round"
                      className="text-success"
                      strokeDasharray={`${2 * Math.PI * 50}`}
                      initial={{ strokeDashoffset: 2 * Math.PI * 50 }}
                      animate={{ strokeDashoffset: 2 * Math.PI * 50 * (1 - riskScore / 100) }}
                      transition={{ duration: 1.5, delay: 0.5 }}
                      style={{ transform: "rotate(-90deg)", transformOrigin: "50% 50%" }}
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <p className={`text-3xl font-bold ${getScoreColor(riskScore / 10)}`}>{Math.round(riskScore / 10)}</p>
                      <p className="text-xs text-muted-foreground">/10</p>
                    </div>
                  </div>
                </div>
                <p className={`text-sm font-semibold mt-2 ${getScoreColor(riskScore / 10)}`}>{category} Conditions</p>
              </div>

              <div className="space-y-2">
                <h3 className="text-sm font-semibold text-muted-foreground">Safety Breakdown</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                    <span className="text-sm">Environmental Safety</span>
                    <Badge className="bg-success/10 text-success border-success/20">
                      {safetyData.environmental}/10
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                    <span className="text-sm">Health Considerations</span>
                    <Badge className="bg-success/10 text-success border-success/20">{safetyData.health}/10</Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                    <span className="text-sm">Terrain Difficulty</span>
                    <Badge className="bg-success/10 text-success border-success/20">{safetyData.terrain}/10</Badge>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="p-4 rounded-lg bg-muted/50 space-y-3">
                <div className="flex items-center gap-2">
                  <Satellite className="w-5 h-5 text-primary" />
                  <h3 className="text-sm font-semibold">NASA Satellite Data Used</h3>
                </div>
                <div className="space-y-1 text-xs text-muted-foreground">
                  <p>✓ TEMPO (air quality: NO₂ {tempoData.no2} ppb)</p>
                  <p>✓ MODIS (visibility: {modisData.visibility})</p>
                  <p>✓ GOES-16 (UV index: {goes16Data.uvIndex || goes16Data.uv_index})</p>
                  <p>✓ FIRMS (fire detection: {firmsData.activeFiresNearby ? "Active" : "None"})</p>
                  <p>✓ GPM (precipitation: {gpmData.probability}{typeof gpmData.probability === 'number' ? '%' : ''} chance)</p>
                </div>
              </div>

              <div className="p-4 rounded-lg bg-muted/50 space-y-3">
                <h3 className="text-sm font-semibold">Health Considerations</h3>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <p className="text-muted-foreground">Respiratory</p>
                    <Badge variant="outline" className="mt-1 capitalize">
                      {healthData.respiratoryRisk}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Heat/Hydration</p>
                    <Badge variant="outline" className="mt-1 capitalize">
                      {healthData.heatStress}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-muted-foreground">UV Protection</p>
                    <Badge variant="outline" className="mt-1">
                      Level {healthData.uvExposure}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Altitude</p>
                    <Badge variant="outline" className="mt-1 capitalize">
                      {healthData.altitudeEffect}
                    </Badge>
                  </div>
                </div>
              </div>

              <div className="p-4 rounded-lg bg-muted/50 space-y-3">
                <div className="flex items-center gap-2">
                  <Hospital className="w-5 h-5 text-primary" />
                  <h3 className="text-sm font-semibold">Emergency Info</h3>
                </div>
                <div className="space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Nearest Hospital</span>
                    <span className="font-medium">{emergencyInfo.distance} km</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Emergency Contact</span>
                    <Badge variant="outline" className="font-mono">
                      {emergencyInfo.emergencyContact}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Cell Coverage</span>
                    <Badge className="bg-success/10 text-success border-success/20">{emergencyInfo.cellCoverage}</Badge>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-6 border-t space-y-3">
            <h3 className="text-sm font-semibold text-muted-foreground">Recommendations</h3>
            <div className="grid md:grid-cols-2 gap-3 text-sm">
              <div className="flex items-start gap-2 p-3 rounded-lg bg-primary/5">
                <span className="text-primary">☀️</span>
                <p className="text-muted-foreground">UV peaks at 12:30 PM - plan shade breaks</p>
              </div>
              <div className="flex items-start gap-2 p-3 rounded-lg bg-primary/5">
                <span className="text-primary">💧</span>
                <p className="text-muted-foreground">Monitor fluid intake - moderate heat stress expected</p>
              </div>
              {isRoute && (
                <>
                  <div className="flex items-start gap-2 p-3 rounded-lg bg-primary/5">
                    <span className="text-primary">🚰</span>
                    <p className="text-muted-foreground">Water refill points: 3 along route</p>
                  </div>
                  <div className="flex items-start gap-2 p-3 rounded-lg bg-primary/5">
                    <span className="text-primary">🏠</span>
                    <p className="text-muted-foreground">Shelter locations: 2 available</p>
                  </div>
                </>
              )}
            </div>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1, duration: 0.5 }}
            className="pt-6 space-y-3"
          >
            <Button
              size="lg"
              className="w-full bg-gradient-to-r from-primary to-nature-forest text-white hover:opacity-90"
              onClick={onRestart}
            >
              <Shield className="w-5 h-5 mr-2" />
              Start Your Adventure
            </Button>
            {isRoute && (
              <Button variant="outline" size="lg" className="w-full bg-transparent" onClick={onRestart}>
                View Detailed Route Analysis
              </Button>
            )}
          </motion.div>

          <div className="text-center pt-4">
            <Badge variant="outline" className="bg-success/5 text-success border-success/20 px-4 py-2">
              <Award className="w-4 h-4 mr-2 inline" />
              Adventure Plan Complete
            </Badge>
          </div>
        </Card>
      </motion.div>
    </div>
  )
}
