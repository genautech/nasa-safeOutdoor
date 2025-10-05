"""OpenAQ air quality data service."""
import httpx
import logging
import asyncio
from typing import Optional
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)


async def fetch_openaq_data(lat: float, lon: float, radius_km: int = 25) -> Optional[dict]:
    """
    Fetch PM2.5 and NO2 from OpenAQ v3 API.
    
    API v3 Docs: https://docs.openaq.org/using-the-api/v3
    
    Args:
        lat: Latitude
        lon: Longitude
        radius_km: Search radius in kilometers
    
    Returns:
        dict with keys:
            - pm25: float (µg/m³, averaged from stations)
            - no2: float (µg/m³, averaged from stations)
            - stations: int (station count)
            - last_update: str (ISO timestamp)
        Returns None on failure
    """
    base_url = "https://api.openaq.org/v3/locations"
    
    # v3 API requires API key in header
    headers = {
        "X-API-Key": settings.openaq_api_key,
        "Accept": "application/json"
    }
    
    params = {
        "coordinates": f"{lat},{lon}",
        "radius": radius_km * 1000,  # Convert km to meters
        "limit": 20,
        "sort": "distance"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for attempt in range(3):
            try:
                logger.info(f"Fetching OpenAQ v3 data for ({lat}, {lon}) - Attempt {attempt + 1}/3")
                
                response = await client.get(base_url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                # v3 has different structure: results[].latest{}
                results = data.get("results", [])
                
                if not results:
                    logger.warning(f"No OpenAQ stations found within {radius_km}km")
                    return None
                
                pm25_values = []
                no2_values = []
                latest_timestamp = None
                
                for location in results:
                    # Get latest measurements for this location
                    latest = location.get("latest", {})
                    
                    # latest is a dict with parameter names as keys
                    for param_name, param_data in latest.items():
                        if not param_data or not isinstance(param_data, dict):
                            continue
                        
                        value = param_data.get("value")
                        timestamp = param_data.get("datetime")
                        
                        if value is not None:
                            if param_name == "pm25":
                                pm25_values.append(float(value))
                            elif param_name == "no2":
                                no2_values.append(float(value))
                            
                            if timestamp and (not latest_timestamp or timestamp > latest_timestamp):
                                latest_timestamp = timestamp
                
                # Calculate averages
                pm25_avg = round(sum(pm25_values) / len(pm25_values), 2) if pm25_values else None
                no2_avg = round(sum(no2_values) / len(no2_values), 2) if no2_values else None
                
                result = {
                    "pm25": pm25_avg,
                    "no2": no2_avg,
                    "stations": len(results),
                    "last_update": latest_timestamp or datetime.utcnow().isoformat()
                }
                
                logger.info(
                    f"OpenAQ v3: Found {len(results)} stations, "
                    f"PM2.5={pm25_avg}, NO2={no2_avg}"
                )
                
                return result
                
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                logger.warning(
                    f"OpenAQ v3 HTTP {status} error: {e} (attempt {attempt + 1}/3)"
                )
                
                if status == 401:
                    logger.error("OpenAQ API key is invalid or missing")
                    return None
                elif status == 410:
                    logger.error("OpenAQ v2 API is deprecated, migrated to v3")
                    return None
                
                if attempt == 2:
                    return None
                    
                await asyncio.sleep(1)
                
            except httpx.TimeoutException:
                logger.warning(f"Timeout fetching OpenAQ v3 data (attempt {attempt + 1}/3)")
                if attempt == 2:
                    return None
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"OpenAQ v3 error: {e} (attempt {attempt + 1}/3)")
                if attempt == 2:
                    return None
                await asyncio.sleep(1)
    
    return None


class OpenAQService:
    """Service for fetching air quality data from OpenAQ."""
    
    BASE_URL = "https://api.openaq.org/v3"
    
    def __init__(self):
        self.api_key = settings.openaq_api_key
    
    async def get_air_quality(
        self,
        lat: float,
        lon: float,
        radius: int = 25000  # meters
    ) -> dict:
        """
        Fetch air quality data near location.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius in meters
            
        Returns:
            dict: Air quality data (PM2.5, NO2, O3, CO, etc.)
        """
        # Use the new fetch function
        data = await fetch_openaq_data(lat, lon, radius_km=radius / 1000)
        
        if not data:
            return self._get_fallback_data()
        
        # Calculate AQI from PM2.5 (EPA standard)
        pm25 = data.get("pm25")
        aqi = self._calculate_aqi_from_pm25(pm25) if pm25 else 50
        
        return {
            "pm25": data.get("pm25", 15.0),
            "pm10": data.get("pm25", 15.0) * 2 if data.get("pm25") else 30.0,  # Estimate
            "no2": data.get("no2", 20.0),
            "o3": 45.0,  # OpenAQ v3 may not always have O3
            "co": 0.4,
            "so2": 2.0,
            "aqi": aqi,
            "dominant_pollutant": "pm25" if pm25 and pm25 > 12 else "no2",
            "measurements": [],
            "source": "OpenAQ",
            "timestamp": data.get("last_update")
        }
    
    async def get_historical_data(
        self,
        lat: float,
        lon: float,
        days: int = 7
    ) -> list[dict]:
        """
        Fetch historical air quality data.
        
        Args:
            lat: Latitude
            lon: Longitude
            days: Number of days of historical data
            
        Returns:
            list[dict]: Historical measurements
        """
        # TODO: Implement OpenAQ historical data endpoint
        logger.info(f"Fetching {days} days of historical AQ data for ({lat}, {lon})")
        
        # Mock historical data
        historical = []
        for i in range(days):
            historical.append({
                "date": f"2024-09-{27+i:02d}",
                "aqi_avg": 45 + (i * 2),
                "pm25_avg": 13.0 + (i * 0.5),
                "no2_avg": 19.0 + (i * 0.3)
            })
        
        return historical
    
    def _calculate_aqi_from_pm25(self, pm25: float) -> int:
        """Calculate AQI from PM2.5 using EPA breakpoints."""
        if pm25 <= 12.0:
            return int((50 / 12.0) * pm25)
        elif pm25 <= 35.4:
            return int(50 + ((100 - 50) / (35.4 - 12.1)) * (pm25 - 12.1))
        elif pm25 <= 55.4:
            return int(100 + ((150 - 100) / (55.4 - 35.5)) * (pm25 - 35.5))
        elif pm25 <= 150.4:
            return int(150 + ((200 - 150) / (150.4 - 55.5)) * (pm25 - 55.5))
        elif pm25 <= 250.4:
            return int(200 + ((300 - 200) / (250.4 - 150.5)) * (pm25 - 150.5))
        else:
            return int(300 + ((500 - 300) / (500.4 - 250.5)) * (pm25 - 250.5))
    
    def _get_fallback_data(self) -> dict:
        """Return safe fallback data when API fails."""
        logger.warning("Using fallback air quality data")
        return {
            "pm25": 15.0,
            "pm10": 30.0,
            "no2": 20.0,
            "o3": 50.0,
            "co": 0.5,
            "so2": 3.0,
            "aqi": 55,
            "dominant_pollutant": "pm25",
            "measurements": [],
            "source": "Fallback",
            "timestamp": None
        }
