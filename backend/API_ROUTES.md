# API Routes Documentation

Complete documentation for SafeOutdoor backend API endpoints.

## Base URL

**Development:** `http://localhost:8000`  
**Production:** `https://api.safeoutdoor.app`

---

## Main Endpoints

### 1. Analyze Adventure (`POST /api/analyze`)

**Main orchestration endpoint** that fetches all data and performs complete safety analysis.

#### Request

```http
POST /api/analyze
Content-Type: application/json

{
  "activity": "hiking",
  "lat": 40.7829,
  "lon": -73.9654,
  "start_time": "2024-10-05T07:00:00Z",  // Optional
  "duration_hours": 4,
  "user_profile": {}  // Optional
}
```

#### Request Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `activity` | string | ✅ Yes | Activity type: `hiking`, `cycling`, `running`, `trail_running`, `camping`, `rock_climbing`, `mountaineering` |
| `lat` | float | ✅ Yes | Latitude (-90 to 90) |
| `lon` | float | ✅ Yes | Longitude (-180 to 180) |
| `start_time` | string | No | ISO 8601 timestamp (e.g., `2024-10-05T07:00:00Z`) |
| `duration_hours` | int | No | Expected duration (1-72 hours, default: 4) |
| `user_profile` | object | No | User preferences and health information |

#### Response

```json
{
  "request_id": "a1b2c3d4-...",
  "risk_score": 8.3,
  "category": "Good",
  "air_quality": {
    "aqi": 42,
    "category": "Good",
    "pm25": 12.5,
    "no2": 18.3,
    "dominant_pollutant": "pm25"
  },
  "weather_forecast": [
    {
      "timestamp": "2024-10-05T07:00:00",
      "temp_c": 22.5,
      "humidity": 55,
      "wind_speed_kmh": 12.0,
      "wind_direction": 180,
      "uv_index": 6.5,
      "precipitation_mm": 0.0,
      "cloud_cover": 25
    }
    // ... more hours
  ],
  "elevation": {
    "elevation_m": 450.0,
    "terrain_type": "hills",
    "slope_degrees": null
  },
  "checklist": [
    {
      "item": "Hiking boots or trail shoes",
      "required": true,
      "reason": "Proper footwear for terrain",
      "category": "clothing"
    },
    {
      "item": "Sunscreen SPF 30+",
      "required": true,
      "reason": "High UV index (6.5)",
      "category": "sun_protection"
    }
    // ... more items
  ],
  "warnings": [
    "☀️ High UV - sunscreen and hat recommended"
  ],
  "ai_summary": "Great day for hiking! Air quality is good (AQI 42) and weather is favorable at 22°C. UV levels are moderate, so remember your sunscreen and enjoy the trails!",
  "risk_factors": [
    {
      "factor": "Air Quality",
      "score": 9.2,
      "weight": 0.35
    },
    {
      "factor": "Weather",
      "score": 8.5,
      "weight": 0.25
    },
    {
      "factor": "UV Exposure",
      "score": 7.0,
      "weight": 0.15
    },
    {
      "factor": "Terrain",
      "score": 9.0,
      "weight": 0.15
    }
  ],
  "data_sources": [
    "NASA TEMPO",
    "OpenAQ",
    "Open-Meteo",
    "Open-Elevation"
  ],
  "generated_at": "2024-10-05T06:30:00.123456Z"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `request_id` | string | Unique identifier for request tracing |
| `risk_score` | float | Overall safety score (0-10, higher is safer) |
| `category` | string | Risk category: `Excellent`, `Good`, `Moderate`, `Poor`, `Dangerous` |
| `air_quality` | object | Air quality metrics and AQI |
| `weather_forecast` | array | Hourly weather forecast for duration |
| `elevation` | object | Elevation and terrain information |
| `checklist` | array | Comprehensive gear checklist |
| `warnings` | array | Safety warnings (empty if excellent conditions) |
| `ai_summary` | string | Natural language summary (AI-generated) |
| `risk_factors` | array | Breakdown of sub-scores by factor |
| `data_sources` | array | List of data sources used |
| `generated_at` | string | ISO 8601 timestamp of analysis |

#### Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success - analysis complete |
| `400` | Bad Request - invalid parameters |
| `504` | Gateway Timeout - external services timed out |
| `500` | Internal Server Error - analysis failed |

#### Flow Diagram

```
POST /api/analyze
    │
    ├─→ Parallel Data Fetch (asyncio.gather)
    │   ├─→ NASA TEMPO (NO2)
    │   ├─→ OpenAQ (PM2.5)
    │   ├─→ Open-Meteo (Weather)
    │   └─→ Open-Elevation (Elevation)
    │
    ├─→ Calculate AQI (from PM2.5 + NO2)
    │
    ├─→ Calculate Risk Score
    │   ├─→ Air Quality Sub-Score (35%)
    │   ├─→ Weather Sub-Score (25%)
    │   ├─→ UV Sub-Score (15%)
    │   └─→ Terrain Sub-Score (15%)
    │
    ├─→ Generate Checklist
    │   ├─→ Base checklist by activity
    │   └─→ Add conditional items
    │
    ├─→ Generate AI Summary (OpenAI)
    │   └─→ Fallback to template if fails
    │
    └─→ Return Complete Response
