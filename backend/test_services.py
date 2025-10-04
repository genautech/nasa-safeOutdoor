"""Test script for API integration services."""
import asyncio
import logging
from app.services.nasa_tempo import fetch_tempo_no2
from app.services.openaq import fetch_openaq_data
from app.services.weather import fetch_weather_forecast
from app.services.elevation import fetch_elevation

# Configure logging to see the API calls
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def test_all_services():
    """Test all API integration services."""
    
    # Test coordinates: Central Park, New York
    lat, lon = 40.7829, -73.9654
    
    logger.info("=" * 60)
    logger.info("Testing API Integration Services")
    logger.info(f"Location: {lat}, {lon} (Central Park, NY)")
    logger.info("=" * 60)
    
    # Test NASA TEMPO NO2
    logger.info("\n[1/4] Testing NASA TEMPO NO2...")
    tempo_data = await fetch_tempo_no2(lat, lon)
    if tempo_data:
        logger.info(f"✓ TEMPO Success: NO2={tempo_data['no2_ppb']} ppb")
    else:
        logger.warning("✗ TEMPO Failed (check API credentials)")
    
    # Test OpenAQ
    logger.info("\n[2/4] Testing OpenAQ Air Quality...")
    openaq_data = await fetch_openaq_data(lat, lon, radius_km=25)
    if openaq_data:
        logger.info(f"✓ OpenAQ Success: PM2.5={openaq_data['pm25']}, "
                   f"NO2={openaq_data['no2']}, Stations={openaq_data['stations']}")
    else:
        logger.warning("✗ OpenAQ Failed (check API key or network)")
    
    # Test Weather Forecast
    logger.info("\n[3/4] Testing Weather Forecast (Open-Meteo)...")
    weather_data = await fetch_weather_forecast(lat, lon, hours=24)
    if weather_data:
        first_hour = weather_data[0]
        logger.info(f"✓ Weather Success: {len(weather_data)} hours fetched")
        logger.info(f"  First hour: {first_hour['temp_c']}°C, "
                   f"UV={first_hour['uv_index']}, Humidity={first_hour['humidity']}%")
    else:
        logger.warning("✗ Weather Failed")
    
    # Test Elevation
    logger.info("\n[4/4] Testing Elevation...")
    elevation_data = await fetch_elevation(lat, lon)
    if elevation_data:
        logger.info(f"✓ Elevation Success: {elevation_data['elevation_m']}m "
                   f"({elevation_data['terrain_type']})")
    else:
        logger.warning("✗ Elevation Failed")
    
    logger.info("\n" + "=" * 60)
    logger.info("Test Complete!")
    logger.info("=" * 60)
    
    # Return summary
    return {
        "tempo": tempo_data,
        "openaq": openaq_data,
        "weather": weather_data,
        "elevation": elevation_data
    }


async def test_retry_logic():
    """Test retry logic with invalid coordinates."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Retry Logic (will attempt 3 times each)")
    logger.info("=" * 60)
    
    # Invalid coordinates that might cause errors
    lat, lon = 91.0, 181.0  # Out of bounds
    
    logger.info(f"\nTesting with invalid coords: {lat}, {lon}")
    
    result = await fetch_elevation(lat, lon)
    if result:
        logger.info(f"Result: {result}")
    else:
        logger.info("✓ Correctly handled invalid input (returned None)")


if __name__ == "__main__":
    print("\n🚀 SafeOutdoor API Services Test Suite\n")
    
    # Run main tests
    results = asyncio.run(test_all_services())
    
    # Test retry logic
    asyncio.run(test_retry_logic())
    
    print("\n✅ All tests completed!")
    print("\nNote: Some services may fail if:")
    print("  - API keys are not configured in .env")
    print("  - Network connectivity issues")
    print("  - Rate limits are reached")
    print("\nThis is expected behavior - services will return None and use fallback data.")
