export interface Activity {
  id: string
  name: string
  icon: string
}

export interface HealthData {
  respiratoryRisk: "low" | "moderate" | "high"
  uvExposure: number // 0-11+ scale
  heatStress: "minimal" | "moderate" | "severe"
  wildfireSmoke: boolean
  pollenLevel: "low" | "medium" | "high"
  altitudeEffect: "none" | "mild" | "significant"
  visibilityKm: number
  lightningRisk: boolean
}

export interface SatelliteData {
  tempo: {
    no2: number // ppb
    status: string
  }
  modis: {
    aod: number // Aerosol Optical Depth
    visibility: string
  }
  goes16: {
    cloudCover: number // percentage
    uvIndex: number
  }
  firms: {
    activeFiresNearby: boolean
    distanceKm: number | null
  }
  gpm: {
    precipitationForecast: string
    probability: number
  }
}

export interface EnvironmentalMetrics {
  airQuality: {
    aqi: number
    pm25: number
    no2: number
    status: "good" | "moderate" | "unhealthy"
  }
  weather: {
    condition: string
    temp: number
    humidity: number
    windSpeed: number
  }
  uvIndex: number
  cloudCover: number
  visibility: number
  wildfireRisk: {
    detected: boolean
    distance: number | null
  }
}

export interface RouteSegmentData {
  segmentId: string
  name: string
  aqi: number
  uvIndex: number
  time: string
  warnings: string[]
}

export interface SafetyAnalysis {
  score: number
  overallSafety: {
    environmental: number
    health: number
    terrain: number
  }
  aqi: number
  pm25: number
  no2: number
  weather: {
    condition: string
    temp: number
    uvIndex: string
    humidity: number
    windSpeed: number
  }
  trailConditions: string
  recommendedTime: {
    date: string
    startTime: string
    endTime: string
  }
  emergencyFeaturesActive: boolean
  healthData: HealthData
  satelliteData: SatelliteData
  environmentalMetrics: EnvironmentalMetrics
  routeSegments?: RouteSegmentData[]
  emergencyInfo: {
    nearestHospital: string
    distance: number
    emergencyContact: string
    cellCoverage: string
  }
}

export interface LoadingItem {
  id: string
  label: string
  sublabel: string
  icon: string
  duration: number
}

export interface LocationData {
  mode: "single" | "route"
  single?: {
    lat: number
    lon: number
    address: string
    city: string
  }
  route?: {
    waypoints: Array<{
      id: string
      lat: number
      lon: number
      address: string
      order: number
    }>
    totalDistance: number // km
    estimatedDuration: number // minutes
  }
}

export interface AdventureContext {
  activity: string
  location: LocationData
  timestamp: number
  safetyAnalysis?: SafetyAnalysis
}
