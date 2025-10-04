# SafeOutdoor Backend API

FastAPI backend for SafeOutdoor air quality and outdoor safety analysis application.

## Tech Stack

- **FastAPI 0.115+** - Modern Python web framework
- **Python 3.11+** - Programming language
- **Supabase** - PostgreSQL database and auth
- **httpx** - Async HTTP client
- **Pydantic v2** - Data validation
- **OpenAI** - AI-powered insights

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings (Pydantic)
│   ├── database.py          # Supabase client
│   ├── services/            # External API integrations
│   │   ├── nasa_tempo.py    # NASA TEMPO NO2 data
│   │   ├── openaq.py        # OpenAQ air quality
│   │   ├── weather.py       # Weather data
│   │   ├── elevation.py     # Elevation/terrain
│   │   └── geocoding.py     # Mapbox geocoding
│   ├── logic/               # Business logic
│   │   ├── risk_score.py    # Safety score calculation
│   │   ├── checklist.py     # Gear checklist generation
│   │   └── ai_analysis.py   # OpenAI insights
│   ├── routes/              # API endpoints
│   │   ├── analyze.py       # POST /api/analyze
│   │   ├── forecast.py      # GET /api/forecast
│   │   └── trips.py         # CRUD for trips
│   └── models/
│       └── schemas.py       # Pydantic models
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── Dockerfile              # Container image
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Required variables:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Supabase anon key
- `NASA_EARTHDATA_USER` - NASA Earthdata username
- `NASA_EARTHDATA_PASS` - NASA Earthdata password
- `OPENAQ_API_KEY` - OpenAQ API key
- `OPENWEATHER_API_KEY` - OpenWeather API key (or use Open-Meteo for free)
- `MAPBOX_TOKEN` - Mapbox access token
- `OPENAI_API_KEY` - OpenAI API key

### 3. Run Development Server

```bash
uvicorn app.main:app --reload
```

API will be available at: http://localhost:8000

API docs: http://localhost:8000/docs

## API Endpoints

### Health Check
```
GET /health
```

### Analyze Conditions
```
POST /api/analyze
```

Request body:
```json
{
  "activity": "hiking",
  "mode": "single",
  "location": {
    "lat": 40.7829,
    "lon": -73.9654,
    "city": "New York"
  }
}
```

### Get Forecast
```
GET /api/forecast?lat=40.7829&lon=-73.9654&days=7
```

### Trips CRUD
```
POST /api/trips
GET /api/trips
GET /api/trips/{trip_id}
DELETE /api/trips/{trip_id}
```

## Docker

Build and run with Docker:

```bash
docker build -t safeoutdoor-api .
docker run -p 8000:8000 --env-file .env safeoutdoor-api
```

## Development Notes

- Many service integrations have TODO comments where actual API calls need to be implemented
- Mock data is used in development mode for services that aren't fully integrated yet
- Error handling includes fallback data to ensure the API remains responsive
- Request IDs are added to all requests for tracing and debugging

## TODO

- [ ] Implement actual NASA TEMPO API integration
- [ ] Add caching layer (Redis) for API responses
- [ ] Implement rate limiting
- [ ] Add authentication/authorization
- [ ] Set up database migrations
- [ ] Add comprehensive test suite
- [ ] Implement WebSocket for real-time updates
- [ ] Add metrics and monitoring (Prometheus/Grafana)

## License

MIT
