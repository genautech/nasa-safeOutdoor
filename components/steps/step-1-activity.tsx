"use client"

import { motion } from "framer-motion"
import { ActivityCard } from "@/components/activity-card"
import { Button } from "@/components/ui/button"
import { activities } from "@/lib/mock-data"

interface Step1ActivityProps {
  selectedActivity: string | null
  onSelectActivity: (id: string) => void
  onNext: () => void
}

export function Step1Activity({ selectedActivity, onSelectActivity, onNext }: Step1ActivityProps) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-nature-sky via-nature-forest/20 to-background">
      <div className="container mx-auto px-4 py-12 md:py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground mb-4 text-balance">
            Choose Your Adventure
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
            AI will analyze safety conditions for your activity
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="max-w-4xl mx-auto"
        >
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-8">
            {activities.map((activity, index) => (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index, duration: 0.4 }}
              >
                <ActivityCard
                  name={activity.name}
                  icon={activity.icon}
                  selected={selectedActivity === activity.id}
                  onClick={() => onSelectActivity(activity.id)}
                />
              </motion.div>
            ))}
          </div>

          <div className="flex justify-center gap-4">
            <Button
              size="lg"
              onClick={onNext}
              disabled={!selectedActivity}
              className="min-w-[200px] bg-primary hover:bg-primary/90"
            >
              Next
            </Button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
