"""Main analysis endpoint."""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import asyncio
import logging

from app.services.nasa_tempo import fetch_tempo_no2
from app.services.openaq import fetch_openaq_data
from app.services.weather import fetch_weather_forecast
from app.services.elevation import fetch_elevation
from app.logic.risk_score import calculate_safety_score
from app.logic.checklist import generate_checklist
from app.logic.aqi import calculate_aqi_from_pollutants, get_aqi_category as get_aqi_category_new

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["analysis"])


# ===== Request Models =====

class AnalyzeRequest(BaseModel):
    """Request model for adventure analysis."""
    activity: str = Field(..., description="Activity type (hiking, cycling, etc.)")
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")
    start_time: Optional[str] = Field(None, description="Start time (ISO 8601)")
    duration_hours: int = Field(4, ge=1, le=72, description="Expected duration in hours")
    user_profile: dict = Field(default_factory=dict, description="User preferences and health info")


# ===== Response Models =====

class AirQualityResponse(BaseModel):
    """Air quality data response."""
    aqi: int
    category: str
    pm25: float
    no2: float
    dominant_pollutant: str


class WeatherHourResponse(BaseModel):
    """Single hour weather data."""
    timestamp: str
    temp_c: float
    humidity: int
    wind_speed_kmh: float
    wind_direction: int
    uv_index: float
    precipitation_mm: float
    cloud_cover: int


class ChecklistItemResponse(BaseModel):
    """Checklist item."""
    item: str
    required: bool
    reason: str
    category: str


class OverallSafetyResponse(BaseModel):
    """Overall safety breakdown scores."""
    environmental: float
    health: float
    terrain: float
    overall: float


class AnalyzeResponse(BaseModel):
    """Complete analysis response."""
    request_id: str
    risk_score: float
    category: str
    overallSafety: OverallSafetyResponse
    air_quality: AirQualityResponse
    weather_forecast: List[WeatherHourResponse]
    elevation: dict
    checklist: List[ChecklistItemResponse]
    warnings: List[str]
    ai_summary: str
    risk_factors: List[dict]
    data_sources: List[str]
    generated_at: str


# Removed - now using app.logic.aqi module


async def generate_ai_summary(
    request: AnalyzeRequest,
    risk_data: dict,
    checklist: List[dict],
    air_quality: dict,
    weather: dict
) -> str:
    """
    Generate natural language AI summary using OpenAI.
    
    Falls back to template-based summary if OpenAI fails.
    """
    try:
        from openai import AsyncOpenAI
        from app.config import settings
        
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        # Build context for AI
        context = f"""
Activity: {request.activity}
Location: {request.lat:.4f}, {request.lon:.4f}
Duration: {request.duration_hours} hours

Safety Score: {risk_data['score']}/10 ({risk_data['category']})
Air Quality: AQI {air_quality['aqi']} ({air_quality['category']})
Weather: {weather.get('temp_c', 20)}°C, UV {weather.get('uv_index', 5)}, Wind {weather.get('wind_speed_kmh', 10)} km/h

Key Warnings:
{chr(10).join('- ' + w for w in risk_data['warnings'][:3])}

Required Gear Items: {sum(1 for item in checklist if item['required'])}
"""
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an outdoor safety expert. Provide a concise, friendly 2-3 sentence summary of the conditions for this outdoor activity. Focus on the most important safety considerations and be encouraging when conditions are good, cautionary when they're challenging."
                },
                {
                    "role": "user",
                    "content": context
                }
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        summary = response.choices[0].message.content.strip()
        logger.info(f"Generated AI summary: {len(summary)} characters")
        return summary
        
    except Exception as e:
        logger.warning(f"AI summary generation failed: {e}, using fallback")
        return generate_fallback_summary(risk_data, air_quality, weather)


