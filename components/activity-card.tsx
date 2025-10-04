"use client"

import { motion } from "framer-motion"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface ActivityCardProps {
  name: string
  icon: string
  selected?: boolean
  onClick?: () => void
}

export function ActivityCard({ name, icon, selected, onClick }: ActivityCardProps) {
  return (
    <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.98 }} transition={{ duration: 0.2 }}>
      <Card
        className={cn(
          "flex flex-col items-center justify-center gap-3 p-6 cursor-pointer transition-all duration-300 hover:shadow-lg",
          selected ? "bg-primary text-primary-foreground ring-2 ring-primary" : "bg-card hover:bg-accent",
        )}
        onClick={onClick}
      >
        <span className="text-4xl" role="img" aria-label={name}>
          {icon}
        </span>
        <span className="text-sm font-medium text-center">{name}</span>
      </Card>
    </motion.div>
  )
}
