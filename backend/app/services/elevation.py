"""Elevation and terrain data service."""
import httpx
import logging
from typing import Optional
import math

logger = logging.getLogger(__name__)


async def fetch_elevation(lat: float, lon: float) -> Optional[dict]:
    """
    Get elevation and terrain data.
    API: Open-Elevation or Mapbox Tilequery
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        dict with keys:
            - elevation_m: float
            - slope_degrees: float (if available)
            - terrain_type: str
        Returns None on failure
    """
    max_retries = 3
    timeout = 10.0
    
    # Try Open-Elevation first (free, no API key needed)
    base_url = "https://api.open-elevation.com/api/v1/lookup"
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching elevation for ({lat}, {lon}) - Attempt {attempt + 1}/{max_retries}")
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(
                    base_url,
                    params={"locations": f"{lat},{lon}"}
                )
                response.raise_for_status()
                data = response.json()
                
                results = data.get("results", [])
                if not results:
                    logger.warning("No elevation data in response")
                    return None
                
                elevation_m = results[0].get("elevation", 0)
                
                # Determine terrain type based on elevation
                if elevation_m < 300:
                    terrain_type = "lowland"
                elif elevation_m < 1000:
                    terrain_type = "hills"
                elif elevation_m < 2500:
                    terrain_type = "mountains"
                else:
                    terrain_type = "high_mountains"
                
                result = {
                    "elevation_m": round(elevation_m, 1),
                    "slope_degrees": None,  # Would require multiple points to calculate
                    "terrain_type": terrain_type
                }
                
                logger.info(f"Elevation: {result['elevation_m']}m ({result['terrain_type']})")
                return result
                
        except httpx.TimeoutException:
            logger.warning(f"Timeout fetching elevation (attempt {attempt + 1})")
            if attempt == max_retries - 1:
                logger.error("All elevation fetch attempts timed out")
                return None
        except httpx.HTTPError as e:
            logger.warning(f"HTTP error fetching elevation: {e} (attempt {attempt + 1})")
            # Try USGS as fallback on last attempt
            if attempt == max_retries - 1:
                return await _fetch_elevation_usgs(lat, lon)
        except Exception as e:
            logger.error(f"Unexpected error fetching elevation: {e}")
            return None
    
    return None


async def _fetch_elevation_usgs(lat: float, lon: float) -> Optional[dict]:
    """Fallback to USGS Elevation Point Query Service."""
    try:
        logger.info("Trying USGS elevation service as fallback")
        base_url = "https://epqs.nationalmap.gov/v1/json"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                base_url,
                params={"x": lon, "y": lat, "units": "Meters"}
            )
            response.raise_for_status()
            data = response.json()
            
            elevation_m = data.get("value", 0)
            
            if elevation_m < 300:
                terrain_type = "lowland"
            elif elevation_m < 1000:
                terrain_type = "hills"
            elif elevation_m < 2500:
                terrain_type = "mountains"
            else:
                terrain_type = "high_mountains"
            
            result = {
                "elevation_m": round(elevation_m, 1),
                "slope_degrees": None,
                "terrain_type": terrain_type
            }
            
            logger.info(f"USGS Elevation: {result['elevation_m']}m")
            return result
            
    except Exception as e:
        logger.error(f"USGS elevation fetch failed: {e}")
        return None


class ElevationService:
    """Service for fetching elevation and terrain data."""
    
    # Open-Elevation API (free, open-source)
    OPEN_ELEVATION_URL = "https://api.open-elevation.com/api/v1/lookup"
    
    # Alternative: USGS Elevation Point Query Service
    USGS_URL = "https://epqs.nationalmap.gov/v1/json"
    
    async def get_elevation(
        self,
        lat: float,
        lon: float
    ) -> dict:
        """
        Fetch elevation data for location.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            dict: Elevation data including altitude, terrain info
        """
        # Use the new fetch function
        data = await fetch_elevation(lat, lon)
        
        if not data:
            return self._get_fallback_elevation()
        
        elevation_m = data["elevation_m"]
        elevation_ft = elevation_m * 3.28084
        
        return {
            "elevation_m": elevation_m,
            "elevation_ft": round(elevation_ft, 1),
            "altitude_effect": self._calculate_altitude_effect(elevation_m),
            "terrain_type": data["terrain_type"],
            "slope_degrees": data.get("slope_degrees"),
            "source": "Open-Elevation"
        }
    
    async def get_terrain_profile(
        self,
        waypoints: list[tuple[float, float]]
    ) -> list[dict]:
        """
        Get elevation profile along a route.
        
        Args:
            waypoints: List of (lat, lon) tuples
            
        Returns:
            list[dict]: Elevation profile data points
        """
        logger.info(f"Fetching terrain profile for {len(waypoints)} waypoints")
        
        # TODO: Implement batch elevation query for route
        profile = []
        
        for i, (lat, lon) in enumerate(waypoints):
            elevation_data = await self.get_elevation(lat, lon)
            profile.append({
                "point": i,
                "lat": lat,
                "lon": lon,
                **elevation_data
            })
        
        return profile
    
    def _calculate_altitude_effect(self, elevation_m: float) -> str:
        """
        Determine altitude effect on human physiology.
        
        Args:
            elevation_m: Elevation in meters
            
        Returns:
            str: Altitude effect category
        """
        if elevation_m < 1500:
            return "none"
        elif elevation_m < 2500:
            return "minimal"
        elif elevation_m < 3500:
            return "moderate"
        else:
            return "significant"
    
    def _get_fallback_elevation(self) -> dict:
        """Return fallback elevation data."""
        logger.warning("Using fallback elevation data")
        return {
            "elevation_m": 100,
            "elevation_ft": 328,
            "altitude_effect": "none",
            "source": "Fallback"
        }
