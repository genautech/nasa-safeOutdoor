import { CheckCircle2, AlertCircle, Sun, Users } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface MetricBadgeProps {
  label: string
  value: string | number
  status?: "excellent" | "good" | "moderate" | "poor"
  icon?: "check" | "alert" | "sun" | "users"
  className?: string
}

const iconMap = {
  check: CheckCircle2,
  alert: AlertCircle,
  sun: Sun,
  users: Users,
}

const statusColors = {
  excellent: "bg-success/10 text-success border-success/20",
  good: "bg-success/10 text-success border-success/20",
  moderate: "bg-warning/10 text-warning border-warning/20",
  poor: "bg-destructive/10 text-destructive border-destructive/20",
}

export function MetricBadge({ label, value, status = "good", icon, className }: MetricBadgeProps) {
  const Icon = icon ? iconMap[icon] : null

  return (
    <div className={cn("flex items-center justify-between gap-3", className)}>
      <div className="flex items-center gap-2">
        {Icon && <Icon className="w-4 h-4 text-muted-foreground" />}
        <span className="text-sm text-muted-foreground">{label}</span>
      </div>
      <Badge variant="outline" className={cn("font-semibold", statusColors[status])}>
        {value}
      </Badge>
    </div>
  )
}
