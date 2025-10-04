# Testing Instructions - Frontend-Backend Integration

## 🧪 Complete Testing Guide

Follow these steps to verify the frontend-backend integration is working correctly.

---

## Prerequisites

1. **Backend is deployed and running:**
   - URL: https://safeoutdoor-backend-3yse.onrender.com
   - Test: https://safeoutdoor-backend-3yse.onrender.com/health

2. **Frontend dependencies installed:**
   ```bash
   npm install
   ```

3. **Environment variable set:**
   - File `.env.local` exists in project root
   - Contains: `NEXT_PUBLIC_API_URL=https://safeoutdoor-backend-3yse.onrender.com`

---

## Test 1: Backend Health Check

### Browser Test

```bash
# Start the frontend
npm run dev
```

1. Open browser to http://localhost:3000
2. Look at **bottom-right corner** of screen
3. You should see a status indicator:
   - 🔵 "Checking backend connection..." (for a moment)
   - 🟢 "Backend connected" (if successful)
   - 🔴 "Backend offline - using sample data" (if backend is down)

### Console Test

Open browser DevTools (F12) and run:

```javascript
fetch('https://safeoutdoor-backend-3yse.onrender.com/health')
  .then(r => r.json())
  .then(console.log)
```

**Expected Output:**
```json
{
  "status": "healthy",
  "service": "SafeOutdoor API",
  "version": "1.0.0",
  "environment": "development"
}
```

✅ **PASS:** Backend is healthy and reachable

---

## Test 2: Complete User Flow

### Step-by-Step Test

1. **Navigate to homepage:** http://localhost:3000

2. **Step 1 - Choose Activity:**
   - Click on **"Hiking"** card
   - Click **"Next"** button
   - ✅ Verify: Transitions to location selection

3. **Step 2 - Choose Location:**
   - Click on **"Location"** tab (should be selected by default)
   - You should see "New York" with Central Park example
   - Click **"Next"** button
   - ✅ Verify: Transitions to analysis screen

4. **Step 3 - AI Analysis (THE IMPORTANT TEST):**
   
   **Watch for these indicators:**
   
   a. **Loading Animation (6 seconds):**
      - "Fetching NASA satellite data" with progress bar
      - "Checking air quality stations" with progress bar
      - "Analyzing weather patterns" with progress bar
      - "Calculating risk factors" with progress bar
   
   b. **Browser Console Logs:**
      - Open DevTools (F12) → Console tab
      - Look for these logs:
        ```
        [API Request] POST /api/analyze
        Calling backend API with: { activity: "hiking", lat: 40.7829, lon: -73.9654, ... }
        [API Response] 200 /api/analyze
        Backend response: { request_id: "...", risk_score: 8.3, ... }
        ```
   
   c. **Success Indicators:**
      - Large circular **Safety Score** appears (e.g., "83/100")
      - Below the score shows:
        - "Air Quality: AQI 42 (Good)"
        - "NASA TEMPO • OpenAQ • Open-Meteo • Open-Elevation"
      - ✅ **PASS if you see real AQI and data sources**
   
   d. **Error Handling (if backend is slow/offline):**
      - Yellow alert box appears: "Connection Issue"
      - Message: "Failed to connect to backend. Using sample data."
      - Score still shows (using mock data as fallback)
      - ✅ **PASS - Graceful degradation working**

5. **Step 4 - Smart Timing:**
   - Click **"Next"** button
   - See recommended timing and detailed analysis
   - Weather data shown
   - Checklist items displayed
   - ✅ Verify: Data from previous step is used

6. **Step 5 - Ready:**
   - Click **"Next"** button
   - See final confirmation screen
   - ✅ Verify: Flow completes successfully

---

## Test 3: API Direct Call Test

### Using Browser Console

```javascript
// Test the analyze endpoint directly
fetch('https://safeoutdoor-backend-3yse.onrender.com/api/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    activity: 'hiking',
    lat: 40.7829,
    lon: -73.9654,
    duration_hours: 4,
    start_time: new Date().toISOString()
  })
})
  .then(r => r.json())
  .then(data => {
    console.log('✅ Success! Risk Score:', data.risk_score)
    console.log('Air Quality AQI:', data.air_quality.aqi)
    console.log('Category:', data.category)
    console.log('Warnings:', data.warnings)
    console.log('Full response:', data)
  })
  .catch(err => {
    console.error('❌ Failed:', err)
  })
```

**Expected Output:**
```javascript
✅ Success! Risk Score: 8.3
Air Quality AQI: 42
Category: Good
Warnings: ["☀️ High UV - sunscreen recommended"]
Full response: { request_id: "...", risk_score: 8.3, ... }
```

---

## Test 4: Error Scenarios

### Test Timeout Handling

1. Disconnect internet temporarily
2. Navigate to Step 3 (Analysis)
3. **Expected:**
   - Loading indicators show
   - After 30 seconds, timeout occurs
   - Yellow error message appears
   - Mock data is used as fallback
   - ✅ **PASS:** Graceful error handling

### Test Invalid Coordinates

```javascript
// In browser console
fetch('https://safeoutdoor-backend-3yse.onrender.com/api/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    activity: 'hiking',
    lat: 999,  // Invalid
    lon: 999,  // Invalid
    duration_hours: 4
  })
})
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

**Expected:** 400 Bad Request error

---

## Test 5: CORS Verification

### Check Headers

```javascript
fetch('https://safeoutdoor-backend-3yse.onrender.com/api/analyze', {
  method: 'OPTIONS',
  headers: { 'Content-Type': 'application/json' }
})
  .then(r => {
    console.log('CORS Headers:')
    console.log('Access-Control-Allow-Origin:', r.headers.get('Access-Control-Allow-Origin'))
    console.log('Access-Control-Allow-Methods:', r.headers.get('Access-Control-Allow-Methods'))
  })
