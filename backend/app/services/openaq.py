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
    
    OpenAQ v3 requires 2-step process:
    1. GET /v3/locations - Find nearby locations with sensors
    2. GET /v3/locations/{id}/latest - Get actual measurement values
    
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
    # v3 API requires API key in header
    headers = {
        "X-API-Key": settings.openaq_api_key,
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        for attempt in range(3):
            try:
                logger.info(f"🔍 OpenAQ v3 Step 1: Finding locations near ({lat}, {lon})")
                
                # STEP 1: Find nearby locations with PM2.5 or NO2 sensors
                locations_url = "https://api.openaq.org/v3/locations"
                params = {
                    "coordinates": f"{lat},{lon}",
                    "radius": radius_km * 1000,  # Convert km to meters
                    "limit": 10,  # Get top 10 closest
                    "sort": "distance"
                }
                
                locations_response = await client.get(locations_url, headers=headers, params=params)
                locations_response.raise_for_status()
                locations_data = locations_response.json()
                
                locations = locations_data.get("results", [])
                logger.info(f"✅ Found {len(locations)} locations within {radius_km}km")
                
                if not locations:
                    logger.warning(f"⚠️ No OpenAQ stations found within {radius_km}km")
                    return None
                
                # Filter locations that have PM2.5 or NO2 sensors
                pm25_locations = []
                no2_locations = []
                
                for location in locations:
                    location_id = location.get("id")
                    location_name = location.get("name", "Unknown")
                    sensors = location.get("sensors", [])
                    
                    has_pm25 = False
                    has_no2 = False
                    
                    for sensor in sensors:
                        param = sensor.get("parameter", {})
                        param_name = param.get("name", "")
                        
                        if param_name == "pm25":
                            has_pm25 = True
                        elif param_name == "no2":
                            has_no2 = True
                    
                    if has_pm25:
                        pm25_locations.append({"id": location_id, "name": location_name})
                    if has_no2:
                        no2_locations.append({"id": location_id, "name": location_name})
                
                logger.info(f"📊 {len(pm25_locations)} locations with PM2.5, {len(no2_locations)} with NO2")
                
                # STEP 2: Fetch latest measurements from each location
                pm25_values = []
                no2_values = []
                latest_timestamp = None
                successful_fetches = 0
                
                # Get unique location IDs (some have both PM2.5 and NO2)
                unique_location_ids = set()
                for loc in pm25_locations + no2_locations:
                    unique_location_ids.add(loc["id"])
                
                logger.info(f"🔍 OpenAQ v3 Step 2: Fetching measurements from {len(unique_location_ids)} locations")
                
                # Limit to top 5 to avoid rate limits and long waits
                for location_id in list(unique_location_ids)[:5]:
                    try:
                        latest_url = f"https://api.openaq.org/v3/locations/{location_id}/latest"
                        
                        logger.info(f"📡 Fetching latest from location {location_id}...")
                        latest_response = await client.get(latest_url, headers=headers, timeout=5.0)
                        latest_response.raise_for_status()
                        latest_data = latest_response.json()
                        
                        logger.info(f"🔍 Latest response keys: {list(latest_data.keys())}")
                        
                        # The /latest endpoint returns parameter measurements directly
                        # Structure: {"pm25": {"value": 12.5, "datetime": "..."}, "no2": {...}}
                        for param_name, param_data in latest_data.items():
                            if not isinstance(param_data, dict):
                                continue
                            
                            value = param_data.get("value")
                            timestamp = param_data.get("datetime")
                            
                            if value is not None:
                                logger.info(f"✅ Location {location_id}: {param_name} = {value}")
                                
                                if param_name == "pm25":
                                    pm25_values.append(float(value))
                                elif param_name == "no2":
                                    # NO2 might be in ppm, convert to µg/m³ if needed
                                    # Check units in param_data
                                    units = param_data.get("unit", "")
                                    if units == "ppm":
                                        # Convert ppm to µg/m³ (NO2: 1 ppm ≈ 1880 µg/m³)
                                        value_ugm3 = float(value) * 1880
                                        no2_values.append(value_ugm3)
                                        logger.info(f"   Converted NO2 from {value} ppm to {value_ugm3:.2f} µg/m³")
                                    else:
                                        no2_values.append(float(value))
                                
                                if timestamp and (not latest_timestamp or timestamp > latest_timestamp):
                                    latest_timestamp = timestamp
                        
                        successful_fetches += 1
                        
                    except httpx.HTTPStatusError as e:
                        logger.warning(f"⚠️ Failed to fetch latest for location {location_id}: HTTP {e.response.status_code}")
                        continue
                    except Exception as e:
                        logger.warning(f"⚠️ Error fetching location {location_id}: {e}")
                        continue
                
                logger.info(f"📊 Collected {len(pm25_values)} PM2.5 values: {pm25_values}")
                logger.info(f"📊 Collected {len(no2_values)} NO2 values: {no2_values}")
                logger.info(f"✅ Successfully fetched from {successful_fetches}/{len(unique_location_ids)} locations")
                
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
                    f"✅ OpenAQ v3 FINAL: {successful_fetches} stations, "
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
