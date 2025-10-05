"""
NASA TEMPO satellite data integration using earthaccess streaming.

TEMPO (Tropospheric Emissions: Monitoring of Pollution) provides hourly NO2
measurements across North America. This implementation uses earthaccess to 
stream data without downloading entire 800MB files.

Coverage: North America (15°N to 70°N, 170°W to 40°W)
Resolution: ~10km spatial, hourly temporal
Protocol: earthaccess streaming (efficient remote data access)
Data Transfer: Streaming only needed pixels

Authentication: Requires NASA EarthData Bearer token
"""
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
import asyncio
import os
from app.config import settings

logger = logging.getLogger(__name__)


class TEMPOService:
    """NASA TEMPO satellite data service with earthaccess streaming."""
    
    # TEMPO dataset info
    SHORT_NAME = "TEMPO_NO2_L3"
    VERSION = "V04"
    
    # Coverage bounds
    LAT_MIN, LAT_MAX = 15.0, 70.0
    LON_MIN, LON_MAX = -170.0, -40.0
    
    @staticmethod
    def is_in_coverage(lat: float, lon: float) -> bool:
        """
        Check if location is within TEMPO satellite coverage.
        
        Args:
            lat: Latitude (-90 to 90)
            lon: Longitude (-180 to 180)
        
        Returns:
            True if in North America coverage area
        """
        return (TEMPOService.LAT_MIN <= lat <= TEMPOService.LAT_MAX and 
                TEMPOService.LON_MIN <= lon <= TEMPOService.LON_MAX)
    
    @staticmethod
    async def find_and_extract_no2(lat: float, lon: float) -> Optional[Dict]:
        """
        Find latest TEMPO granule and extract NO2 value using earthaccess streaming.
        
        Uses earthaccess to:
        1. Search for granules with bounding box
        2. Stream data (no 800MB download!)
        3. Extract specific pixel
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            dict with NO2 value in ppb, quality flag, and age, or None if failed
        """
        try:
            import earthaccess
            import xarray as xr
            import numpy as np
            
            # Set Bearer token for earthaccess
            os.environ['EARTHDATA_TOKEN'] = settings.nasa_earthdata_token
            
            # Authenticate
            loop = asyncio.get_event_loop()
            
            def search_and_extract():
                # Login to NASA Earthdata
                auth = earthaccess.login(strategy="environment", persist=False)
                if not auth.authenticated:
                    logger.error("❌ earthaccess authentication failed")
                    return None
                
                # Create bounding box around point (~2km radius for precise data)
                delta = 0.02  # ~2km
                bbox = (lon - delta, lat - delta, lon + delta, lat + delta)
                
                # Search last 24 hours
                now = datetime.utcnow()
                start = now - timedelta(hours=24)
                
                logger.debug(f"🔍 Searching TEMPO granules at ({lat:.4f}, {lon:.4f}) bbox={bbox}")
                
                # Search for TEMPO NO2 L3 data
                results = earthaccess.search_data(
                    short_name=TEMPOService.SHORT_NAME,
                    version=TEMPOService.VERSION,
                    temporal=(start.isoformat(), now.isoformat()),
                    bounding_box=bbox,
                    count=1
                )
                
                if not results:
                    logger.info("No recent TEMPO granules found")
                    return None
                
                logger.info(f"✅ Found {len(results)} TEMPO granule(s)")
                
                # Open first granule with streaming (NO DOWNLOAD!)
                logger.debug(f"📡 Opening TEMPO granule with streaming...")
                fileset = earthaccess.open(results[0:1])
                
                if not fileset:
                    logger.error("❌ Failed to open TEMPO granule")
                    return None
                
                # Open with xarray
                ds = xr.open_dataset(fileset[0], group='product', decode_times=False)
                logger.debug(f"📊 Dataset opened, variables: {list(ds.data_vars.keys())}")
                
                # Get coordinate arrays
                lats = ds['latitude'].values
                lons = ds['longitude'].values
                
                # Find nearest pixel
                lat_idx = int(np.abs(lats - lat).argmin())
                lon_idx = int(np.abs(lons - lon).argmin())
                
                actual_lat = float(lats[lat_idx])
                actual_lon = float(lons[lon_idx])
                
                logger.info(f"📍 Nearest pixel: [{lat_idx}, {lon_idx}] → ({actual_lat:.4f}, {actual_lon:.4f})")
                
                # Extract NO2 value
                no2_var_names = [
                    'vertical_column_troposphere',
                    'tropospheric_vertical_column',
                    'no2_column',
                    'column_amount_no2_troposphere'
                ]
                
                no2_value = None
                for var_name in no2_var_names:
                    if var_name in ds.data_vars:
                        no2_value = float(ds[var_name].values[lat_idx, lon_idx])
                        logger.debug(f"✅ Found NO2 variable: {var_name}")
                        break
                
                if no2_value is None:
                    logger.error(f"❌ NO2 variable not found in dataset")
                    return None
                
                # Check quality flag if available
                quality_flag = 0
                if 'quality_flag' in ds.data_vars:
                    quality_flag = int(ds['quality_flag'].values[lat_idx, lon_idx])
                
                # Convert from molecules/cm² to ppb (approximate)
                # TEMPO gives column density, convert to mixing ratio
                no2_ppb = no2_value * 1e-15 * 2.69e10  # Rough conversion
                
                # Calculate data age
                if 'time' in ds.data_vars:
                    data_time = ds['time'].values[0]
                    age_hours = (now - datetime.utcfromtimestamp(data_time)).total_seconds() / 3600
                else:
                    age_hours = 0.0
                
                logger.info(f"✅ Extracted NO2: {no2_ppb:.2f} ppb (quality={quality_flag}, age={age_hours:.1f}h)")
                
                return {
                    "no2_ppb": no2_ppb,
                    "quality_flag": quality_flag,
                    "age_hours": age_hours,
                    "pixel_lat": actual_lat,
                    "pixel_lon": actual_lon
                }
            
            # Run blocking earthaccess code in executor
            result = await loop.run_in_executor(None, search_and_extract)
            return result
            
        except ImportError as e:
            logger.error(f"❌ Required libraries not installed: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ TEMPO extraction failed: {type(e).__name__}: {e}")
            return None


async def fetch_tempo_no2(lat: float, lon: float) -> Optional[Dict]:
    """
    Fetch NO2 data from NASA TEMPO satellite using earthaccess streaming.
    
    Main entry point for TEMPO data retrieval. Uses earthaccess to stream data.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
    
    Returns:
        dict with NO2 data or None if unavailable
    """
    # Check coverage
    if not TEMPOService.is_in_coverage(lat, lon):
        logger.info(
            f"📍 Location ({lat:.4f}, {lon:.4f}) outside TEMPO coverage. "
            f"TEMPO covers North America only (15°N-70°N, 170°W-40°W)"
        )
        return None
    
    # Check if token is configured
    if not settings.nasa_earthdata_token:
        logger.warning("⚠️ NASA EarthData token not configured")
        return None
    
    # Search and extract with earthaccess
    logger.info(f"🛰️ Fetching NASA TEMPO data for ({lat:.4f}, {lon:.4f})...")
    return await TEMPOService.find_and_extract_no2(lat, lon)