```

---

### 2. Health Check (`GET /api/health`)

Simple health check for the analyze service.

#### Request

```http
GET /api/health
```

#### Response

```json
{
  "status": "healthy",
  "service": "analyze",
  "endpoints": ["/api/analyze"]
}
```

---

## Example Requests

### Example 1: Perfect Hiking Day

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "activity": "hiking",
    "lat": 40.7829,
    "lon": -73.9654,
    "duration_hours": 4
  }'
```

**Expected Result:** Score ~8-9, category "Good" or "Excellent"

---

### Example 2: Running with Poor Air Quality

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "activity": "running",
    "lat": 34.0522,
    "lon": -118.2437,
    "duration_hours": 2
  }'
```

**Expected Result:** May show air quality warnings, mask recommendations

---

### Example 3: High Altitude Mountaineering

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "activity": "mountaineering",
    "lat": 27.9881,
    "lon": 86.9250,
    "duration_hours": 12
  }'
```

**Expected Result:** Altitude warnings, additional cold weather gear

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": [
    {
      "loc": ["body", "lat"],
      "msg": "ensure this value is greater than or equal to -90",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error",
  "message": "Analysis failed: <error details>",
  "request_id": "a1b2c3d4-..."
}
```

### 504 Gateway Timeout

```json
{
  "detail": "Analysis timed out while fetching data from external services"
}
```

---

## Data Sources

The API integrates data from multiple sources:

### 1. NASA TEMPO
- **Data:** NO2 column density (satellite)
- **Coverage:** Continental United States
- **Update:** Hourly during daylight
- **Auth:** NASA Earthdata credentials required

### 2. OpenAQ
- **Data:** PM2.5, NO2 from ground stations
- **Coverage:** Global (varies by location)
- **Update:** Hourly
- **Auth:** API key optional (higher rate limits)

### 3. Open-Meteo
- **Data:** Weather forecast (temp, UV, wind, etc.)
- **Coverage:** Global
- **Update:** Hourly, up to 10 days
- **Auth:** None required (free)

### 4. Open-Elevation
- **Data:** Elevation and terrain classification
- **Coverage:** Global
- **Update:** Static
- **Auth:** None required (free)
- **Fallback:** USGS Elevation Service

---

## Rate Limits

| Endpoint | Rate Limit | Notes |
|----------|------------|-------|
| `POST /api/analyze` | 60 requests/minute | Per IP address |
| `GET /api/health` | Unlimited | Monitoring only |

---

## Performance

Typical response times:

| Condition | Response Time |
|-----------|---------------|
| All services healthy | 1-3 seconds |
| Some fallbacks needed | 2-4 seconds |
| Heavy load | 3-5 seconds |

**Optimization:** All external API calls are made in parallel using `asyncio.gather()`.

---

## Integration Examples

### Python

```python
import httpx
import asyncio

async def analyze_adventure():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/analyze",
            json={
                "activity": "hiking",
                "lat": 40.7829,
                "lon": -73.9654,
                "duration_hours": 4
            }
        )
        data = response.json()
        print(f"Risk Score: {data['risk_score']}/10")
        print(f"Category: {data['category']}")
        print(f"Warnings: {len(data['warnings'])}")

asyncio.run(analyze_adventure())
```

### JavaScript/TypeScript

```javascript
const response = await fetch('http://localhost:8000/api/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    activity: 'hiking',
    lat: 40.7829,
    lon: -73.9654,
    duration_hours: 4
  })
});

const data = await response.json();
console.log(`Risk Score: ${data.risk_score}/10`);
console.log(`Category: ${data.category}`);
console.log(`AI Summary: ${data.ai_summary}`);
```

### cURL (with pretty print)

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "activity": "hiking",
    "lat": 40.7829,
    "lon": -73.9654,
    "duration_hours": 4
  }' | jq '.'
```

---

## Development

### Running Locally

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### API Documentation

Interactive API docs available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Testing

```bash
# Run test suite
python test_services.py
python test_logic.py

# Test endpoint
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

---

## Future Endpoints (Planned)

### Forecast (`GET /api/forecast`)
Multi-day forecast for location

### Trips (`POST /api/trips`)
Save trip analysis to database

### Trips List (`GET /api/trips`)
Retrieve user's saved trips

---

## Support

- **GitHub:** [github.com/safeoutdoor/backend](https://github.com/safeoutdoor/backend)
- **Docs:** [docs.safeoutdoor.app](https://docs.safeoutdoor.app)
- **Email:** support@safeoutdoor.app

---

**Version:** 1.0.0  
**Last Updated:** October 2024  
**Status:** ✅ Production Ready
