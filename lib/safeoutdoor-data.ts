export interface NasaDataset {
  id: string
  name: string
  short: string
  iconUrl: string
  primaryMetric: string
  unit: string
  currentValue: number
  change: number
  changeLabel: string
  accuracy: number
  description: string
  insights: string[]
  dataSeries: Array<{ label: string; value: number }>
}

export interface RoutineOption {
  id: string
  label: string
  source: "Fitbit" | "Calendar" | "Manual"
  nextOccurrence: string
  location: string
  healthFocus: string
}

export interface NotificationMessage {
  id: string
  timestamp: string
  message: string
  channel: "push" | "email" | "sms"
  emphasis?: "positive" | "warning"
}

export interface ActivityHistoryItem {
  id: string
  activity: string
  date: string
  location: string
  conditions: string
  status: "completed" | "skipped" | "adjusted"
  score: number
}

export const nasaDatasets: NasaDataset[] = [
  {
    id: "tempo",
    name: "NASA TEMPO",
    short: "TEMPO",
    iconUrl: "https://cdn-icons-png.flaticon.com/512/8617/8617145.png",
    primaryMetric: "NO₂ & PM2.5",
    unit: "µg/m³",
    currentValue: 11.3,
    change: -18,
    changeLabel: "Cleaner than yesterday",
    accuracy: 0.93,
    description:
      "Hourly scans across North America showing breathable windows and neighborhood-level pollution hotspots.",
    insights: [
      "NO₂ exposure down 20% during sunrise windows",
      "Microburst of PM2.5 predicted near downtown after 9:30 AM",
      "Safe to maintain moderate intensity workouts until 10:45 AM",
    ],
    dataSeries: [
      { label: "4 AM", value: 16 },
      { label: "6 AM", value: 13 },
      { label: "8 AM", value: 11.3 },
      { label: "10 AM", value: 14 },
      { label: "12 PM", value: 18 },
      { label: "2 PM", value: 21 },
    ],
  },
  {
    id: "omi",
    name: "NASA Aura/OMI",
    short: "OMI",
    iconUrl: "https://cdn-icons-png.flaticon.com/512/9239/9239152.png",
    primaryMetric: "UV Index",
    unit: "UV-I",
    currentValue: 4.6,
    change: -12,
    changeLabel: "UV dip expected",
    accuracy: 0.91,
    description:
      "Ultraviolet monitoring from space to time sunscreen reminders and protective gear alerts.",
    insights: [
      "Low UV valley from 6:45 AM to 9:15 AM",
      "Shade recommended after 11:00 AM as UV climbs above 7",
      "Cloud cover reduces midday exposure by 18%",
    ],
    dataSeries: [
      { label: "5 AM", value: 1.2 },
      { label: "7 AM", value: 2.1 },
      { label: "9 AM", value: 4.6 },
      { label: "11 AM", value: 6.9 },
      { label: "1 PM", value: 7.8 },
      { label: "3 PM", value: 6.5 },
    ],
  },
  {
    id: "merra2",
    name: "NASA MERRA-2",
    short: "MERRA-2",
    iconUrl: "https://cdn-icons-png.flaticon.com/512/11150/11150998.png",
    primaryMetric: "Heat & Humidity",
    unit: "°F",
    currentValue: 76,
    change: -5,
    changeLabel: "Heat easing slightly",
    accuracy: 0.9,
    description:
      "Reanalysis dataset blending satellites and stations to flag heat stress and hydration checkpoints.",
    insights: [
      "Humidity stays below 60% until late morning",
      "Heat index crosses 90°F near 1:30 PM",
      "Recommend shaded cool-down after each 45 min of activity",
    ],
    dataSeries: [
      { label: "5 AM", value: 68 },
      { label: "7 AM", value: 70 },
      { label: "9 AM", value: 74 },
      { label: "11 AM", value: 79 },
      { label: "1 PM", value: 84 },
      { label: "3 PM", value: 87 },
    ],
  },
  {
    id: "gpm",
    name: "NASA GPM",
    short: "GPM",
    iconUrl: "https://cdn-icons-png.flaticon.com/512/6429/6429688.png",
    primaryMetric: "Rainfall Intensity",
    unit: "%",
    currentValue: 18,
    change: 6,
    changeLabel: "Drizzle risk later",
    accuracy: 0.92,
    description:
      "Global Precipitation Measurement radar spotting microbursts and rain lull windows so you stay dry.",
    insights: [
      "Light drizzle probability increases after 4:00 PM",
      "Storm cells stay west of trailhead for the next 6 hours",
      "Carry light shell only if staying out past sunset",
    ],
    dataSeries: [
      { label: "6 AM", value: 8 },
      { label: "8 AM", value: 10 },
      { label: "10 AM", value: 12 },
      { label: "12 PM", value: 15 },
      { label: "2 PM", value: 18 },
      { label: "4 PM", value: 26 },
    ],
  },
]

