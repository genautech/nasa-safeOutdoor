"use client"

import { motion, useMotionValue, useTransform, animate } from "framer-motion"
import { useEffect } from "react"
import { CheckCircle2, Sparkles } from "lucide-react"

interface SafetyScoreProps {
  score: number
  showAnimation?: boolean
}

export function SafetyScore({ score, showAnimation = false }: SafetyScoreProps) {
  const count = useMotionValue(0)
  const rounded = useTransform(count, (latest) => {
    // Round to 1 decimal place and return as string
    return (Math.round(latest * 10) / 10).toFixed(1)
  })

  useEffect(() => {
    if (showAnimation) {
      const controls = animate(count, score, { duration: 1, delay: 3.5 })
      return controls.stop
    } else {
      count.set(score)
    }
  }, [count, score, showAnimation])

  const getScoreColor = (score: number) => {
    if (score >= 8.5) return "text-success" // Green for Excellent
    if (score >= 7.0) return "text-emerald-600" // Green for Good
    if (score >= 5.5) return "text-yellow-600" // Yellow for Fair
    if (score >= 4.0) return "text-orange-600" // Orange for Caution
    return "text-destructive" // Red for Poor
  }

  const getScoreLabel = (score: number) => {
    if (score >= 8.5) return "Excellent"
    if (score >= 7.0) return "Good"
    if (score >= 5.5) return "Fair"
    if (score >= 4.0) return "Caution"
    return "Poor"
  }

  const getScoreIcon = (score: number) => {
    if (score >= 7.0) return { icon: CheckCircle2, color: "text-success" }
    if (score >= 5.5) return { icon: CheckCircle2, color: "text-yellow-600" }
    if (score >= 4.0) return { icon: CheckCircle2, color: "text-orange-600" }
    return null // No icon for poor conditions
  }

  return (
    <motion.div
      initial={showAnimation ? { opacity: 0, scale: 0.8 } : false}
      animate={showAnimation ? { opacity: 1, scale: 1 } : false}
      transition={{ delay: 3.5, duration: 0.5 }}
      className="relative"
    >
      <div className="text-center space-y-4">
        <h3 className="text-2xl font-bold text-foreground">Safety Score</h3>
        <div className="relative inline-block">
          <motion.div className={cn("text-6xl font-bold", getScoreColor(score))}>
            <motion.span>{rounded}</motion.span>
            <span className="text-3xl text-muted-foreground">/10</span>
          </motion.div>
          {showAnimation && getScoreIcon(score) && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 4.5, duration: 0.3 }}
              className="absolute -right-8 -top-2"
            >
              {(() => {
                const iconData = getScoreIcon(score);
                if (!iconData) return null;
                const Icon = iconData.icon;
                return <Icon className={cn("w-8 h-8", iconData.color)} />;
              })()}
            </motion.div>
          )}
        </div>
        <motion.p
          initial={showAnimation ? { opacity: 0 } : false}
          animate={showAnimation ? { opacity: 1 } : false}
          transition={{ delay: 4.7, duration: 0.3 }}
          className={cn("text-lg font-semibold", getScoreColor(score))}
        >
          {getScoreLabel(score)} conditions!
        </motion.p>
      </div>

      {showAnimation && score >= 7.0 && (
        <>
          {[...Array(12)].map((_, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, scale: 0 }}
              animate={{
                opacity: [0, 1, 0],
                scale: [0, 1, 0],
                x: Math.cos((i * Math.PI * 2) / 12) * 100,
                y: Math.sin((i * Math.PI * 2) / 12) * 100,
              }}
              transition={{ delay: 4.5, duration: 1 }}
              className="absolute top-1/2 left-1/2"
            >
              <Sparkles className={cn("w-4 h-4", getScoreColor(score))} />
            </motion.div>
          ))}
        </>
      )}
    </motion.div>
  )
}

function cn(...classes: (string | boolean | undefined)[]) {
  return classes.filter(Boolean).join(" ")
}
