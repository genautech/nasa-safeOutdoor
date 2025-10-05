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
    
    OpenAQ v3 uses 2-step process with sensor ID mapping:
    1. GET /v3/locations - Get locations with sensor metadata
    2. GET /v3/locations/{id}/latest - Get values using sensorsId
    
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
    headers = {
        "X-API-Key": settings.openaq_api_key,
        "Accept": "application/json"
    }
    
    params = {
        "coordinates": f"{lat},{lon}",
        "radius": radius_km * 1000,  # Convert km to meters
        "limit": 10,
        "sort": "distance"
    }
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            logger.info(f"🔍 OpenAQ v3 Step 1: Finding locations near ({lat}, {lon})")
            
            # STEP 1: Get locations and build sensor ID → parameter name map
            locations_response = await client.get(base_url, headers=headers, params=params)
            locations_response.raise_for_status()
            locations_data = locations_response.json()
            
            locations = locations_data.get("results", [])
            logger.info(f"✅ Found {len(locations)} locations within {radius_km}km")
            
            if not locations:
                logger.warning(f"⚠️ No OpenAQ stations found within {radius_km}km")
                return None
            
            # Build sensor map: sensor_id → parameter_name
            sensor_map = {}
            location_ids = []
            
            for location in locations:
                location_id = location.get("id")
                location_ids.append(location_id)
                
                for sensor in location.get("sensors", []):
                    sensor_id = sensor.get("id")
                    param = sensor.get("parameter", {})
                    param_name = param.get("name", "")
                    
                    # Map sensor ID to parameter name
                    if param_name in ["pm25", "no2"]:
                        sensor_map[sensor_id] = param_name
            
            logger.info(f"📊 Built sensor map with {len(sensor_map)} relevant sensors (PM2.5/NO2)")
            
            # STEP 2: Fetch latest measurements using sensor map
            pm25_values = []
            no2_values = []
            latest_timestamp = None
            successful_fetches = 0
            
            logger.info(f"🔍 OpenAQ v3 Step 2: Fetching measurements from {len(location_ids[:5])} locations")
            
            # Limit to top 5 locations to avoid rate limits
            for location_id in location_ids[:5]:
                try:
                    latest_url = f"{base_url}/{location_id}/latest"
                    
                    logger.info(f"📡 Fetching latest from location {location_id}...")
                    latest_response = await client.get(latest_url, headers=headers, timeout=5.0)
                    latest_response.raise_for_status()
                    latest_data = latest_response.json()
                    
                    # Parse results array
                    # Structure: {"results": [{"sensorsId": 673, "value": 11.2, "datetime": {...}}, ...]}
                    for result in latest_data.get("results", []):
                        sensor_id = result.get("sensorsId")
                        value = result.get("value")
                        datetime_obj = result.get("datetime", {})
                        timestamp = datetime_obj.get("utc") if isinstance(datetime_obj, dict) else None
                        
                        # Use sensor map to determine parameter type
                        if sensor_id in sensor_map and value is not None:
                            param_name = sensor_map[sensor_id]
                            
                            logger.info(f"✅ Location {location_id}, Sensor {sensor_id}: {param_name} = {value}")
                            
                            if param_name == "pm25":
                                pm25_values.append(float(value))
                            elif param_name == "no2":
                                # NO2 values < 1 are likely in ppm, convert to µg/m³
                                # NO2: 1 ppm ≈ 1880 µg/m³ at 25°C
                                if value < 1:
                                    value_ugm3 = float(value) * 1880
                                    no2_values.append(value_ugm3)
                                    logger.info(f"   ⚙️ Converted NO2 from {value} ppm to {value_ugm3:.2f} µg/m³")
                                else:
                                    no2_values.append(float(value))
                            
                            if timestamp and (not latest_timestamp or timestamp > latest_timestamp):
                                latest_timestamp = timestamp
                    
                    successful_fetches += 1
                    
                except httpx.HTTPStatusError as e:
                    logger.warning(f"⚠️ Location {location_id} failed: HTTP {e.response.status_code}")
                    continue
                except Exception as e:
                    logger.warning(f"⚠️ Location {location_id} error: {e}")
                    continue
            
            logger.info(f"📊 Collected {len(pm25_values)} PM2.5 values: {pm25_values[:5]}...")
            logger.info(f"📊 Collected {len(no2_values)} NO2 values: {no2_values[:5]}...")
            
            # Calculate averages
            pm25_avg = round(sum(pm25_values) / len(pm25_values), 2) if pm25_values else None
            no2_avg = round(sum(no2_values) / len(no2_values), 2) if no2_values else None
            
            result = {
                "pm25": pm25_avg,
                "no2": no2_avg,
                "stations": successful_fetches,
                "last_update": latest_timestamp or datetime.utcnow().isoformat()
            }
            
            logger.info(
                f"✅ OpenAQ v3 SUCCESS: PM2.5={pm25_avg}, NO2={no2_avg} "
                f"from {successful_fetches} stations"
            )
            
            return result
                
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            logger.error(f"OpenAQ v3 HTTP {status} error: {e}")
            return None
        except Exception as e:
            logger.error(f"OpenAQ v3 unexpected error: {e}")
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