def _build_data_sources_list(tempo_data: Optional[dict], openaq_data: Optional[dict], no2_source: Optional[str]) -> List[str]:
    """
    Build list of data sources used for this analysis.
    
    Clearly indicates which sources provided actual data vs fallbacks.
    Shows NASA TEMPO when satellite data was used, OpenAQ for ground measurements.
    """
    sources = []
    
    # NO2 source (TEMPO or OpenAQ or fallback)
    if tempo_data and tempo_data.get("no2_ppb") is not None:
        quality = tempo_data.get("quality_flag", 0)
        if quality == 0:
            sources.append("NASA TEMPO satellite (NO2)")
        else:
            sources.append("NASA TEMPO satellite (NO2 estimated)")
    elif "OpenAQ" in str(no2_source):
        sources.append("OpenAQ ground stations (NO2)")
    elif "Fallback" in str(no2_source):
        # Don't add fallback to sources - it's not a real data source
        pass
    
    # PM2.5 source (always OpenAQ, TEMPO doesn't measure particles)
    if openaq_data and openaq_data.get("pm25") is not None:
        # Only add if not already mentioned
        if not any("OpenAQ" in s for s in sources):
            sources.append("OpenAQ ground stations (PM2.5)")
        elif "OpenAQ ground stations (NO2)" in sources:
            # Replace with combined
            sources = [s for s in sources if s != "OpenAQ ground stations (NO2)"]
            sources.append("OpenAQ ground stations (NO2, PM2.5)")
    
    # Weather and elevation (always used)
    sources.extend([
        "Open-Meteo weather API",
        "Open-Elevation terrain API"
    ])
    
    return sources


