# 🚀 Deployment Steps - CORS Fix

## ✅ CORS Configuration Updated

The backend CORS settings have been updated to allow requests from your frontend.

---

## Deploy Backend Changes

### Option 1: Git Push (Recommended)

If your backend is connected to a Git repository on Render.com:

```bash
# Navigate to backend directory
cd backend

# Check status
git status

# Add the changed file
git add app/main.py

# Commit
git commit -m "Fix: Update CORS to allow frontend origins"

# Push to main/master
git push origin main
```

Render.com will **automatically redeploy** the backend within 2-3 minutes.

---

### Option 2: Manual Redeploy

If auto-deploy is not enabled:

1. **Go to Render Dashboard:**
   - https://dashboard.render.com

2. **Select your service:**
   - Find "safeoutdoor-backend" (or your service name)
   - Click on it

3. **Manual Deploy:**
   - Click "Manual Deploy" button
   - Select "Deploy latest commit"
   - Wait 2-3 minutes for deployment

4. **Check Logs:**
   - Click "Logs" tab
   - Look for "Starting SafeOutdoor API" message
   - Verify no errors during startup

---

### Option 3: Direct File Upload (If no Git)

If you're not using Git:

1. Copy the updated `backend/app/main.py` file
2. Upload to your Render.com service via their dashboard
3. Restart the service

---

## Verify Deployment

### 1. Check Backend is Running

```bash
curl https://safeoutdoor-backend-3yse.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "SafeOutdoor API",
  "version": "1.0.0"
}
```

### 2. Test CORS from Browser

Open your frontend (http://localhost:3000) and open browser console (F12):

```javascript
// Test health endpoint
fetch('https://safeoutdoor-backend-3yse.onrender.com/health')
  .then(r => r.json())
  .then(data => console.log('✅ CORS working!', data))
  .catch(err => console.error('❌ CORS error:', err))

// Test analyze endpoint
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
  .then(data => console.log('✅ API call successful!', data))
  .catch(err => console.error('❌ API error:', err))
```

### 3. Test Full Frontend Flow

1. Start frontend: `npm run dev`
2. Navigate to http://localhost:3000
3. Go through the flow:
   - Step 1: Select activity
   - Step 2: Select location
   - Step 3: Watch analysis
4. Check browser console for:
   - ✅ No CORS errors
   - ✅ API request/response logs
   - ✅ Real data displayed

---

## What Changed

**File:** `backend/app/main.py`

```python
# Before
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # From config file
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# After
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",              # Local development
        "http://127.0.0.1:3000",             # Alternative localhost
        "http://localhost:3001",             # Alternative port
        "https://safe-outdoor.vercel.app",   # Vercel production
        "https://safeoutdoor.app",           # Custom domain
        "*"                                   # Allow all (temporary)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Troubleshooting

### Issue: "Still getting CORS errors"

**Solutions:**

1. **Clear browser cache:**
   - Press Ctrl+Shift+Delete
   - Clear cached images and files
   - Refresh page (Ctrl+F5)

2. **Check deployment status:**
   ```bash
   curl -I https://safeoutdoor-backend-3yse.onrender.com/health
   ```
   Look for `200 OK` status

3. **Check backend logs on Render:**
   - Go to dashboard
   - Click "Logs" tab
   - Look for error messages

4. **Verify CORS headers:**
   - Open DevTools (F12) → Network tab
   - Make a request
   - Check Response Headers for:
     ```
     Access-Control-Allow-Origin: http://localhost:3000
     Access-Control-Allow-Credentials: true
     ```

### Issue: "OPTIONS request failed"

**Cause:** Preflight request not handled

**Solution:** Already handled by `allow_methods=["*"]` ✅

### Issue: "Backend not redeploying"

**Solutions:**

1. **Force redeploy:**
   - Go to Render dashboard
   - Click "Manual Deploy"
   - Select "Clear build cache & deploy"

2. **Check build logs:**
   - Look for "Build successful" message
   - Check for Python errors

3. **Restart service:**
   - Dashboard → Settings → Restart Service

---

## Production Deployment

When deploying to production (Vercel):

### 1. Deploy Frontend to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Or use Vercel dashboard:
# 1. Connect GitHub repo
# 2. Import project
# 3. Add environment variable:
#    NEXT_PUBLIC_API_URL=https://safeoutdoor-backend-3yse.onrender.com
# 4. Deploy
```

### 2. Update Backend CORS

After deploying frontend, note your Vercel URL (e.g., `https://safe-outdoor-abc123.vercel.app`)

Update `backend/app/main.py`:

```python
allow_origins=[
    "http://localhost:3000",                  # Keep for local dev
    "https://safe-outdoor-abc123.vercel.app", # Your Vercel URL
    "https://safe-outdoor.vercel.app",        # If you set custom domain
    # Remove "*" for production security
]
```

### 3. Redeploy Backend

```bash
cd backend
git add app/main.py
git commit -m "Update: Add production frontend domain to CORS"
git push
```

---

## Security Recommendations

### Remove Wildcard in Production

**Current (Development):**
```python
allow_origins=[
    "http://localhost:3000",
    "*"  # Allows any domain
]
```

**Production (Secure):**
```python
allow_origins=[
    "https://safe-outdoor.vercel.app",  # Only production domain
    "https://safeoutdoor.app"           # Custom domain if any
]
```

### Environment-Based Configuration

For better security, use environment variables:

**Create:** `backend/.env`
```bash
ALLOWED_ORIGINS=https://safe-outdoor.vercel.app,https://safeoutdoor.app
```

**Update:** `backend/app/main.py`
```python
import os

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Set on Render.com:**
1. Dashboard → Service → Environment
2. Add variable: `ALLOWED_ORIGINS`
3. Value: `https://safe-outdoor.vercel.app,https://safeoutdoor.app`
4. Save and redeploy

---

## Verification Checklist

After deployment:

- [ ] Backend health check returns 200 OK
- [ ] No CORS errors in browser console
- [ ] Frontend can call `/health` endpoint
- [ ] Frontend can call `/api/analyze` endpoint
- [ ] Response includes CORS headers
- [ ] Full flow works end-to-end
- [ ] Backend logs show successful requests
- [ ] Status indicator shows 🟢 "Backend connected"

---

## Quick Test Commands

```bash
# Test backend is running
curl https://safeoutdoor-backend-3yse.onrender.com/health

# Test CORS headers
curl -i -X OPTIONS https://safeoutdoor-backend-3yse.onrender.com/health \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST"

# Test API endpoint
curl -X POST https://safeoutdoor-backend-3yse.onrender.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"activity":"hiking","lat":40.7829,"lon":-73.9654,"duration_hours":4}'
```

---

## Next Steps

1. ✅ **CORS is fixed** - Backend updated
2. 🚀 **Deploy the changes** - Push to Git or manual deploy
3. 🧪 **Test the integration** - Use browser console tests
4. 📊 **Monitor logs** - Check for errors on Render
5. 🔒 **Secure for production** - Remove wildcard, use specific domains

---

**Need Help?**

Check these files:
- `CORS_UPDATE.md` - Detailed CORS documentation
- `TESTING_INSTRUCTIONS.md` - Testing guide
- `FRONTEND_BACKEND_INTEGRATION.md` - Integration overview

**Backend URL:** https://safeoutdoor-backend-3yse.onrender.com  
**Render Dashboard:** https://dashboard.render.com

---

**Status:** ✅ CORS Fixed - Ready to Deploy
