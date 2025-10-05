"""
NASA TEMPO satellite data integration for real-time NO2 tropospheric measurements.

TEMPO (Tropospheric Emissions: Monitoring of Pollution) is NASA's first Earth
Venture Instrument mission. It provides hourly daytime observations of air quality
across North America from geostationary orbit.

Coverage: North America (15°N to 70°N, 170°W to 40°W)
Resolution: ~10km spatial, hourly temporal
Data: NO2 tropospheric column density
"""
import httpx
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# TEMPO coverage bounds
TEMPO_LAT_MIN, TEMPO_LAT_MAX = 15.0, 70.0
TEMPO_LON_MIN, TEMPO_LON_MAX = -170.0, -40.0


async def fetch_tempo_no2(lat: float, lon: float) -> Optional[Dict]:
    """
    Fetch NO2 tropospheric column density from NASA TEMPO satellite.
    
    TEMPO provides hourly NO2 measurements across North America.
    Resolution: ~10km spatial, hourly temporal
    Coverage: North America (15°N to 70°N, 170°W to 40°W)
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
    
    Returns:
        dict with NO2 data or None if unavailable:
        {
            "no2_ppb": float,  # NO2 concentration in ppb
            "no2_column": float,  # NO2 column density in molecules/cm²
            "quality_flag": int,  # Data quality (0=good, 1=questionable)
            "timestamp": str,  # ISO 8601 timestamp
            "source": "NASA TEMPO"
        }
    """
    
    # Check if location is in TEMPO coverage area
    if not (TEMPO_LAT_MIN <= lat <= TEMPO_LAT_MAX and TEMPO_LON_MIN <= lon <= TEMPO_LON_MAX):
        logger.info(f"Location ({lat:.4f}, {lon:.4f}) outside TEMPO coverage (North America only)")
        return None
    
    logger.info(f"Attempting to fetch TEMPO NO2 data for ({lat:.4f}, {lon:.4f})")
    
    # Try CMR API approach first
    result = await _fetch_via_cmr(lat, lon)
    if result:
        return result
    
    # Try GIBS visualization service as fallback
    result = await _fetch_via_gibs(lat, lon)
    if result:
        return result
    
    # All methods failed
    logger.warning("All TEMPO data retrieval methods failed, falling back to OpenAQ")
    return None


