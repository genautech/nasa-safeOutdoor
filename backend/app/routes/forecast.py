"""Forecast endpoint for multi-day predictions."""
from fastapi import APIRouter, HTTPException, Request
from app.models.schemas import ForecastRequest, ForecastResponse
from app.services.openaq import OpenAQService
from app.services.weather import WeatherService
from app.logic.risk_score import RiskScoreCalculator
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/forecast", response_model=ForecastResponse)
async def get_forecast(
    request: Request,
    lat: float,
    lon: float,
    days: int = 7
):
    """
    Get multi-day forecast for location.
    
    Query Parameters:
        lat: Latitude
        lon: Longitude
        days: Number of days (1-14, default 7)
    """
    request_id = getattr(request.state, "request_id", "unknown")
    logger.info(f"[{request_id}] Forecast request: ({lat}, {lon}), {days} days")
    
    if days < 1 or days > 14:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 14")
    
    try:
        # Initialize services
        weather_service = WeatherService()
        openaq_service = OpenAQService()
        risk_calculator = RiskScoreCalculator()
        
        # Fetch weather forecast
        logger.info(f"[{request_id}] Fetching weather forecast...")
        weather_forecast = await weather_service.get_forecast(lat, lon, days)
        
        # TODO: Fetch historical AQ data for trend prediction
        historical_aq = await openaq_service.get_historical_data(lat, lon, days=7)
        
        # Build forecast response
        forecast_days = []
        for day_data in weather_forecast:
            # TODO: Predict AQI based on weather and historical patterns
            # For now, use historical average
            predicted_aqi = self._predict_aqi(day_data, historical_aq)
            
            # Calculate safety score for the day
            mock_aq_data = {"aqi": predicted_aqi, "pm25": predicted_aqi * 0.3}
            mock_satellite = {"goes16": {"uv_index": day_data.get("uv_index", 7)}, "modis": {}, "firms": {}}
            mock_elevation = {"elevation_m": 100, "altitude_effect": "none"}
            
            safety_data = risk_calculator.calculate_safety_score(
                air_quality_data=mock_aq_data,
                weather_data={
                    "temp": day_data["temp_high"],
                    "wind_speed": day_data.get("wind_speed_max", 10),
                    "humidity": 50,
                    "condition": day_data["condition"],
                    "visibility": 10
                },
                satellite_data=mock_satellite,
                elevation_data=mock_elevation,
                activity="hiking"  # Generic activity
            )
            
            forecast_days.append({
                "date": day_data["date"],
                "aqi_avg": predicted_aqi,
                "aqi_max": int(predicted_aqi * 1.2),
                "temp_high": day_data["temp_high"],
                "temp_low": day_data["temp_low"],
                "condition": day_data["condition"],
                "safety_score": safety_data["safety_score"],
                "recommended": safety_data["safety_score"] >= 70
            })
        
        response = {
            "location": {
                "lat": lat,
                "lon": lon,
                "city": None,
                "address": None
            },
            "forecast": forecast_days,
            "generated_at": datetime.utcnow()
        }
        
        logger.info(f"[{request_id}] Forecast generated: {len(forecast_days)} days")
        return response
        
    except Exception as e:
        logger.error(f"[{request_id}] Forecast failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


def _predict_aqi(day_data: dict, historical: list[dict]) -> int:
    """
    Predict AQI based on weather and historical data.
    
    TODO: Implement ML model or better heuristics
    """
    # Simple baseline: use historical average with weather adjustments
    if historical:
        avg_aqi = sum(h.get("aqi_avg", 50) for h in historical) / len(historical)
    else:
        avg_aqi = 50
    
    # Adjust based on weather
    precip_prob = day_data.get("precipitation_prob", 0)
    if precip_prob > 50:
        avg_aqi *= 0.7  # Rain clears air
    
    wind_speed = day_data.get("wind_speed_max", 10)
    if wind_speed > 15:
        avg_aqi *= 0.8  # Wind disperses pollutants
    
    return int(max(0, min(500, avg_aqi)))


@router.post("/forecast", response_model=ForecastResponse)
async def post_forecast(request: Request, data: ForecastRequest):
    """
    POST version of forecast endpoint.
    
    Accepts ForecastRequest body instead of query params.
    """
    return await get_forecast(
        request=request,
        lat=data.lat,
        lon=data.lon,
        days=data.days
    )
