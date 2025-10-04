"""Pydantic models for request/response validation."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime


# ===== Request Models =====

class LocationRequest(BaseModel):
    """Single location coordinates."""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")
    city: Optional[str] = None
    address: Optional[str] = None


class WaypointRequest(BaseModel):
    """Waypoint for route analysis."""
    id: str
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    order: int = Field(..., ge=0)
    name: Optional[str] = None


class RouteRequest(BaseModel):
    """Route with multiple waypoints."""
    waypoints: list[WaypointRequest] = Field(..., min_length=2)
    total_distance: Optional[float] = None
    estimated_duration: Optional[int] = None  # minutes


class AnalyzeRequest(BaseModel):
    """Main analysis request."""
    activity: str = Field(..., description="Activity type (hiking, cycling, running, etc.)")
    mode: Literal["single", "route"] = Field(..., description="Location mode")
    location: Optional[LocationRequest] = None
    route: Optional[RouteRequest] = None
    
    @field_validator("location")
    def validate_location(cls, v, info):
        """Ensure location is provided if mode is 'single'."""
        if info.data.get("mode") == "single" and v is None:
            raise ValueError("location is required when mode is 'single'")
        return v
    
    @field_validator("route")
    def validate_route(cls, v, info):
        """Ensure route is provided if mode is 'route'."""
        if info.data.get("mode") == "route" and v is None:
            raise ValueError("route is required when mode is 'route'")
        return v


class ForecastRequest(BaseModel):
    """Forecast request for specific location."""
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    days: int = Field(7, ge=1, le=14, description="Number of days to forecast")


# ===== Response Models =====

class AirQualityData(BaseModel):
    """Air quality metrics."""
    aqi: int = Field(..., ge=0, le=500)
    status: str  # Good, Moderate, Unhealthy, etc.
    pm25: float
    no2: float
    o3: Optional[float] = None
    co: Optional[float] = None


class WeatherData(BaseModel):
    """Weather conditions."""
    temp: float
    feels_like: Optional[float] = None
    humidity: int
    wind_speed: float
    wind_direction: Optional[int] = None
    condition: str
    cloud_cover: Optional[int] = None
    visibility: Optional[float] = None


class HealthData(BaseModel):
    """Health-related metrics."""
    uv_exposure: int = Field(..., ge=0, le=15)
    respiratory_risk: str
    heat_stress: str
    pollen_level: str
    altitude_effect: str
    visibility_km: float


class SatelliteData(BaseModel):
    """Satellite imagery data."""
    goes16: dict
    modis: dict
    firms: dict  # Fire information


class RecommendedTime(BaseModel):
    """Recommended activity time window."""
    date: str
    start_time: str
    end_time: str
    reason: str


class RouteSegment(BaseModel):
    """Route segment analysis."""
    segment_id: str
    name: str
    time: str
    aqi: int
    uv_index: int
    warnings: list[str]


class SafetyAnalysis(BaseModel):
    """Complete safety analysis response."""
    safety_score: int = Field(..., ge=0, le=100)
    risk_level: str
    weather: WeatherData
    air_quality: AirQualityData
    health_data: HealthData
    environmental_metrics: dict
    satellite_data: SatelliteData
    recommended_time: RecommendedTime
    route_segments: Optional[list[RouteSegment]] = None
    gear_checklist: list[str]
    warnings: list[str]
    ai_insights: str


class AnalyzeResponse(BaseModel):
    """Response for analyze endpoint."""
    request_id: str
    analysis: SafetyAnalysis
    metadata: dict


class ForecastDay(BaseModel):
    """Single day forecast."""
    date: str
    aqi_avg: int
    aqi_max: int
    temp_high: float
    temp_low: float
    condition: str
    safety_score: int
    recommended: bool


class ForecastResponse(BaseModel):
    """Multi-day forecast response."""
    location: LocationRequest
    forecast: list[ForecastDay]
    generated_at: datetime


# ===== Trip Models (Database) =====

class TripCreate(BaseModel):
    """Create new trip record."""
    user_id: Optional[str] = None
    activity: str
    location_data: dict
    analysis_data: dict


class TripResponse(BaseModel):
    """Trip record from database."""
    id: str
    user_id: Optional[str]
    activity: str
    location_data: dict
    analysis_data: dict
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    message: str
    request_id: Optional[str] = None
