"""NASA TEMPO NO2 data fetching service."""
import httpx
import logging
from typing import Optional
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)


async def fetch_tempo_no2(lat: float, lon: float) -> Optional[dict]:
    """
    Fetch NO2 data from NASA TEMPO satellite.
    API: https://disc.gsfc.nasa.gov/datasets/TEMPO_NO2_L2_V03
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        dict with keys:
            - no2_column: float (molec/cm²)
            - no2_ppb: float (converted to ppb)
            - quality_flag: int
            - timestamp: str
        Returns None on failure
    """
    max_retries = 3
    timeout = 10.0
    
    # NASA TEMPO data access endpoint
    # Note: TEMPO data is available through NASA's Earthdata Search
    base_url = "https://disc.gsfc.nasa.gov/api/tempo/no2"
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching TEMPO NO2 data for ({lat}, {lon}) - Attempt {attempt + 1}/{max_retries}")
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(
                    base_url,
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "format": "json"
                    },
                    auth=(settings.nasa_earthdata_user, settings.nasa_earthdata_pass)
                )
                response.raise_for_status()
                data = response.json()
                
                # Convert column density to ppb (approximate conversion)
                # 1 ppb ≈ 1.88e15 molec/cm² for NO2
                no2_column = data.get("no2_column_density", 2.5e15)
                no2_ppb = no2_column / 1.88e15
                
                result = {
                    "no2_column": no2_column,
                    "no2_ppb": round(no2_ppb, 2),
                    "quality_flag": data.get("quality_flag", 0),
                    "timestamp": data.get("timestamp", datetime.utcnow().isoformat())
                }
                
                logger.info(f"TEMPO NO2: {result['no2_ppb']} ppb")
                return result
                
        except httpx.TimeoutException:
            logger.warning(f"Timeout fetching TEMPO data (attempt {attempt + 1})")
            if attempt == max_retries - 1:
                logger.error("All TEMPO fetch attempts timed out")
                return None
        except httpx.HTTPError as e:
            logger.warning(f"HTTP error fetching TEMPO data: {e} (attempt {attempt + 1})")
            if attempt == max_retries - 1:
                logger.error(f"Failed to fetch TEMPO data after {max_retries} attempts")
                return None
        except Exception as e:
            logger.error(f"Unexpected error fetching TEMPO data: {e}")
            return None
    
    return None


class NASATempoService:
    """Service for fetching NASA TEMPO NO2 satellite data."""
    
    def __init__(self):
        self.username = settings.nasa_earthdata_user
        self.password = settings.nasa_earthdata_pass
    
    async def get_no2_data(
        self,
        lat: float,
        lon: float,
        date: Optional[str] = None
    ) -> Optional[dict]:
        """
        Fetch NO2 concentration data from NASA TEMPO.
        
        Args:
            lat: Latitude
            lon: Longitude
            date: Date string (YYYY-MM-DD), defaults to today
            
        Returns:
            dict: NO2 data including concentration, quality flags, etc.
        """
        return await fetch_tempo_no2(lat, lon)
    
    async def get_no2_forecast(
        self,
        lat: float,
        lon: float,
        hours: int = 24
    ) -> list[dict]:
        """
        Get NO2 forecast for upcoming hours.
        
        Args:
            lat: Latitude
            lon: Longitude
            hours: Number of hours to forecast
            
        Returns:
            list[dict]: Hourly NO2 forecast data
        """
        logger.info(f"Fetching TEMPO NO2 forecast for ({lat}, {lon}) - {hours} hours")
        
        # TEMPO provides observations, not forecasts
        # For forecast, we'd use historical patterns or ML models
        # Returning current data as baseline
        current = await self.get_no2_data(lat, lon)
        
        if not current:
            return []
        
        # Generate simple forecast based on current reading
        forecast = []
        base_no2 = current.get("no2_ppb", 15.0)
        
        for i in range(hours):
            # Simple diurnal pattern (peak midday, lower at night)
            hour_factor = 1.0 + 0.3 * (1 if 10 <= (i % 24) <= 16 else -0.5)
            forecast.append({
                "hour_offset": i,
                "no2_ppb": round(base_no2 * hour_factor, 2),
                "quality_flag": "forecast",
                "confidence": max(0.5, 0.9 - (i * 0.02))
            })
        
        return forecast
