# CORS Configuration Update

## ✅ CORS Fixed

Updated `backend/app/main.py` to allow requests from frontend domains.

---

## Updated Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Local dev (standard Next.js port)
        "http://127.0.0.1:3000",      # Local dev (alternative)
        "http://localhost:3001",      # Local dev (alternative port)
        "https://safe-outdoor.vercel.app",  # Vercel production
        "https://safeoutdoor.app",    # Custom domain (if applicable)
        "*"                            # Allow all (temporary for development)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## What Changed

**Before:**
- Used `settings.allowed_origins` from config file
- Limited to specific domains only

**After:**
- Hardcoded list of allowed origins
- Includes localhost for development
- Includes production domains
- Includes `"*"` wildcard for testing

---

## Deployment Steps

### 1. **Commit and Push to Git**

```bash
cd backend
git add app/main.py
git commit -m "Fix: Update CORS to allow frontend origins"
git push
```

### 2. **Redeploy on Render.com**

The backend will automatically redeploy if you have auto-deploy enabled.

Or manually redeploy:
1. Go to https://dashboard.render.com
2. Select your service
3. Click "Manual Deploy" → "Deploy latest commit"
4. Wait for deployment to complete (~2-3 minutes)

### 3. **Test CORS**

After redeployment, test in browser console:

```javascript
// Test preflight OPTIONS request
fetch('https://safeoutdoor-backend-3yse.onrender.com/health', {
  method: 'OPTIONS',
  headers: {
    'Origin': 'http://localhost:3000',
    'Access-Control-Request-Method': 'POST'
  }
})
  .then(r => {
    console.log('CORS Headers:')
    console.log('Allow-Origin:', r.headers.get('Access-Control-Allow-Origin'))
    console.log('Allow-Methods:', r.headers.get('Access-Control-Allow-Methods'))
    console.log('Allow-Headers:', r.headers.get('Access-Control-Allow-Headers'))
  })

// Test actual request
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
  .then(data => console.log('✅ CORS working!', data))
  .catch(err => console.error('❌ CORS error:', err))
```

---

## Security Considerations

### Development vs Production

**For Development (Current):**
```python
allow_origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"  # Allows all origins
]
```

**For Production (Recommended):**
```python
allow_origins=[
    "https://safe-outdoor.vercel.app",
    "https://safeoutdoor.app"
    # Remove "*" wildcard
    # Remove localhost entries
]
```

### Best Practices

1. **Remove `"*"` wildcard in production**
   - Allows any domain to access your API
   - Security risk if API keys or sensitive data are exposed
   - Only use for development/testing

2. **Use specific domains only**
   ```python
   allow_origins=[
       "https://safe-outdoor.vercel.app",
       "https://safeoutdoor.app"
   ]
   ```

3. **Environment-based configuration**
   ```python
   import os
   
   if os.getenv("ENVIRONMENT") == "production":
       allowed_origins = [
           "https://safe-outdoor.vercel.app",
           "https://safeoutdoor.app"
       ]
   else:
       allowed_origins = [
           "http://localhost:3000",
           "http://127.0.0.1:3000",
           "*"
       ]
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=allowed_origins,
       ...
   )
   ```

---

## Common CORS Errors

### Error 1: "Access-Control-Allow-Origin missing"

**Cause:** Frontend domain not in allowed origins list

**Solution:**
- Add frontend domain to `allow_origins` list
- Ensure no trailing slashes in URLs
- Check protocol (http vs https)

### Error 2: "Credentials mode is 'include' but Access-Control-Allow-Credentials is false"

**Cause:** `allow_credentials=False` but frontend sends credentials

**Solution:**
- Set `allow_credentials=True` (already done ✅)

### Error 3: "Preflight request failed"

**Cause:** OPTIONS request not handled correctly

**Solution:**
- Ensure `allow_methods=["*"]` (already done ✅)
- Ensure `allow_headers=["*"]` (already done ✅)

---

## Testing Checklist

After redeployment:

- [ ] Frontend can connect to `/health` endpoint
- [ ] Frontend can call `/api/analyze` endpoint
- [ ] No CORS errors in browser console
- [ ] Backend logs show successful requests
- [ ] Preflight OPTIONS requests succeed
- [ ] POST requests with JSON body work
- [ ] Response headers include CORS headers

---

## Verification

### Browser Console Test

```javascript
// Open http://localhost:3000
// Press F12 → Console
// Run this:

fetch('https://safeoutdoor-backend-3yse.onrender.com/health')
  .then(r => r.json())
  .then(data => console.log('✅ No CORS error!', data))
  .catch(err => console.error('❌ CORS error:', err))
```

**Expected Output:**
```javascript
✅ No CORS error! {
  status: "healthy",
  service: "SafeOutdoor API",
  version: "1.0.0"
}
```

### Network Tab Check

1. Open DevTools (F12)
2. Go to Network tab
3. Make a request to the backend
4. Click on the request
5. Check Response Headers:
   ```
   Access-Control-Allow-Origin: http://localhost:3000
   Access-Control-Allow-Credentials: true
   Access-Control-Allow-Methods: *
   Access-Control-Allow-Headers: *
   ```

---

## Update Production Domains

When you deploy frontend to Vercel, update the allowed origins:

```python
allow_origins=[
    "http://localhost:3000",                    # Keep for local dev
    "https://YOUR-APP.vercel.app",             # Your Vercel domain
    "https://safe-outdoor.vercel.app",         # Production domain
    "https://safeoutdoor.app",                 # Custom domain (if any)
]
```

Remove the `"*"` wildcard for security.

---

## Environment Variables Approach (Advanced)

For better configuration management, you can use environment variables:

### In `backend/app/config.py`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... existing settings ...
    
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    @property
    def cors_origins(self) -> list[str]:
        """Parse allowed origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
```

### In `backend/.env`:

```bash
ALLOWED_ORIGINS=http://localhost:3000,https://safe-outdoor.vercel.app,https://safeoutdoor.app
```

### In `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

This way you can configure origins via environment variables on Render.com without code changes.

---

## Status

✅ **CORS Configuration Updated**

**File:** `backend/app/main.py`  
**Line:** 48-56  
**Change:** Hardcoded allowed origins list

**Next Steps:**
1. Commit and push changes
2. Redeploy backend on Render.com
3. Test frontend connection
4. Remove `"*"` wildcard for production

---

**Last Updated:** October 4, 2025  
**Backend URL:** https://safeoutdoor-backend-3yse.onrender.com
