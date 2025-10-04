"use client"

import { GripVertical, X } from "lucide-react"
import { Button } from "@/components/ui/button"

interface WaypointItemProps {
  waypoint: {
    id: string
    address: string
    order: number
  }
  isFirst: boolean
  isLast: boolean
  onRemove: () => void
}

export function WaypointItem({ waypoint, isFirst, isLast, onRemove }: WaypointItemProps) {
  const getLabel = () => {
    if (isFirst) return "Start"
    if (isLast) return "End"
    return "Via"
  }

  return (
    <div className="flex items-center gap-3 p-3 bg-card rounded-lg border border-border group hover:border-forest-500/50 transition-colors">
      <GripVertical className="h-5 w-5 text-muted-foreground cursor-grab active:cursor-grabbing" />

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-forest-600 dark:text-forest-400">{getLabel()}:</span>
          <span className="text-sm font-medium truncate">{waypoint.address}</span>
        </div>
      </div>

      <Button
        size="icon"
        variant="ghost"
        className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
        onClick={onRemove}
      >
        <X className="h-4 w-4" />
      </Button>
    </div>
  )
}
