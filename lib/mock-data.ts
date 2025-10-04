import type { Activity, SafetyAnalysis, LoadingItem, LocationData } from "./types"

export const activities: Activity[] = [
  { id: "hiking", name: "Hiking", icon: "🥾" },
  { id: "camping", name: "Camping", icon: "⛺" },
  { id: "rock-climbing", name: "Rock Climbing", icon: "🧗" },
  { id: "mountain-biking", name: "Mountain Biking", icon: "🚵" },
  { id: "running", name: "Running", icon: "🏃" },
  { id: "fishing", name: "Fishing", icon: "🎣" },
  { id: "trail-running", name: "Trail Running", icon: "👟" },
  { id: "bird-watching", name: "Bird Watching", icon: "🦅" },
]

export const getLoadingItems = (location: LocationData | null): LoadingItem[] => {
  const city = location?.mode === "single" ? location.single?.city : "your route"
  const coords =
    location?.mode === "single"
      ? `${location.single?.lat.toFixed(2)}, ${location.single?.lon.toFixed(2)}`
      : "multiple checkpoints"

  return [
    {
      id: "nasa-tempo",
      label: "NASA TEMPO",
      sublabel: `Scanning NO₂ at ${city} (${coords})...`,
      icon: "satellite",
      duration: 1500,
    },
    {
      id: "nasa-modis",
      label: "NASA MODIS",
      sublabel: "Analyzing aerosol optical depth...",
      icon: "eye",
      duration: 1200,
    },
    {
      id: "nasa-goes",
      label: "NASA GOES-16",
      sublabel: "Checking cloud cover and UV index...",
      icon: "cloud-sun",
      duration: 1300,
    },
    {
      id: "nasa-firms",
      label: "NASA FIRMS",
      sublabel: "Detecting active fires and smoke risk...",
      icon: "flame",
      duration: 1100,
    },
    {
      id: "nasa-gpm",
      label: "NASA GPM",
      sublabel: "Processing precipitation forecast...",
      icon: "cloud-rain",
      duration: 1000,
    },
    {
      id: "openaq",
      label: "OpenAQ",
      sublabel:
        location?.mode === "route"
          ? `Checking PM2.5 along route (${location.route?.waypoints.length} checkpoints)...`
          : "Checking PM2.5 levels...",
      icon: "wind",
      duration: 1200,
    },
    {
      id: "weather",
      label: "Weather data",
      sublabel: "Processing forecasts...",
      icon: "thermometer",
      duration: 1000,
    },
    {
      id: "trail",
      label: "Trail conditions",
      sublabel: "Checking latest updates!",
      icon: "mountain",
      duration: 1300,
    },
  ]
}

export const getMockSafetyAnalysis = (activity: string, location: LocationData | null): SafetyAnalysis => {
  const city = location?.mode === "single" ? location.single?.city : "Route"
  const isRoute = location?.mode === "route"

  return {
    score: 8.5,
    overallSafety: {
      environmental: 9,
      health: 8,
      terrain: 8,
    },
    aqi: 45,
    pm25: 12,
    no2: 8,
    weather: {
      condition: "Sunny",
      temp: 72,
      uvIndex: "7 (High)",
      humidity: 55,
      windSpeed: 8,
    },
    trailConditions: "Well-maintained",
    recommendedTime: {
      date: "Tomorrow",
      startTime: "8 AM",
      endTime: "2 PM",
    },
    emergencyFeaturesActive: true,
    healthData: {
      respiratoryRisk: "low",
      uvExposure: 7,
      heatStress: "moderate",
      wildfireSmoke: false,
      pollenLevel: "low",
      altitudeEffect: "none",
      visibilityKm: 15,
      lightningRisk: false,
    },
    satelliteData: {
      tempo: {
        no2: 8,
        status: "Good air quality detected",
      },
      modis: {
        aod: 0.12,
        visibility: "Excellent (>10km)",
      },
      goes16: {
        cloudCover: 20,
        uvIndex: 7,
      },
      firms: {
        activeFiresNearby: false,
        distanceKm: null,
      },
      gpm: {
        precipitationForecast: "No rain expected",
        probability: 5,
      },
    },
    environmentalMetrics: {
      airQuality: {
        aqi: 45,
        pm25: 12,
        no2: 8,
        status: "good",
      },
      weather: {
        condition: "Sunny",
        temp: 72,
        humidity: 55,
        windSpeed: 8,
      },
      uvIndex: 7,
      cloudCover: 20,
      visibility: 15,
      wildfireRisk: {
        detected: false,
        distance: null,
      },
    },
    routeSegments: isRoute
      ? [
          {
            segmentId: "1",
            name: "Start (Central Park)",
            aqi: 45,
            uvIndex: 3,
            time: "8:00 AM",
            warnings: [],
          },
          {
            segmentId: "2",
            name: "Midpoint (Brooklyn Bridge)",
            aqi: 67,
            uvIndex: 5,
            time: "9:15 AM",
            warnings: ["Increased traffic pollution - wear mask if sensitive"],
          },
          {
            segmentId: "3",
            name: "Checkpoint 3",
            aqi: 58,
            uvIndex: 7,
            time: "10:30 AM",
            warnings: [],
          },
          {
            segmentId: "4",
            name: "End (Prospect Park)",
            aqi: 52,
            uvIndex: 8,
            time: "11:45 AM",
            warnings: ["High UV - reapply sunscreen"],
          },
        ]
      : undefined,
    emergencyInfo: {
      nearestHospital: city === "New York" ? "Mount Sinai Hospital" : "Local Hospital",
      distance: 2.3,
      emergencyContact: "911",
      cellCoverage: "Excellent (4G/5G)",
    },
  }
}

export const mockLocationData: LocationData = {
  mode: "single",
  single: {
    lat: 40.7829,
    lon: -73.9654,
    address: "Central Park, New York, NY",
    city: "New York",
  },
}

export const mockRouteData: LocationData = {
  mode: "route",
  route: {
    waypoints: [
      {
        id: "1",
        lat: 40.7829,
        lon: -73.9654,
        address: "Central Park, New York, NY",
        order: 0,
      },
      {
        id: "2",
        lat: 40.7061,
        lon: -73.9969,
        address: "Brooklyn Bridge, New York, NY",
        order: 1,
      },
      {
        id: "3",
        lat: 40.6602,
        lon: -73.969,
        address: "Prospect Park, Brooklyn, NY",
        order: 2,
      },
    ],
    totalDistance: 12.5,
    estimatedDuration: 135,
  },
}
