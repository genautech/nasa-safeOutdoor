# 🚀 Quick Start - Test the Integration

## Steps to Test

### 1. Start the Development Server

```bash
npm run dev
```

### 2. Open Browser

Navigate to: **http://localhost:3000**

### 3. Complete the Flow

**Step 1: Choose Activity**
- Click **"Hiking"** card
- Click **"Next"**

**Step 2: Choose Location**
- Default location (New York) is already selected
- Click **"Next"**

**Step 3: AI Analysis** ⚡ **THIS IS WHERE THE MAGIC HAPPENS**

Watch for:
- ✅ Loading animations (6 seconds)
- ✅ Console logs showing API calls
- ✅ Real data appears:
  - Risk score (e.g., "83/100")
  - AQI value (e.g., "AQI 42 (Good)")
  - Data sources: "NASA TEMPO • OpenAQ • Open-Meteo • Open-Elevation"

### 4. Check Browser Console

Press **F12** → **Console** tab

You should see:
```
[API Request] POST /api/analyze
Calling backend API with: { activity: "hiking", lat: 40.7829, lon: -73.9654, ... }
[API Response] 200 /api/analyze
Backend response: { request_id: "...", risk_score: 8.3, air_quality: {...}, ... }
```

### 5. Check Backend Status

Look at the **bottom-right corner** of the screen:
- 🟢 **"Backend connected"** = Everything working!
- 🔴 **"Backend offline"** = Using mock data as fallback

---

## Expected Results

### ✅ Success Indicators

1. **Loading Progress Bars** appear and animate
2. **API Request Logs** in console
3. **Real Data Displays:**
   - Risk score from backend (0-100 scale)
   - Actual AQI value
   - List of data sources
4. **No Errors** in console
5. **Backend Status** shows green

### ⚠️ If Backend is Offline

You'll see:
- Yellow alert box: "Connection Issue"
- Message: "Failed to connect to backend. Using sample data."
- Flow continues with mock data
- Backend status shows red

**This is expected behavior!** The app gracefully falls back to sample data.

---

## Test Different Locations

Try various locations to see different results:

| Location | Coordinates | Expected |
|----------|-------------|----------|
| New York (default) | 40.7829, -73.9654 | AQI ~40-60 |
| Los Angeles | 34.0522, -118.2437 | Higher AQI |
| Denver | 39.7392, -104.9903 | Elevation warnings |
| Miami | 25.7617, -80.1918 | High UV warnings |

---

## Troubleshooting

### "Backend offline" always shows

**Check:**
1. Is `.env.local` file in project root?
   ```bash
   cat .env.local
   ```
   Should contain:
   ```
   NEXT_PUBLIC_API_URL=https://safeoutdoor-backend-3yse.onrender.com
   ```

2. Restart dev server:
   ```bash
   # Press Ctrl+C to stop
   npm run dev
   ```

3. Test backend directly:
   ```bash
   curl https://safeoutdoor-backend-3yse.onrender.com/health
   ```

### No console logs

**Solution:**
- Open DevTools (F12)
- Go to Console tab
- Refresh page
- Navigate to Step 3

### Cold Start (30-60s delay)

**Note:** Render.com free tier sleeps after 15 minutes of inactivity.

**First request may take 30-60 seconds.**

Subsequent requests will be fast (2-4 seconds).

---

## Backend API Endpoints

Test directly in browser console:

### Health Check
```javascript
fetch('https://safeoutdoor-backend-3yse.onrender.com/health')
  .then(r => r.json())
  .then(console.log)
```

### Analyze Endpoint
```javascript
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
```

---

## Success Checklist

- [ ] Dev server started (`npm run dev`)
- [ ] Opened http://localhost:3000
- [ ] Completed Step 1 (activity)
- [ ] Completed Step 2 (location)
- [ ] Saw loading animations on Step 3
- [ ] Console shows API request/response
- [ ] Real data displayed (AQI, risk score)
- [ ] Data sources listed
- [ ] Backend status indicator visible
- [ ] No CORS errors in console

---

## What's Next?

Once you've verified the integration works:

1. **Deploy to Production**
   - Push to Git
   - Deploy to Vercel/Netlify
   - Add environment variable
   - Update backend CORS

2. **Further Testing**
   - See `TESTING_INSTRUCTIONS.md` for comprehensive tests

3. **Customization**
   - Modify UI as needed
   - Add more features
   - Integrate additional APIs

---

**Need Help?**

Check these files:
- `FRONTEND_BACKEND_INTEGRATION.md` - Complete integration guide
- `TESTING_INSTRUCTIONS.md` - Detailed testing steps
- `IMPLEMENTATION_COMPLETE.md` - Implementation summary

**Backend URL:** https://safeoutdoor-backend-3yse.onrender.com  
**API Docs:** https://safeoutdoor-backend-3yse.onrender.com/docs

---

**Ready? Let's test it!**

```bash
npm run dev
```

🚀 **Open http://localhost:3000 and enjoy!**
