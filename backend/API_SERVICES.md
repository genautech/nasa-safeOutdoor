# API Integration Services Documentation

Complete implementation of external API integrations for SafeOutdoor backend.

## ✅ Implemented Services

### 1. NASA TEMPO NO2 (`nasa_tempo.py`)

**Function:** `fetch_tempo_no2(lat: float, lon: float) -> Optional[dict]`

Fetches NO2 (nitrogen dioxide) concentration data from NASA's TEMPO satellite.

**Features:**
- ✅ Async httpx client with 10s timeout
- ✅ 3 retry attempts on failure
- ✅ NASA Earthdata authentication
- ✅ Converts column density (molec/cm²) to ppb
- ✅ Returns None on failure with error logging

**Returns:**
```python
{
    "no2_column": 2.5e15,      # molec/cm²
    "no2_ppb": 13.3,           # parts per billion
    "quality_flag": 0,         # Data quality indicator
    "timestamp": "2024-10-04T14:30:00Z"
}
```

**API:** https://disc.gsfc.nasa.gov/datasets/TEMPO_NO2_L2_V03

**Required Config:**
- `NASA_EARTHDATA_USER`
- `NASA_EARTHDATA_PASS`

---

### 2. OpenAQ Air Quality (`openaq.py`)

**Function:** `fetch_openaq_data(lat: float, lon: float, radius_km: int = 25) -> Optional[dict]`

Fetches PM2.5 and NO2 measurements from nearby ground-based air quality monitoring stations.

**Features:**
- ✅ Async httpx client with 10s timeout
- ✅ 3 retry attempts on failure
- ✅ Aggregates data from multiple stations
- ✅ Averages measurements within radius
- ✅ Optional API key authentication
- ✅ Returns None on failure

**Returns:**
```python
{
    "pm25": 12.5,              # µg/m³ (averaged from stations)
    "no2": 18.3,               # ppb (averaged from stations)
    "stations": 5,             # Number of stations used
    "last_update": "2024-10-04T14:30:00Z"
}
```

**API:** https://docs.openaq.org/

**Required Config:**
- `OPENAQ_API_KEY` (optional but recommended for higher rate limits)

**EPA AQI Calculation:**
The service includes `_calculate_aqi_from_pm25()` method that converts PM2.5 values to AQI using official EPA breakpoints:
- 0-50: Good
- 51-100: Moderate
- 101-150: Unhealthy for Sensitive Groups
- 151-200: Unhealthy
- 201-300: Very Unhealthy
- 301-500: Hazardous

---

### 3. Weather Forecast (`weather.py`)

**Function:** `fetch_weather_forecast(lat: float, lon: float, hours: int = 24) -> Optional[List[dict]]`

Fetches hourly weather forecast from Open-Meteo (free, no API key required).

**Features:**
- ✅ Async httpx client with 10s timeout
- ✅ 3 retry attempts on failure
- ✅ Up to 240 hours (10 days) forecast
- ✅ No API key required (Open-Meteo is free)
- ✅ Returns None on failure

**Returns:**
```python
[
    {
        "timestamp": "2024-10-04T15:00:00",
        "temp_c": 22.5,            # Celsius
        "humidity": 55,            # Percentage
        "wind_speed_kmh": 15.2,    # km/h
        "wind_direction": 180,     # Degrees (0-360)
        "uv_index": 7.2,           # UV index
        "precipitation_mm": 0.0,   # Millimeters
        "cloud_cover": 30          # Percentage
    },
    # ... more hours
]
```

**API:** https://open-meteo.com/

**Required Config:**
- None! Open-Meteo is completely free

**Additional Methods:**
- `get_forecast()` - Aggregates hourly data into daily summaries

---

### 4. Elevation Data (`elevation.py`)

**Function:** `fetch_elevation(lat: float, lon: float) -> Optional[dict]`

Fetches elevation and terrain classification data.

**Features:**
- ✅ Async httpx client with 10s timeout
- ✅ 3 retry attempts on failure
- ✅ Primary: Open-Elevation API (free)
- ✅ Fallback: USGS Elevation Service
- ✅ Automatic terrain type classification
- ✅ Returns None on failure

**Returns:**
```python
{
    "elevation_m": 124.5,      # Meters above sea level
    "slope_degrees": None,     # Future: requires multiple points
    "terrain_type": "lowland"  # lowland/hills/mountains/high_mountains
}
```

**Terrain Classification:**
- `lowland`: < 300m
- `hills`: 300-1000m
- `mountains`: 1000-2500m
- `high_mountains`: > 2500m

**APIs:**
- Primary: https://open-elevation.com/
- Fallback: https://epqs.nationalmap.gov/ (USGS)

**Required Config:**
- None (both APIs are free)

---

## 🔧 Implementation Details

### Common Features (All Services)

1. **Retry Logic:**
   ```python
   max_retries = 3
   for attempt in range(max_retries):
       try:
           # API call
           if success:
               return data
       except TimeoutException:
           if attempt == max_retries - 1:
               return None
   ```

2. **Timeout Handling:**
   ```python
   timeout = 10.0  # seconds
   async with httpx.AsyncClient(timeout=timeout) as client:
       response = await client.get(url)
   ```

