"use client"

import { motion } from "framer-motion"
import { Satellite, Cloud, CloudSun, Mountain } from "lucide-react"
import { Progress } from "@/components/ui/progress"

interface LoadingItemProps {
  label: string
  sublabel: string
  icon: string
  delay: number
  progress: number
}

const iconMap = {
  satellite: Satellite,
  cloud: Cloud,
  "cloud-sun": CloudSun,
  mountain: Mountain,
}

export function LoadingItem({ label, sublabel, icon, delay, progress }: LoadingItemProps) {
  const Icon = iconMap[icon as keyof typeof iconMap] || Cloud

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay, duration: 0.5 }}
      className="flex items-start gap-4 mb-6"
    >
      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
        <Icon className="w-5 h-5 text-primary" />
      </div>
      <div className="flex-1 space-y-2">
        <div>
          <p className="font-semibold text-foreground">{label}</p>
          <p className="text-sm text-muted-foreground">{sublabel}</p>
        </div>
        <Progress value={progress} className="h-1" />
      </div>
    </motion.div>
  )
}
