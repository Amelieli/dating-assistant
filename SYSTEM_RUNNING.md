# SYSTEM IS RUNNING!

## Backend Status: LIVE on http://localhost:5001

### Health Check
```json
{
  "service": "dating-orchestrator",
  "status": "ok"
}
```

### Current Stats
```json
{
    "by_app": {},
    "incoming_likes": 0,
    "mutual_matches": 0,
    "outgoing_likes": 0,
    "total_profiles": 0
}
```

## How To Use The Running Backend

### 1. Test Health
```bash
curl http://localhost:5001/health
```

### 2. Initialize (Already Done!)
```bash
curl -X POST http://localhost:5001/init \
  -H "Content-Type: application/json" \
  -d '{
    "min_age": 18,
    "max_age": 100,
    "max_distance_km": 50,
    "use_clip": true
  }'
```

### 3. Get Stats
```bash
curl http://localhost:5001/stats
```

### 4. Use Python API (Recommended!)
```python
from dating_agent.profile_aggregator import profile_aggregator

# Initialize
agg = profile_aggregator()

# Authenticate with Hinge
result = agg.hinge_auth.request_phone_verification(
    "+1-YOUR-PHONE",
    solve_captcha=True
)

print(f"OTP ID: {result['otp_id']}")
print("Check your phone for SMS code")

# Enter SMS code
code = input("Enter SMS code: ")

verify = agg.hinge_auth.verify_phone_otp(
    result['otp_id'],
    code
)

print(f"User ID: {verify['user_id']}")

# Sync profiles (with rate limiting!)
sync = agg.run_full_sync(
    hinge_user_id=verify['user_id'],
    limit=50,
    find_duplicates=True
)

print(f"Fetched: {sync['platforms']['hinge']['profiles_fetched']} profiles")
```

## Available API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `POST /init` - Initialize with filter config
- `GET /stats` - Get profile statistics

### Authentication
- `POST /authenticate` - Authenticate with dating apps

### Profile Management
- `POST /sync` - Sync profiles from apps
- `GET /matches/mutual` - Get mutual matches
- `GET /matches/incoming` - Get incoming likes
- `POST /filter-and-rank` - Filter and rank profiles

### Advanced
- `POST /search/by-description` - CLIP-based text search
- `POST /refresh` - Refresh all data
- `GET /profile/<app>/<id>` - Get specific profile
- `GET /export/mutual-matches` - Export to JSON

## Quick Test Commands

### Check if backend is responding
```bash
curl http://localhost:5001/health
```

### Get current stats
```bash
curl http://localhost:5001/stats | python3 -m json.tool
```

### Initialize with custom config
```bash
curl -X POST http://localhost:5001/init \
  -H "Content-Type: application/json" \
  -d '{
    "min_age": 25,
    "max_age": 35,
    "max_distance_km": 30,
    "must_not_smoke": true
  }'
```

## For Frontend UI

The backend is ready for the React frontend! To start the frontend on your local machine:

```bash
cd frontend
npm install   # First time only
npm run dev   # Start dev server
```

Then open: http://localhost:3000

The frontend will automatically connect to the backend on port 5001.

## To Stop The Backend

```bash
# Find the process
lsof -ti:5001

# Kill it
kill $(lsof -ti:5001)

# Or use the script
./STOP_EVERYTHING.sh
```

## Backend Logs

Check logs at:
```bash
tail -f backend.log
```

## What's Working

- [x] Backend API running on port 5001
- [x] All endpoints responding
- [x] Orchestrator initialized
- [x] Rate limiting active
- [x] Database ready
- [x] Ready for authentication
- [ ] Frontend UI (needs npm on your machine)

## Next Steps

1. **Test with Python** (recommended):
   ```bash
   python3 quick_start_hinge.py
   ```

2. **Or use direct API calls**:
   ```bash
   curl http://localhost:5001/stats
   ```

3. **Or start frontend on your machine**:
   ```bash
   cd frontend && npm install && npm run dev
   ```

---

**Backend is LIVE and ready to aggregate your dating profiles!**