async def _fetch_via_cmr(lat: float, lon: float) -> Optional[Dict]:
    """
    Fetch TEMPO data via NASA Common Metadata Repository (CMR) API.
    
    This method queries for TEMPO granules and attempts to extract NO2 values.
    Note: Full implementation requires NASA EarthData credentials and netCDF processing.
    """
    cmr_url = "https://cmr.earthdata.nasa.gov/search/granules.json"
    
    try:
        # Get temporal window (last 24 hours)
        today = datetime.utcnow()
        yesterday = today - timedelta(days=1)
        
        # Query CMR for TEMPO NO2 granules
        params = {
            "collection_concept_id": "C2832095828-LARC_CLOUD",  # TEMPO L2 NO2 product
            "temporal": f"{yesterday.strftime('%Y-%m-%dT%H:%M:%SZ')},{today.strftime('%Y-%m-%dT%H:%M:%SZ')}",
            "bounding_box": f"{lon-0.5},{lat-0.5},{lon+0.5},{lat+0.5}",
            "page_size": 5,
            "sort_key": "-start_date"
        }
        
        logger.debug(f"Querying CMR with params: {params}")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(cmr_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            entries = data.get("feed", {}).get("entry", [])
            if not entries:
                logger.info("No recent TEMPO granules found in CMR for this location")
                return None
            
            logger.info(f"Found {len(entries)} TEMPO granules in CMR")
            
            # NOTE: Actual data extraction requires:
            # 1. Download netCDF file from granule URL
            # 2. Authenticate with NASA EarthData
            # 3. Parse netCDF and extract pixel value at lat/lon
            # 4. Apply quality flags and cloud screening
            
            # For now, log the availability and return None
            logger.warning(
                "TEMPO granules found but data extraction requires NASA EarthData "
                "authentication and netCDF processing (not implemented for real-time API)"
            )
            
            return None
            
    except httpx.TimeoutException:
        logger.warning("CMR API timeout")
        return None
    except httpx.HTTPStatusError as e:
        logger.warning(f"CMR API HTTP error: {e.response.status_code}")
        return None
    except Exception as e:
        logger.error(f"CMR API error: {e}")
        return None


async def _fetch_via_gibs(lat: float, lon: float) -> Optional[Dict]:
    """
    Fetch TEMPO data via NASA GIBS (Global Imagery Browse Services).
    
    GIBS provides visualization-ready imagery but not raw data values.
    This method attempts to extract approximate NO2 values from GIBS layers.
    
    Note: GIBS is designed for visualization, not quantitative data extraction.
    Results are approximate and should be validated against ground stations.
    """
    gibs_url = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"
    
    try:
        # GetFeatureInfo request for TEMPO NO2 layer
        params = {
            "SERVICE": "WMS",
            "REQUEST": "GetFeatureInfo",
            "VERSION": "1.3.0",
            "LAYERS": "TEMPO_L2_NO2_Vertical_Column",
            "QUERY_LAYERS": "TEMPO_L2_NO2_Vertical_Column",
            "STYLES": "",
            "FORMAT": "image/png",
            "TRANSPARENT": "true",
            "CRS": "EPSG:4326",
            "BBOX": f"{lat-0.05},{lon-0.05},{lat+0.05},{lon+0.05}",
            "HEIGHT": 256,
            "WIDTH": 256,
            "I": 128,  # X pixel
            "J": 128,  # Y pixel
            "INFO_FORMAT": "application/json",
            "TIME": datetime.utcnow().strftime('%Y-%m-%d')
        }
        
        logger.debug(f"Querying GIBS with params: {params}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(gibs_url, params=params)
            
            if response.status_code != 200:
                logger.info(f"GIBS API returned {response.status_code} (no data available)")
                return None
            
            # Try to parse JSON response
            try:
                data = response.json()
                logger.debug(f"GIBS response: {data}")
                
                # GIBS responses vary by layer - attempt to extract NO2 value
                # This is highly dependent on GIBS layer configuration
                if "features" in data and len(data["features"]) > 0:
                    feature = data["features"][0]
                    properties = feature.get("properties", {})
                    
                    # Look for NO2-related fields
                    no2_column = properties.get("no2_column") or properties.get("value")
                    
                    if no2_column:
                        # Convert column density to ppb (approximate)
                        # 1e15 molecules/cm² ≈ 10 ppb (rough conversion)
                        no2_ppb = no2_column / 1e15 * 10
                        
                        logger.info(f"GIBS TEMPO NO2: {no2_ppb:.2f} ppb (from column: {no2_column:.2e})")
                        
                        return {
                            "no2_ppb": round(no2_ppb, 2),
                    "no2_column": no2_column,
                            "quality_flag": 0,
                            "timestamp": datetime.utcnow().isoformat(),
                            "source": "NASA TEMPO (GIBS)"
                        }
                
                logger.info("GIBS returned data but NO2 value not found in response")
                return None
                
            except ValueError:
                # Response is not JSON (probably image data)
                logger.info("GIBS returned image data, not JSON (layer may not support GetFeatureInfo)")
                return None
            
    except httpx.TimeoutException:
        logger.warning("GIBS API timeout")
        return None
    except httpx.HTTPStatusError as e:
        logger.warning(f"GIBS API HTTP error: {e.response.status_code}")
                return None
        except Exception as e:
        logger.error(f"GIBS API error: {e}")
    return None


def is_tempo_coverage(lat: float, lon: float) -> bool:
    """
    Check if a location is within TEMPO satellite coverage area.
        
        Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
            
        Returns:
        True if location is covered by TEMPO, False otherwise
    """
    return (TEMPO_LAT_MIN <= lat <= TEMPO_LAT_MAX and 
            TEMPO_LON_MIN <= lon <= TEMPO_LON_MAX)


# Export coverage bounds for use in other modules
__all__ = [
    'fetch_tempo_no2',
    'is_tempo_coverage',
    'TEMPO_LAT_MIN',
    'TEMPO_LAT_MAX',
    'TEMPO_LON_MIN',
    'TEMPO_LON_MAX'
]