# Production Deployment Guide

## Frontend Production Error Fix

### Problem
The frontend application shows "Application error: a client-side exception has occurred" in production but works fine locally.

### Root Cause
The frontend is trying to make API calls to `http://localhost:8000/api/v1` in production because the `NEXT_PUBLIC_API_BASE_URL` environment variable is not set.

### Solution

#### 1. Set Environment Variables in Production

**For Vercel:**
```bash
# In your Vercel dashboard or via CLI
vercel env add NEXT_PUBLIC_API_BASE_URL
# Enter: https://api.superconnectai.com/api/v1
```

**For Netlify:**
```bash
# In your Netlify dashboard, go to Site settings > Environment variables
NEXT_PUBLIC_API_BASE_URL=https://api.superconnectai.com/api/v1
```

**For other platforms:**
Set the environment variable `NEXT_PUBLIC_API_BASE_URL` to your production API URL.

#### 2. Backend API URL Options

Choose one of these patterns for your production API:

1. **Subdomain (Recommended):**
   - `https://api.superconnectai.com/api/v1`

2. **Path-based:**
   - `https://superconnectai.com/api/v1`

3. **Different domain:**
   - `https://your-backend-domain.com/api/v1`

#### 3. Backend CORS Configuration

Ensure your backend allows requests from your frontend domain. The current configuration allows all origins (`allow_origins=["*"]`), which works but is less secure.

For better security, update `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.superconnectai.com",
        "https://superconnectai.com",
        "http://localhost:3000"  # for local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 4. SSL/HTTPS Considerations

- Ensure your production API uses HTTPS
- Mixed content (HTTPS frontend calling HTTP API) will be blocked by browsers
- Use the same protocol (HTTPS) for both frontend and backend in production

#### 5. Testing the Fix

After setting the environment variable:

1. **Redeploy your frontend** (environment variables require a rebuild)
2. **Check browser console** for the log: "API_BASE_URL configured as: [your-api-url]"
3. **Verify API calls** are going to the correct URL
4. **Test key functionality** like login and search

#### 6. Debugging Production Issues

The updated code now includes enhanced logging. Check browser console for:

- `API_BASE_URL configured as: [url]` - Shows which API URL is being used
- Detailed error messages with context about which API call failed
- Network error details if the API server is unreachable

### Quick Fix Commands

```bash
# 1. Set environment variable in your deployment platform
# 2. Redeploy frontend
# 3. Check browser console for API_BASE_URL log
# 4. Test the application
```

### Environment Variable Priority

The API URL is determined in this order:

1. `NEXT_PUBLIC_API_BASE_URL` environment variable (highest priority)
2. Auto-detection based on domain (for www.superconnectai.com)
3. Localhost fallback for development (lowest priority)

This ensures the app works in all environments while being configurable for production.