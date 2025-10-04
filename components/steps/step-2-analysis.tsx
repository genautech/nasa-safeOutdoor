"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { LoadingItem } from "@/components/loading-item"
import { SafetyScore } from "@/components/safety-score"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { getLoadingItems, getMockSafetyAnalysis } from "@/lib/mock-data"
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

  const loadingItems = getLoadingItems(adventureContext?.location || null)
  const safetyAnalysis = getMockSafetyAnalysis(
    adventureContext?.activity || "Hiking",
    adventureContext?.location || null,
  )

  useEffect(() => {
    // Simulate loading progress for each item
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

    // Show score after all items are loaded
    setTimeout(() => {
      setShowScore(true)
      onAnalysisComplete(safetyAnalysis)
    }, 6500)
  }, [])

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

          {showScore && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="space-y-8"
            >
              <SafetyScore score={safetyAnalysis.score} showAnimation />

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
