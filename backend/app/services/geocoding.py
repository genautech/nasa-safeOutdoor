"""Geocoding service using Mapbox."""
import httpx
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class GeocodingService:
    """Service for geocoding and reverse geocoding with Mapbox."""
    
    BASE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"
    
    def __init__(self):
        self.token = settings.mapbox_token
    
    async def geocode(
        self,
        query: str,
        limit: int = 5
    ) -> list[dict]:
        """
        Forward geocode: convert address/place to coordinates.
        
        Args:
            query: Search query (address, place name, etc.)
            limit: Maximum number of results
            
        Returns:
            list[dict]: List of matching locations with coordinates
        """
        logger.info(f"Geocoding query: '{query}'")
        
        try:
            async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
                # URL encode the query
                response = await client.get(
                    f"{self.BASE_URL}/{query}.json",
                    params={
                        "access_token": self.token,
                        "limit": limit,
                        "types": "place,address,poi"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                # TODO: Transform Mapbox response to simplified format
                results = []
                for feature in data.get("features", []):
                    results.append({
                        "id": feature.get("id"),
                        "name": feature.get("text"),
                        "full_name": feature.get("place_name"),
                        "lon": feature["geometry"]["coordinates"][0],
                        "lat": feature["geometry"]["coordinates"][1],
                        "type": feature.get("place_type", ["unknown"])[0],
                        "context": self._parse_context(feature.get("context", []))
                    })
                
                logger.info(f"Found {len(results)} results for '{query}'")
                return results
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during geocoding: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during geocoding: {e}")
            return []
    
    async def reverse_geocode(
        self,
        lat: float,
        lon: float
    ) -> Optional[dict]:
        """
        Reverse geocode: convert coordinates to address/place name.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            dict: Location information (address, city, country, etc.)
        """
        logger.info(f"Reverse geocoding ({lat}, {lon})")
        
        try:
            async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
                response = await client.get(
                    f"{self.BASE_URL}/{lon},{lat}.json",
                    params={
                        "access_token": self.token,
                        "types": "place,address"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                features = data.get("features", [])
                if not features:
                    return None
                
                feature = features[0]
                context = self._parse_context(feature.get("context", []))
                
                result = {
                    "address": feature.get("place_name"),
                    "place": feature.get("text"),
                    "city": context.get("place"),
                    "region": context.get("region"),
                    "country": context.get("country"),
                    "postcode": context.get("postcode"),
                    "lat": lat,
                    "lon": lon
                }
                
                logger.info(f"Reverse geocoded to: {result['city']}, {result['region']}")
                return result
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during reverse geocoding: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during reverse geocoding: {e}")
            return None
    
    def _parse_context(self, context: list[dict]) -> dict:
        """
        Parse Mapbox context array into structured data.
        
        Args:
            context: Mapbox context array
            
        Returns:
            dict: Structured location context
        """
        parsed = {}
        
        for item in context:
            item_id = item.get("id", "")
            text = item.get("text")
            
            if item_id.startswith("place"):
                parsed["place"] = text
            elif item_id.startswith("region"):
                parsed["region"] = text
            elif item_id.startswith("country"):
                parsed["country"] = text
            elif item_id.startswith("postcode"):
                parsed["postcode"] = text
        
        return parsed