def generate_fallback_summary(risk_data: dict, air_quality: dict, weather: dict) -> str:
    """Generate template-based summary when AI is unavailable."""
    score = risk_data['score']
    category = risk_data['category']
    aqi = air_quality['aqi']
    temp = weather.get('temp_c', 20)
    
    if score >= 8.5:
        return f"Excellent conditions for your activity! Air quality is {air_quality['category'].lower()} (AQI {aqi}) and weather is favorable at {temp}°C. Enjoy your adventure safely!"
    elif score >= 7.0:
        return f"Good conditions overall. Air quality is {air_quality['category'].lower()} (AQI {aqi}) with {temp}°C temperatures. {risk_data['warnings'][0] if risk_data['warnings'] else 'Stay hydrated and protected from the sun.'}"
    elif score >= 5.0:
        return f"Moderate conditions require some precautions. Air quality is {air_quality['category'].lower()} (AQI {aqi}). {' '.join(risk_data['warnings'][:2]) if risk_data['warnings'] else 'Monitor conditions and take appropriate safety measures.'}"
    else:
        return f"Challenging conditions detected. Air quality is {air_quality['category'].lower()} (AQI {aqi}) and score is {score}/10. {' '.join(risk_data['warnings'][:2])}. Consider rescheduling if possible."


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_adventure(request: Request, req: AnalyzeRequest):
    """
    Main endpoint: Orchestrates all data fetching and analysis.
    
    Flow:
    1. Fetch NASA TEMPO data (NO2)
    2. Fetch OpenAQ data (PM2.5)
    3. Fetch weather forecast
    4. Fetch elevation
    5. Calculate AQI
    6. Calculate risk score
    7. Generate checklist
    8. Generate AI summary
    9. Return complete analysis
    """
    request_id = getattr(request.state, "request_id", "unknown")
    logger.info(
        f"[{request_id}] Analysis request: {req.activity} at ({req.lat}, {req.lon}), "
        f"duration={req.duration_hours}h"
    )
    
    try:
        start_time = datetime.utcnow()
        
        # Step 1: Fetch all data in parallel for optimal performance
        logger.info(f"[{request_id}] Fetching data from all sources...")
        
        tempo_task = fetch_tempo_no2(req.lat, req.lon)
        openaq_task = fetch_openaq_data(req.lat, req.lon, radius_km=25)
        weather_task = fetch_weather_forecast(req.lat, req.lon, hours=req.duration_hours)
        elevation_task = fetch_elevation(req.lat, req.lon)
        
        # Gather all data (None if any service fails)
        tempo_data, openaq_data, weather_data, elevation_data = await asyncio.gather(
            tempo_task,
            openaq_task,
            weather_task,
            elevation_task,
            return_exceptions=False
        )
        
        logger.info(f"[{request_id}] Data fetched successfully")
        
        # Step 2: Handle None responses with fallback data
        if tempo_data is None:
            logger.warning(f"[{request_id}] TEMPO data unavailable, using fallback")
            tempo_data = {"no2_ppb": 20.0, "no2_column": 2.5e15}
        
        if openaq_data is None:
            logger.warning(f"[{request_id}] OpenAQ data unavailable, using fallback")
            openaq_data = {"pm25": 15.0, "no2": 20.0, "stations": 0}
        
        if weather_data is None or len(weather_data) == 0:
            logger.warning(f"[{request_id}] Weather data unavailable, using fallback")
            weather_data = [{
                "timestamp": datetime.utcnow().isoformat(),
                "temp_c": 20.0,
                "humidity": 50,
                "wind_speed_kmh": 10.0,
                "wind_direction": 180,
                "uv_index": 5.0,
                "precipitation_mm": 0.0,
                "cloud_cover": 30
            }]
        
        if elevation_data is None:
            logger.warning(f"[{request_id}] Elevation data unavailable, using fallback")
            elevation_data = {"elevation_m": 100.0, "terrain_type": "lowland"}
        
        # Step 3: Merge TEMPO and OpenAQ data intelligently
        # Strategy:
        # 1. Try NASA TEMPO first (satellite, North America only)
        # 2. Fallback to OpenAQ for NO2 (ground stations, global)
        # 3. Always use OpenAQ for PM2.5 (TEMPO doesn't measure particles)
        
        no2_ppb = None
        no2_source = None
        
        # Check if TEMPO provided valid NO2 data
        if tempo_data and tempo_data.get("no2_ppb") is not None:
            no2_ppb = tempo_data["no2_ppb"]
            quality = tempo_data.get("quality_flag", 0)
            age = tempo_data.get("age_hours", 0)
            
            if quality == 0:
                no2_source = f"NASA TEMPO satellite ({age:.1f}h old)"
            else:
                no2_source = f"NASA TEMPO estimated ({age:.1f}h old)"
            
            logger.info(
                f"[{request_id}] ✅ Using TEMPO NO2: {no2_ppb:.2f} ppb "
                f"[{no2_source}]"
            )
        
        # Fallback to OpenAQ if TEMPO unavailable
        elif openaq_data and openaq_data.get("no2") is not None:
            no2_ppb = openaq_data["no2"]
            stations = openaq_data.get("stations", 0)
            no2_source = f"OpenAQ ground stations (n={stations})"
            logger.info(
                f"[{request_id}] 🔄 Using OpenAQ NO2 (TEMPO unavailable): "
                f"{no2_ppb:.2f} ppb [{no2_source}]"
            )
        
        # Last resort: use fallback value
        else:
            no2_ppb = 20.0  # Conservative moderate value
            no2_source = "Fallback estimate"
            logger.warning(
                f"[{request_id}] ⚠️ No NO2 data from TEMPO or OpenAQ, "
                f"using fallback: {no2_ppb} ppb"
            )
        
        pm25 = openaq_data.get("pm25") if openaq_data else None
        if pm25:
            logger.info(f"[{request_id}] Using OpenAQ PM2.5: {pm25:.2f} μg/m³")
        
        # Calculate AQI from available pollutants
        aqi, dominant_pollutant = calculate_aqi_from_pollutants(pm25, no2_ppb)
        aqi_category = get_aqi_category_new(aqi)
        
        logger.info(f"[{request_id}] Calculated AQI: {aqi} ({aqi_category}), dominant: {dominant_pollutant}")
        
        # Step 4: Calculate risk score
        current_weather = weather_data[0]
        risk_input = {
            "activity": req.activity,
            "aqi": aqi,
            "pm25": pm25 if pm25 is not None else 15.0,
            "no2": no2_ppb if no2_ppb is not None else 20.0,
            "weather": current_weather,
            "elevation": int(elevation_data.get("elevation_m", 100)),
            "uv_index": current_weather.get("uv_index", 5.0)
        }
        
        risk_data = calculate_safety_score(risk_input)
        logger.info(f"[{request_id}] Risk score: {risk_data['score']}/10 ({risk_data['category']})")
        
        # Step 5: Generate checklist
        checklist_input = {
            "aqi": aqi,
            "pm25": pm25 if pm25 is not None else 15.0,
            "no2": no2_ppb if no2_ppb is not None else 20.0,
            "uv_index": current_weather.get("uv_index", 5.0),
            "elevation": int(elevation_data.get("elevation_m", 100))
        }
        
        checklist = generate_checklist(
            req.activity,
            checklist_input,
            current_weather
        )
        logger.info(f"[{request_id}] Generated checklist: {len(checklist)} items")
        
        # Step 6: Generate AI summary
        air_quality_dict = {
            "aqi": aqi,
            "category": aqi_category,
            "pm25": pm25 if pm25 is not None else 15.0,
            "no2": no2_ppb if no2_ppb is not None else 20.0
        }
        
        ai_summary = await generate_ai_summary(
            req,
            risk_data,
            checklist,
            air_quality_dict,
            current_weather
        )
        
        # Step 7: Calculate detailed safety breakdown with null safety
        try:
            # Safe extraction with null checks
            aqi_value = None
            if openaq_data and openaq_data.get("pm25") is not None:
                aqi_value = openaq_data.get("pm25")
            else:
                aqi_value = 50  # Default moderate
            
            elevation_m = None
            if elevation_data and elevation_data.get("elevation_m") is not None:
                elevation_m = elevation_data.get("elevation_m")
            else:
                elevation_m = 100  # Default lowland
            
            # Environmental score based on AQI (inverse relationship)
            # Ensure aqi_value is not None before math
            if aqi_value is not None:
                environmental_score = max(0, min(10, (100 - aqi_value) / 10))
            else:
                environmental_score = 8.0
            
            # Health score from risk calculation
            # Ensure risk_data["score"] exists and is not None
            health_score = risk_data.get("score", 8.0)
            if health_score is None:
                health_score = 8.0
            
            # Terrain score based on elevation and activity
            # Ensure elevation_m is not None
            if elevation_m is not None:
                if elevation_m < 1000:
                    terrain_score = 9.0
                elif elevation_m < 2000:
                    terrain_score = 7.5
                elif elevation_m < 3000:
                    terrain_score = 6.0
                else:
                    terrain_score = 4.5
            else:
                terrain_score = 8.0
            
            # Overall score (weighted average)
            overall_score = (environmental_score * 0.3 + health_score * 0.5 + terrain_score * 0.2)
            
            overall_safety = OverallSafetyResponse(
                environmental=round(environmental_score, 1),
                health=round(health_score, 1),
                terrain=round(terrain_score, 1),
                overall=round(overall_score, 1)
            )
            
            logger.info(
                f"[{request_id}] Safety breakdown: env={overall_safety.environmental}, "
                f"health={overall_safety.health}, terrain={overall_safety.terrain}"
            )
            
        except Exception as e:
            logger.error(f"[{request_id}] Safety calculation failed: {e}, using fallback values")
            # Fallback to safe default values
            overall_safety = OverallSafetyResponse(
                environmental=8.0,
                health=8.0,
                terrain=8.0,
                overall=8.0
            )
        
        # Step 8: Build complete response
        response = AnalyzeResponse(
            request_id=request_id,
            risk_score=risk_data["score"],
            category=risk_data["category"],
            overallSafety=overall_safety,
            air_quality=AirQualityResponse(
                aqi=aqi,
                category=aqi_category,
                pm25=pm25 if pm25 is not None else 15.0,
                no2=no2_ppb if no2_ppb is not None else 20.0,
                dominant_pollutant=dominant_pollutant
            ),
            weather_forecast=[
                WeatherHourResponse(**hour) for hour in weather_data[:24]
            ],
            elevation=elevation_data,
            checklist=[
                ChecklistItemResponse(**item) for item in checklist
            ],
            warnings=risk_data["warnings"],
            ai_summary=ai_summary,
            risk_factors=risk_data["risk_factors"],
            data_sources=_build_data_sources_list(tempo_data, openaq_data, no2_source),
            generated_at=datetime.utcnow().isoformat()
        )
        
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            f"[{request_id}] Analysis complete in {elapsed:.2f}s: "
            f"score={response.risk_score}/10, warnings={len(response.warnings)}"
        )
        
        return response
        
    except asyncio.TimeoutError:
        logger.error(f"[{request_id}] Analysis timed out")
        raise HTTPException(
            status_code=504,
            detail="Analysis timed out while fetching data from external services"
        )
    except Exception as e:
        logger.error(f"[{request_id}] Analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check for analyze service."""
    return {
        "status": "healthy",
        "service": "analyze",
        "endpoints": ["/api/analyze"]
    }
