"""Weather data service using NOAA and Open-Meteo."""
import httpx
import logging
from typing import Optional, List
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)


async def fetch_weather_forecast(lat: float, lon: float, hours: int = 24) -> Optional[List[dict]]:
    """
    Fetch hourly weather forecast.
    API: Open-Meteo (free, no key needed)
    
    Args:
        lat: Latitude
        lon: Longitude
        hours: Number of hours to forecast
    
    Returns:
        List of dicts with keys:
            - timestamp: str
            - temp_c: float
            - humidity: int
            - wind_speed_kmh: float
            - wind_direction: int
            - uv_index: float
            - precipitation_mm: float
            - cloud_cover: int
        Returns None on failure
    """
    max_retries = 3
    timeout = 10.0
    base_url = "https://api.open-meteo.com/v1/forecast"
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching weather forecast for ({lat}, {lon}) - Attempt {attempt + 1}/{max_retries}")
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(
                    base_url,
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,"
                                 "wind_direction_10m,uv_index,precipitation,cloud_cover",
                        "temperature_unit": "celsius",
                        "wind_speed_unit": "kmh",
                        "precipitation_unit": "mm",
                        "forecast_hours": min(hours, 240)  # API limit
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                hourly = data.get("hourly", {})
                times = hourly.get("time", [])
                
                if not times:
                    logger.warning("No hourly data in weather response")
                    return None
                
                # Build forecast list
                forecast = []
                for i in range(min(len(times), hours)):
                    forecast.append({
                        "timestamp": times[i],
                        "temp_c": hourly.get("temperature_2m", [])[i] if i < len(hourly.get("temperature_2m", [])) else 20.0,
                        "humidity": hourly.get("relative_humidity_2m", [])[i] if i < len(hourly.get("relative_humidity_2m", [])) else 50,
                        "wind_speed_kmh": hourly.get("wind_speed_10m", [])[i] if i < len(hourly.get("wind_speed_10m", [])) else 10.0,
                        "wind_direction": hourly.get("wind_direction_10m", [])[i] if i < len(hourly.get("wind_direction_10m", [])) else 180,
                        "uv_index": hourly.get("uv_index", [])[i] if i < len(hourly.get("uv_index", [])) else 5.0,
                        "precipitation_mm": hourly.get("precipitation", [])[i] if i < len(hourly.get("precipitation", [])) else 0.0,
                        "cloud_cover": hourly.get("cloud_cover", [])[i] if i < len(hourly.get("cloud_cover", [])) else 30
                    })
                
                logger.info(f"Weather forecast: {len(forecast)} hours fetched")
                return forecast
                
        except httpx.TimeoutException:
            logger.warning(f"Timeout fetching weather data (attempt {attempt + 1})")
            if attempt == max_retries - 1:
                logger.error("All weather fetch attempts timed out")
                return None
        except httpx.HTTPError as e:
            logger.warning(f"HTTP error fetching weather: {e} (attempt {attempt + 1})")
            if attempt == max_retries - 1:
                logger.error(f"Failed to fetch weather after {max_retries} attempts")
                return None
        except Exception as e:
            logger.error(f"Unexpected error fetching weather: {e}")
            return None
    
    return None


class WeatherService:
    """Service for fetching weather data."""
    
    OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
    OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self):
        self.openweather_key = settings.openweather_api_key
    
    async def get_current_weather(
        self,
        lat: float,
        lon: float
    ) -> dict:
        """
        Fetch current weather conditions.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            dict: Current weather data
        """
        logger.info(f"Fetching weather for ({lat}, {lon})")
        
        try:
            async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
                # TODO: Choose between OpenWeather (paid) or Open-Meteo (free)
                # OpenWeather example:
                # response = await client.get(
                #     f"{self.OPENWEATHER_URL}/weather",
                #     params={
                #         "lat": lat,
                #         "lon": lon,
                #         "appid": self.openweather_key,
                #         "units": "imperial"
                #     }
                # )
                
                # Open-Meteo (free alternative):
                response = await client.get(
                    self.OPEN_METEO_URL,
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "current": "temperature_2m,relative_humidity_2m,weather_code,"
                                  "wind_speed_10m,wind_direction_10m,cloud_cover",
                        "temperature_unit": "fahrenheit",
                        "wind_speed_unit": "mph"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                # Transform to consistent format
                current = data.get("current", {})
                weather_data = {
                    "temp": current.get("temperature_2m", 70.0),
                    "feels_like": current.get("temperature_2m", 70.0),
                    "humidity": current.get("relative_humidity_2m", 50),
                    "wind_speed": current.get("wind_speed_10m", 5.0),
                    "wind_direction": current.get("wind_direction_10m", 180),
                    "cloud_cover": current.get("cloud_cover", 20),
                    "condition": self._parse_weather_code(current.get("weather_code", 0)),
                    "visibility": 10.0,  # km
                    "source": "Open-Meteo"
                }
                
                logger.info(f"Weather: {weather_data['temp']}°F, {weather_data['condition']}")
                return weather_data
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching weather: {e}")
            return self._get_fallback_weather()
        except Exception as e:
            logger.error(f"Unexpected error fetching weather: {e}")
            return self._get_fallback_weather()
    
    async def get_forecast(
        self,
        lat: float,
        lon: float,
        days: int = 7
    ) -> list[dict]:
        """
        Fetch weather forecast.
        
        Args:
            lat: Latitude
            lon: Longitude
            days: Number of days to forecast
            
        Returns:
            list[dict]: Daily forecast data
        """
        # Use hourly forecast and aggregate to daily
        hourly_forecast = await fetch_weather_forecast(lat, lon, hours=days * 24)
        
        if not hourly_forecast:
            logger.error("Failed to fetch hourly forecast for daily aggregation")
            return []
        
        # Aggregate hourly to daily
        daily_forecast = []
        current_date = None
        day_temps = []
        day_uv = []
        day_precip = []
        
        for hour_data in hourly_forecast:
            timestamp = hour_data["timestamp"]
            date = timestamp.split("T")[0]
            
            if current_date != date:
                # Save previous day if exists
                if current_date and day_temps:
                    daily_forecast.append({
                        "date": current_date,
                        "temp_high": max(day_temps),
                        "temp_low": min(day_temps),
                        "condition": "Partly Cloudy",  # Could improve with weather codes
                        "uv_index": max(day_uv) if day_uv else 5.0,
                        "precipitation_prob": max(day_precip) if day_precip else 0,
                        "wind_speed_max": 10.0
                    })
                
                # Reset for new day
                current_date = date
                day_temps = []
                day_uv = []
                day_precip = []
            
            day_temps.append(hour_data["temp_c"])
            day_uv.append(hour_data["uv_index"])
            day_precip.append(hour_data["precipitation_mm"])
        
        # Add last day
        if current_date and day_temps:
            daily_forecast.append({
                "date": current_date,
                "temp_high": max(day_temps),
                "temp_low": min(day_temps),
                "condition": "Partly Cloudy",
                "uv_index": max(day_uv) if day_uv else 5.0,
                "precipitation_prob": max(day_precip) if day_precip else 0,
                "wind_speed_max": 10.0
            })
        
        return daily_forecast[:days]
    
    def _parse_weather_code(self, code: int) -> str:
        """Convert WMO weather code to readable condition."""
        # WMO Weather interpretation codes
        conditions = {
            0: "Clear",
            1: "Mainly Clear",
            2: "Partly Cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Foggy",
            51: "Light Drizzle",
            61: "Light Rain",
            80: "Rain Showers",
            95: "Thunderstorm"
        }
        return conditions.get(code, "Clear")
    
    def _get_fallback_weather(self) -> dict:
        """Return safe fallback weather data."""
        logger.warning("Using fallback weather data")
        return {
            "temp": 72.0,
            "feels_like": 72.0,
            "humidity": 55,
            "wind_speed": 5.0,
            "wind_direction": 180,
            "cloud_cover": 30,
            "condition": "Partly Cloudy",
            "visibility": 10.0,
            "source": "Fallback"
        }
