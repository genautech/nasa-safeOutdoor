import axios, { AxiosError } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Configure axios defaults
const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging and error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.status} ${response.config.url}`);
    return response;
  },
  (error: AxiosError) => {
    console.error('[API Response Error]', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

// Types
export interface AnalyzeRequest {
  activity: string;
  lat: number;
  lon: number;
  start_time?: string;
  duration_hours: number;
}

export interface AnalyzeResponse {
  request_id: string;
  risk_score: number;
  category: string;
  air_quality: {
    aqi: number;
    category: string;
    pm25: number;
    no2: number;
    dominant_pollutant: string;
  };
  weather_forecast: Array<{
    timestamp: string;
    temp_c: number;
    humidity: number;
    wind_speed_kmh: number;
    wind_direction: number;
    uv_index: number;
    precipitation_mm: number;
    cloud_cover: number;
  }>;
  elevation: {
    elevation_m: number;
    terrain_type: string;
    slope_degrees: number | null;
  };
  checklist: Array<{
    item: string;
    required: boolean;
    reason: string;
    category: string;
  }>;
  warnings: string[];
  ai_summary: string;
  risk_factors: Array<{
    factor: string;
    score: number;
    weight: number;
  }>;
  data_sources: string[];
  generated_at: string;
}

export interface ForecastResponse {
  location: {
    lat: number;
    lon: number;
    city: string | null;
    address: string | null;
  };
  forecast: Array<{
    date: string;
    aqi_avg: number;
    aqi_max: number;
    temp_high: number;
    temp_low: number;
    condition: string;
    safety_score: number;
    recommended: boolean;
  }>;
  generated_at: string;
}

/**
 * Main analysis endpoint - orchestrates all data fetching and returns comprehensive safety analysis
 */
export async function analyzeAdventure(data: AnalyzeRequest): Promise<AnalyzeResponse> {
  try {
    const response = await apiClient.post<AnalyzeResponse>('/api/analyze', data);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.detail || error.message;
      throw new Error(`Analysis failed: ${message}`);
    }
    throw error;
  }
}

/**
 * Get multi-day forecast for location
 */
export async function getForecast(
  lat: number,
  lon: number,
  hours: number = 24
): Promise<ForecastResponse> {
  try {
    const response = await apiClient.get<ForecastResponse>('/api/forecast', {
      params: { lat, lon, hours },
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.detail || error.message;
      throw new Error(`Forecast fetch failed: ${message}`);
    }
    throw error;
  }
}

/**
 * Health check for backend API
 */
export async function healthCheck(): Promise<{ status: string; service: string; version: string }> {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(`Health check failed: ${error.message}`);
    }
    throw error;
  }
}

/**
 * Check if backend is reachable
 */
export async function checkBackendConnection(): Promise<boolean> {
  try {
    await healthCheck();
    return true;
  } catch (error) {
    console.error('Backend connection failed:', error);
    return false;
  }
}

// Export API client for custom requests
export { apiClient };
