# Frontend-Backend Integration Guide

## ✅ Integration Complete

The Next.js frontend is now connected to the deployed FastAPI backend at:
**https://safeoutdoor-backend-3yse.onrender.com**

---

## 📁 Files Created/Modified

### 1. Environment Configuration

**`.env.local`** (Created)
```bash
NEXT_PUBLIC_API_URL=https://safeoutdoor-backend-3yse.onrender.com
```

This file is already in `.gitignore` and won't be committed to the repository.

---

### 2. API Client Library

**`lib/api.ts`** (Created)

Complete API client with:
- ✅ Axios configuration with 30s timeout
- ✅ Request/response interceptors for logging
- ✅ TypeScript types for all endpoints
- ✅ Error handling and proper error messages
- ✅ Health check functionality

**Available Functions:**

```typescript
// Main analysis endpoint
analyzeAdventure(data: AnalyzeRequest): Promise<AnalyzeResponse>

// Multi-day forecast (when implemented)
getForecast(lat: number, lon: number, hours: number): Promise<ForecastResponse>

// Backend health check
healthCheck(): Promise<{ status: string; service: string; version: string }>

// Check if backend is reachable
checkBackendConnection(): Promise<boolean>
```

---

### 3. Updated Components

#### **`components/steps/step-2-analysis.tsx`** (Modified)

**Changes:**
- ✅ Imports `analyzeAdventure` from `lib/api`
- ✅ Calls real backend API with user's activity and location
- ✅ Converts backend response to SafetyAnalysis type
- ✅ Shows real-time data: AQI, risk score, data sources
- ✅ Error handling with user-friendly messages
- ✅ Falls back to mock data if API fails
- ✅ Loading states maintained for smooth UX

**Data Flow:**
```
User selects activity + location
    ↓
Step 2 Analysis screen loads
    ↓
Calls POST /api/analyze with coordinates
    ↓
Backend fetches data from 4 sources (NASA, OpenAQ, Weather, Elevation)
    ↓
Returns comprehensive analysis
    ↓
Frontend converts to SafetyAnalysis type
    ↓
Shows real risk score + AQI
    ↓
User proceeds to next step with real data
```

#### **`components/backend-status.tsx`** (Created)

Visual indicator showing backend connection status:
- 🔵 **Checking** - Initial connection test
- 🟢 **Connected** - Backend is healthy
- 🟡 **Warning** - Degraded performance
- 🔴 **Disconnected** - Using sample data

Auto-refreshes every 30 seconds.

---

## 🔄 API Request/Response Flow

### Example Request

```typescript
POST https://safeoutdoor-backend-3yse.onrender.com/api/analyze

{
  "activity": "hiking",
  "lat": 40.7829,
  "lon": -73.9654,
  "duration_hours": 4,
  "start_time": "2024-10-05T07:00:00Z"
}
```

### Example Response

```typescript
{
  "request_id": "abc-123",
  "risk_score": 8.3,  // 0-10 scale (converted to 0-100 for UI)
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
      "uv_index": 6.5,
      "precipitation_mm": 0.0,
      "cloud_cover": 25
    }
    // ... more hours
  ],
  "elevation": {
    "elevation_m": 450.0,
    "terrain_type": "hills"
  },
  "checklist": [
    {
      "item": "Hiking boots",
      "required": true,
      "reason": "Proper footwear for terrain",
      "category": "clothing"
    }
    // ... more items
  ],
  "warnings": [
    "☀️ High UV - sunscreen recommended"
  ],
  "ai_summary": "Great day for hiking! Air quality is good...",
  "risk_factors": [...],
  "data_sources": ["NASA TEMPO", "OpenAQ", "Open-Meteo", "Open-Elevation"],
  "generated_at": "2024-10-05T06:30:00Z"
}
```

---

## 🛡️ Error Handling

### 1. Network Errors

```typescript
try {
  const data = await analyzeAdventure(request)
  // Use real data
} catch (error) {
  console.error("Analysis failed:", error)
  // Fall back to mock data
  setError("Failed to connect to backend. Using sample data.")
}
```

### 2. Timeout Handling

Axios is configured with a 30-second timeout. If the backend doesn't respond within 30s, the request is cancelled and mock data is used.

### 3. HTTP Error Codes

| Code | Meaning | Frontend Action |
|------|---------|-----------------|
| 200 | Success | Use real data |
| 400 | Bad Request | Show validation error |
| 504 | Gateway Timeout | Fall back to mock data |
| 500 | Server Error | Fall back to mock data |

### 4. Visual Feedback

- **Loading States:** Progress bars show while fetching data
- **Error Messages:** Yellow alert box appears if connection fails
- **Fallback Data:** Mock data used seamlessly if API unavailable
- **Status Indicator:** Backend status component in bottom-right corner

---

## 🧪 Testing the Integration

### 1. Test Health Check

```bash
# Open browser console
fetch('https://safeoutdoor-backend-3yse.onrender.com/health')
  .then(r => r.json())
  .then(console.log)
```

Expected result:
```json
{
  "status": "healthy",
  "service": "SafeOutdoor API",
  "version": "1.0.0"
}
```

