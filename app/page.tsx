"use client"

import { useState } from "react"
import { Step1Activity } from "@/components/steps/step-1-activity"
import { Step1_5Location } from "@/components/steps/step-1-5-location"
import { Step2Analysis } from "@/components/steps/step-2-analysis"
import { Step3Timing } from "@/components/steps/step-3-timing"
import { Step4Ready } from "@/components/steps/step-4-ready"
import type { LocationData, AdventureContext, SafetyAnalysis } from "@/lib/types"

export default function Home() {
  const [currentStep, setCurrentStep] = useState(0)
  const [selectedActivity, setSelectedActivity] = useState<string | null>(null)
  const [locationData, setLocationData] = useState<LocationData | null>(null)
  const [adventureContext, setAdventureContext] = useState<AdventureContext | null>(null)
  const [safetyAnalysis, setSafetyAnalysis] = useState<SafetyAnalysis | null>(null)

  const handleNext = () => {
    setCurrentStep((prev) => Math.min(prev + 1, 4))
  }

  const handleBack = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 0))
  }

  const handleRestart = () => {
    setCurrentStep(0)
    setSelectedActivity(null)
    setLocationData(null)
    setAdventureContext(null)
    setSafetyAnalysis(null)
  }

  const handleLocationSelect = (location: LocationData) => {
    setLocationData(location)
    if (selectedActivity) {
      setAdventureContext({
        activity: selectedActivity,
        location,
        timestamp: Date.now(),
      })
    }
  }

  const handleAnalysisComplete = (analysis: SafetyAnalysis) => {
    setSafetyAnalysis(analysis)
    if (adventureContext) {
      setAdventureContext({
        ...adventureContext,
        safetyAnalysis: analysis,
      })
    }
  }

  return (
    <main className="min-h-screen">
      {currentStep < 4 && (
        <div className="fixed top-8 left-1/2 -translate-x-1/2 z-50">
          <div className="bg-card/80 backdrop-blur-sm rounded-full px-6 py-3 shadow-lg">
            <p className="text-sm font-medium text-foreground">Step {currentStep + 1} of 5</p>
          </div>
        </div>
      )}

      {currentStep === 0 && (
        <Step1Activity selectedActivity={selectedActivity} onSelectActivity={setSelectedActivity} onNext={handleNext} />
      )}

      {currentStep === 1 && (
        <Step1_5Location onNext={handleNext} onBack={handleBack} onLocationSelect={handleLocationSelect} />
      )}

      {currentStep === 2 && (
        <Step2Analysis
          onNext={handleNext}
          onBack={handleBack}
          adventureContext={adventureContext}
          onAnalysisComplete={handleAnalysisComplete}
        />
      )}

      {currentStep === 3 && (
        <Step3Timing
          onNext={handleNext}
          onBack={handleBack}
          adventureContext={adventureContext}
          safetyAnalysis={safetyAnalysis}
        />
      )}

      {currentStep === 4 && (
        <Step4Ready adventureContext={adventureContext} safetyAnalysis={safetyAnalysis} onRestart={handleRestart} />
      )}
    </main>
  )
}