```

**Expected:**
- `Access-Control-Allow-Origin: http://localhost:3000` or `*`
- `Access-Control-Allow-Methods: GET, POST, OPTIONS`

✅ **PASS:** CORS is properly configured

---

## Test 6: Cold Start Behavior

**Note:** Render.com free tier sleeps after 15 minutes of inactivity.

### Test Cold Start

1. Wait 20 minutes without accessing the backend
2. Navigate to Step 3 (Analysis)
3. **Expected:**
   - First request takes 30-60 seconds
   - Loading indicators continue to show
   - Eventually returns data successfully
   - OR times out and uses mock data
   - ✅ **PASS:** Handles cold start gracefully

---

## Test 7: Different Locations

Test with various locations to ensure coordinate handling works:

### Test Cases

| Location | Coordinates | Expected Result |
|----------|-------------|-----------------|
| Central Park, NY | 40.7829, -73.9654 | AQI ~40-60 (Good) |
| Los Angeles, CA | 34.0522, -118.2437 | AQI ~80-120 (Moderate) |
| Denver, CO | 39.7392, -104.9903 | Elevation warning |
| Miami, FL | 25.7617, -80.1918 | High UV warning |

**Test each:**
1. Enter coordinates via location selection
2. Proceed to analysis
3. Verify different risk scores and warnings
4. ✅ **PASS:** Backend correctly analyzes different locations

---

## Test 8: Backend Status Component

### Visual Test

1. **Check Initial State:**
   - Look at bottom-right corner
   - Should show connection status

2. **Simulate Offline:**
   - Turn off internet
   - Wait 30 seconds
   - Status should change to 🔴 "Backend offline"

3. **Restore Connection:**
   - Turn internet back on
   - Within 30 seconds, status should change to 🟢 "Backend connected"
   - ✅ **PASS:** Status component works

---

## Checklist: Integration Verification

Use this checklist to confirm everything is working:

- [ ] ✅ `.env.local` file exists with correct backend URL
- [ ] ✅ `npm install` completed without errors
- [ ] ✅ Backend health check returns 200 OK
- [ ] ✅ Backend status indicator shows in bottom-right
- [ ] ✅ Status changes from checking → connected
- [ ] ✅ Can complete full flow (Steps 1-5)
- [ ] ✅ Analysis screen shows real AQI data
- [ ] ✅ Console logs show API request/response
- [ ] ✅ Data sources listed (NASA TEMPO, OpenAQ, etc.)
- [ ] ✅ Error handling works (yellow alert box)
- [ ] ✅ Mock data fallback works when backend fails
- [ ] ✅ No CORS errors in console
- [ ] ✅ Timeout handling works (30s limit)
- [ ] ✅ Different locations return different results

---

## Common Issues & Solutions

### Issue 1: "Backend offline" always shows

**Possible Causes:**
- Backend URL incorrect in `.env.local`
- Backend service is actually down
- CORS blocking the request

**Solutions:**
```bash
# Check .env.local
cat .env.local
# Should show: NEXT_PUBLIC_API_URL=https://safeoutdoor-backend-3yse.onrender.com

# Test backend directly
curl https://safeoutdoor-backend-3yse.onrender.com/health

# Restart dev server
# Ctrl+C to stop
npm run dev
```

### Issue 2: No console logs showing

**Solution:**
- Open DevTools (F12)
- Go to Console tab
- Clear console
- Refresh page
- Navigate to Step 3
- Logs should appear

### Issue 3: "TypeError: Cannot read property 'lat'"

**Cause:** Location data not passed to analysis

**Solution:**
- Ensure Step 2 (location selection) is completed
- Check that location data is saved in state
- Verify `adventureContext` prop is passed correctly

### Issue 4: Request takes forever

**Cause:** Backend cold start (Render.com free tier)

**Solutions:**
- Wait 60 seconds for first request
- Subsequent requests will be fast
- Consider backend warm-up ping service
- Or upgrade to Render paid tier

---

## Success Criteria

✅ **All Tests Pass If:**

1. Backend health check returns 200 OK
2. Status indicator shows "Backend connected"
3. Analysis screen displays real AQI values
4. Console shows successful API requests
5. Data sources are listed (NASA, OpenAQ, etc.)
6. Error handling works gracefully
7. Flow completes without crashes

---

## Debugging Tips

### Enable Verbose Logging

Add to `lib/api.ts`:
```typescript
apiClient.interceptors.request.use(config => {
  console.log('📤 API Request:', config.method?.toUpperCase(), config.url)
  console.log('📤 Payload:', config.data)
  return config
})

apiClient.interceptors.response.use(response => {
  console.log('📥 API Response:', response.status, response.data)
  return response
})
```

### Check Network Tab

1. Open DevTools (F12)
2. Go to Network tab
3. Filter by "Fetch/XHR"
4. Reload page and navigate to Step 3
5. Look for `analyze` request
6. Click on it to see:
   - Request headers
   - Request payload
   - Response data
   - Timing information

---

## Next Steps After Testing

If all tests pass:

1. ✅ **Ready for deployment!**
2. Add environment variable to Vercel/Netlify
3. Update backend CORS to include production domain
4. Test on production environment
5. Monitor for errors in production logs

If tests fail:

1. Review error messages in console
2. Check backend logs on Render.com
3. Verify API key configuration
4. Test backend independently
5. Contact support if needed

---

**Last Updated:** October 2024  
**Frontend Version:** 1.0.0  
**Backend URL:** https://safeoutdoor-backend-3yse.onrender.com