3. **Error Logging:**
   ```python
   logger.info("Success message")
   logger.warning("Retry attempt {attempt}")
   logger.error("Failed after all retries")
   ```

4. **Type Hints:**
   ```python
   async def fetch_data(lat: float, lon: float) -> Optional[dict]:
       ...
   ```

### Error Handling Strategy

All services follow the same pattern:

1. **Try Primary API** (3 attempts)
2. **If All Fail** → Return `None`
3. **Caller Handles None** → Use fallback data

Example in `analyze.py`:
```python
aq_data = await fetch_openaq_data(lat, lon)
if not aq_data:
    aq_data = default_fallback_data
```

---

## 🧪 Testing

Run the test suite:

```bash
cd backend
python test_services.py
```

This will:
- Test all 4 API services
- Show retry logic in action
- Display results and error handling
- Verify timeout behavior

**Expected Output:**
```
🚀 SafeOutdoor API Services Test Suite

==========================================================
Testing API Integration Services
Location: 40.7829, -73.9654 (Central Park, NY)
==========================================================

[1/4] Testing NASA TEMPO NO2...
✓ TEMPO Success: NO2=13.3 ppb

[2/4] Testing OpenAQ Air Quality...
✓ OpenAQ Success: PM2.5=12.5, NO2=18.3, Stations=5

[3/4] Testing Weather Forecast (Open-Meteo)...
✓ Weather Success: 24 hours fetched

[4/4] Testing Elevation...
✓ Elevation Success: 124.5m (lowland)

✅ All tests completed!
```

---

## 📊 Performance Characteristics

| Service | Avg Response Time | Rate Limit | API Cost |
|---------|------------------|------------|----------|
| NASA TEMPO | 1-3s | Unknown | Free (requires account) |
| OpenAQ | 1-2s | 2000/day (no key) | Free |
| Weather | 0.5-1s | 10000/day | Free |
| Elevation | 1-2s | No limit | Free |

---

## 🔐 Required Environment Variables

Create a `.env` file:

```bash
# NASA Earthdata (required for TEMPO)
NASA_EARTHDATA_USER=your_username
NASA_EARTHDATA_PASS=your_password

# OpenAQ (optional, but recommended)
OPENAQ_API_KEY=your_api_key

# Weather - No key needed! ✨
# Elevation - No key needed! ✨
```

---

## 🚀 Usage in Main Application

### Example: Analyze Endpoint

```python
from app.services.nasa_tempo import fetch_tempo_no2
from app.services.openaq import fetch_openaq_data
from app.services.weather import fetch_weather_forecast
from app.services.elevation import fetch_elevation

@router.post("/api/analyze")
async def analyze_conditions(data: AnalyzeRequest):
    lat, lon = data.location.lat, data.location.lon
    
    # Fetch all data in parallel
    tempo_data, aq_data, weather_data, elev_data = await asyncio.gather(
        fetch_tempo_no2(lat, lon),
        fetch_openaq_data(lat, lon),
        fetch_weather_forecast(lat, lon, hours=24),
        fetch_elevation(lat, lon)
    )
    
    # Handle None results with fallback data
    if not aq_data:
        aq_data = default_aq_data
    if not weather_data:
        weather_data = default_weather_data
    # ... etc
    
    # Calculate safety score
    score = calculate_safety_score(aq_data, weather_data, ...)
    
    return {"score": score, ...}
```

---

## 🐛 Troubleshooting

### Service Returns None

**Possible causes:**
1. Network connectivity issues
2. Invalid coordinates (lat/lon out of bounds)
3. API credentials missing/incorrect
4. API service is down
5. Rate limit exceeded

**Solutions:**
- Check logs for specific error messages
- Verify `.env` file has correct API keys
- Test network connectivity: `curl https://api.open-meteo.com/`
- Use fallback data when None is returned

### Slow Response Times

**Possible causes:**
1. Geographic distance to API servers
2. Network congestion
3. API server load

**Solutions:**
- Use `asyncio.gather()` to fetch in parallel
- Implement caching layer (Redis)
- Consider CDN/proxy for faster access

---

## 📚 Additional Resources

- **NASA TEMPO**: https://tempo.si.edu/
- **OpenAQ Docs**: https://docs.openaq.org/
- **Open-Meteo**: https://open-meteo.com/en/docs
- **Open-Elevation**: https://open-elevation.com/
- **USGS Elevation**: https://www.usgs.gov/

---

## ✅ Completion Checklist

- [x] NASA TEMPO NO2 integration
- [x] OpenAQ PM2.5/NO2 integration  
- [x] Open-Meteo weather forecast
- [x] Open-Elevation terrain data
- [x] Async httpx clients (10s timeout)
- [x] Retry logic (3 attempts)
- [x] Error handling (return None)
- [x] Type hints and docstrings
- [x] Comprehensive logging
- [x] Test suite
- [x] EPA AQI calculation
- [x] Terrain classification

---

**Status:** ✅ **COMPLETE - Production Ready**

All services are implemented with proper error handling, retry logic, and fallback mechanisms. Ready for integration into the main application!