### 2. Test Full Flow

1. **Start the frontend:**
   ```bash
   npm run dev
   ```

2. **Navigate to Step 1:** Select an activity (e.g., Hiking)

3. **Navigate to Step 2:** Select a location (e.g., Central Park, New York)

4. **Watch Analysis Screen (Step 3):**
   - Loading progress shows
   - Backend API is called
   - Real data displays:
     - Risk score (0-100)
     - AQI value
     - Data sources listed

5. **Check Browser Console:**
   ```
   [API Request] POST /api/analyze
   Calling backend API with: {...}
   [API Response] 200 /api/analyze
   Backend response: {...}
   ```

6. **If backend is offline:**
   - Yellow alert box appears
   - "Using sample data" message shown
   - Flow continues with mock data

### 3. Test CORS

The backend is configured to allow requests from:
- `http://localhost:3000`
- `http://localhost:3001`
- `https://safeoutdoor.app`

If you see CORS errors, check:
1. Backend CORS configuration in `backend/app/main.py`
2. Frontend URL matches allowed origins
3. Browser console for specific error messages

---

## 🚀 Deployment Notes

### Frontend Deployment

When deploying to production (Vercel, Netlify, etc.):

1. **Add environment variable:**
   ```
   NEXT_PUBLIC_API_URL=https://safeoutdoor-backend-3yse.onrender.com
   ```

2. **Update backend CORS:**
   Add your production domain to `allowed_origins` in `backend/app/config.py`:
   ```python
   allowed_origins: list[str] = [
       "http://localhost:3000",
       "https://your-frontend-domain.vercel.app",  # Add this
       "https://safeoutdoor.app",
   ]
   ```

### Backend Cold Start

**Note:** Render.com free tier has cold start delays (~30-60 seconds) when the backend hasn't been accessed recently.

**Solutions:**
1. **Ping service:** Keep backend warm with periodic health checks
2. **Loading message:** Show "Waking up backend..." message
3. **Upgrade:** Use Render's paid tier for instant responses

---

## 📊 Performance

### Typical Response Times

| Scenario | Time |
|----------|------|
| Backend warm, all services healthy | 2-4s |
| Backend cold start (first request) | 30-60s |
| Backend warm, some fallbacks | 3-5s |
| Backend offline, using mock data | Instant |

### Optimization Tips

1. **Parallel Requests:** Backend already uses `asyncio.gather()` for parallel API calls
2. **Caching:** Consider caching responses for frequently requested locations
3. **Progressive Loading:** Show partial results as they arrive
4. **Preload:** Call API in background before user reaches analysis screen

---

## 🔍 Debugging

### Check Backend Logs

```bash
# If you have access to Render dashboard
# Go to: https://dashboard.render.com
# Select your service → Logs tab
```

### Browser Console Commands

```javascript
// Test health check
fetch('https://safeoutdoor-backend-3yse.onrender.com/health')
  .then(r => r.json())
  .then(console.log)

// Test analysis (replace with real coords)
fetch('https://safeoutdoor-backend-3yse.onrender.com/api/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    activity: 'hiking',
    lat: 40.7829,
    lon: -73.9654,
    duration_hours: 4
  })
})
  .then(r => r.json())
  .then(console.log)

// Check environment variable
console.log(process.env.NEXT_PUBLIC_API_URL)
```

### Common Issues

**1. "Cannot read property 'lat' of undefined"**
- **Cause:** Location data not passed correctly
- **Fix:** Ensure Step 2 receives `adventureContext` prop

**2. "Network Error" or "Failed to fetch"**
- **Cause:** Backend is offline or CORS issue
- **Fix:** Check backend health, verify CORS settings

**3. "Request timeout"**
- **Cause:** Backend cold start or slow external APIs
- **Fix:** Increase timeout or show "please wait" message

**4. ".env.local not loading"**
- **Cause:** File created after npm run dev
- **Fix:** Restart development server

---

## 📝 Next Steps

### Immediate Improvements

- [ ] Add loading skeleton for weather forecast
- [ ] Implement retry logic (3 attempts)
- [ ] Add analytics tracking for API calls
- [ ] Cache responses in localStorage
- [ ] Show estimated wait time for cold starts

### Future Enhancements

- [ ] WebSocket for real-time updates
- [ ] Progressive Web App (offline support)
- [ ] Background sync for saved trips
- [ ] Push notifications for weather changes
- [ ] Share trip analysis via URL

---

## 🎉 Summary

**Status:** ✅ **Integration Complete**

The frontend successfully connects to the deployed backend and:
- ✅ Calls real API endpoints
- ✅ Displays actual data (AQI, risk scores, weather)
- ✅ Handles errors gracefully
- ✅ Falls back to mock data when needed
- ✅ Shows user-friendly loading states
- ✅ Logs all API activity to console

**Test it now:**
```bash
npm run dev
# Navigate to http://localhost:3000
# Select activity → Select location → Watch real data load!
```

---

**Last Updated:** October 2024  
**Backend URL:** https://safeoutdoor-backend-3yse.onrender.com  
**API Docs:** https://safeoutdoor-backend-3yse.onrender.com/docs
