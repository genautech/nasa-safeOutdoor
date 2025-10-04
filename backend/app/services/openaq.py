"""OpenAQ air quality data service."""
import httpx
import logging
from typing import Optional
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)


async def fetch_openaq_data(lat: float, lon: float, radius_km: int = 25) -> Optional[dict]:
    """
    Fetch PM2.5 and NO2 from nearby OpenAQ stations.
    API: https://docs.openaq.org/
    
    Args:
        lat: Latitude
        lon: Longitude
        radius_km: Search radius in kilometers
    
    Returns:
        dict with keys:
            - pm25: float (µg/m³, averaged from stations)
            - no2: float (ppb)
            - stations: int
            - last_update: str
        Returns None on failure
    """
    max_retries = 3
    timeout = 10.0
    base_url = "https://api.openaq.org/v2/latest"
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching OpenAQ data for ({lat}, {lon}) - Attempt {attempt + 1}/{max_retries}")
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                headers = {"X-API-Key": settings.openaq_api_key} if settings.openaq_api_key else {}
                
                response = await client.get(
                    base_url,
                    params={
                        "coordinates": f"{lat},{lon}",
                        "radius": radius_km * 1000,  # Convert to meters
                        "limit": 100,
                        "parameter": "pm25,no2"
                    },
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                
                results = data.get("results", [])
                if not results:
                    logger.warning(f"No OpenAQ stations found within {radius_km}km")
                    return None
                
                # Aggregate measurements
                pm25_values = []
                no2_values = []
                station_ids = set()
                latest_timestamp = None
                
                for result in results:
                    station_ids.add(result.get("location"))
                    
                    for measurement in result.get("measurements", []):
                        param = measurement.get("parameter")
                        value = measurement.get("value")
                        timestamp = measurement.get("lastUpdated")
                        
                        if value is not None:
                            if param == "pm25":
                                pm25_values.append(value)
                            elif param == "no2":
                                no2_values.append(value)
                            
                            if timestamp and (not latest_timestamp or timestamp > latest_timestamp):
                                latest_timestamp = timestamp
                
                result = {
                    "pm25": round(sum(pm25_values) / len(pm25_values), 2) if pm25_values else None,
                    "no2": round(sum(no2_values) / len(no2_values), 2) if no2_values else None,
                    "stations": len(station_ids),
                    "last_update": latest_timestamp or datetime.utcnow().isoformat()
                }
                
                logger.info(f"OpenAQ: PM2.5={result['pm25']}, NO2={result['no2']}, stations={result['stations']}")
                return result
                
        except httpx.TimeoutException:
            logger.warning(f"Timeout fetching OpenAQ data (attempt {attempt + 1})")
            if attempt == max_retries - 1:
                logger.error("All OpenAQ fetch attempts timed out")
                return None
        except httpx.HTTPError as e:
            logger.warning(f"HTTP error fetching OpenAQ data: {e} (attempt {attempt + 1})")
            if attempt == max_retries - 1:
                logger.error(f"Failed to fetch OpenAQ data after {max_retries} attempts")
                return None
        except Exception as e:
            logger.error(f"Unexpected error fetching OpenAQ data: {e}")
            return None
    
    return None


class OpenAQService:
    """Service for fetching air quality data from OpenAQ."""
    
    BASE_URL = "https://api.openaq.org/v2"
    
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
            "o3": 45.0,  # OpenAQ v2 may not always have O3
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