export const autoDetectedRoutines: RoutineOption[] = [
  {
    id: "morning-run",
    label: "Sunrise Run Club",
    source: "Fitbit",
    nextOccurrence: "Tomorrow · 6:45 AM",
    location: "Charlotte Greenway Trail",
    healthFocus: "Respiratory recovery & cadence tracking",
  },
  {
    id: "evening-hike",
    label: "Blue Ridge Sunset Hike",
    source: "Calendar",
    nextOccurrence: "Friday · 5:30 PM",
    location: "Crowders Mountain State Park",
    healthFocus: "UV-sensitive itinerary with hydration reminders",
  },
  {
    id: "manual-hike",
    label: "Manual: Hike Tomorrow",
    source: "Manual",
    nextOccurrence: "Tomorrow · 7:30 AM",
    location: "Uwharrie National Forest",
    healthFocus: "Family-friendly pace with pollen checks",
  },
]

export const notificationMessages: NotificationMessage[] = [
  {
    id: "n1",
    timestamp: "6:00 AM",
    message: "Hike at 7 AM: air is 20% cleaner and UV stays below 3 — hydrate and enjoy!",
    channel: "push",
    emphasis: "positive",
  },
  {
    id: "n2",
    timestamp: "6:45 AM",
    message: "Calendar sync: shifted your trail run to 6:50 AM to dodge a PM2.5 pocket downtown.",
    channel: "push",
  },
  {
    id: "n3",
    timestamp: "7:15 AM",
    message: "Fitbit auto-detected recovery walk · pace slower but safe despite rising humidity.",
    channel: "email",
  },
  {
    id: "n4",
    timestamp: "4:25 PM",
    message: "Storm cell alert from GPM radar. Move campsite check-in 30 minutes earlier to stay dry.",
    channel: "sms",
    emphasis: "warning",
  },
]

export const activityHistory: ActivityHistoryItem[] = [
  {
    id: "h1",
    activity: "Morning Run",
    date: "Oct 1, 2025",
    location: "Charlotte Rail Trail",
    conditions: "AQI 42 · UV 2 · Heat index 74°F",
    status: "completed",
    score: 92,
  },
  {
    id: "h2",
    activity: "Family Hike",
    date: "Sep 28, 2025",
    location: "Pisgah National Forest",
    conditions: "AQI 55 · UV 3 · Light breeze",
    status: "adjusted",
    score: 88,
  },
  {
    id: "h3",
    activity: "Trail Ride",
    date: "Sep 23, 2025",
    location: "Lake Norman State Park",
    conditions: "AQI 38 · UV 6 · Heat index 89°F",
    status: "completed",
    score: 85,
  },
  {
    id: "h4",
    activity: "Kayak Session",
    date: "Sep 18, 2025",
    location: "Catawba River",
    conditions: "AQI 40 · UV 5 · Humidity 63%",
    status: "completed",
    score: 91,
  },
]

export const riskSeriesLabels = [
  "5 AM",
  "6 AM",
  "7 AM",
  "8 AM",
  "9 AM",
  "10 AM",
  "11 AM",
  "12 PM",
]

export const riskSeriesValues = {
  respiratory: [0.12, 0.1, 0.08, 0.09, 0.14, 0.2, 0.28, 0.32],
  uv: [0.1, 0.15, 0.25, 0.38, 0.5, 0.74, 0.82, 0.68],
  heat: [0.18, 0.2, 0.24, 0.3, 0.36, 0.44, 0.52, 0.6],
  precipitation: [0.05, 0.05, 0.06, 0.08, 0.1, 0.12, 0.15, 0.2],
}

export const recommendedWindows = [
  {
    id: "window-1",
    title: "Sunrise Boost",
    window: "6:30 – 8:15 AM",
    detail: "Cleanest air window and low UV based on TEMPO and OMI scans.",
  },
  {
    id: "window-2",
    title: "Late Morning Yoga",
    window: "9:45 – 11:00 AM",
    detail: "Heat index stays under 85°F with humidity <60% according to MERRA-2.",
  },
  {
    id: "window-3",
    title: "Sunset Chill",
    window: "5:15 – 6:30 PM",
    detail: "GPM radar shows showers holding off until after 7:00 PM.",
  },
]

export const accuracyTarget = 0.9

export const heroImageUrl =
  "https://images.pexels.com/photos/2259826/pexels-photo-2259826.jpeg?auto=compress&cs=tinysrgb&h=800"

export const wizardBackgroundUrl =
  "https://images.unsplash.com/photo-1526481280695-3c4697e3e46a?auto=format&fit=crop&w=1400&q=80"

export const historyBackgroundUrl =
  "https://images.unsplash.com/photo-1470246973918-29a93221c455?auto=format&fit=crop&w=1400&q=80"
