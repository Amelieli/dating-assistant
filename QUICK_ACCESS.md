# Quick Access Guide

## Backend is RUNNING at: http://localhost:5001

### Easy Access URLs (Open in Browser!)

**Welcome Page:**
```
http://localhost:5001/
```

**Health Check:**
```
http://localhost:5001/health
```

**Statistics:**
```
http://localhost:5001/stats
```

**Mutual Matches:**
```
http://localhost:5001/matches/mutual
```

**Export Data:**
```
http://localhost:5001/export/mutual-matches
```

---

## Quick Test Commands

### Check if backend is running:
```bash
curl http://localhost:5001/
```

### Get stats:
```bash
curl http://localhost:5001/stats
```

### Initialize orchestrator:
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

### Get health status:
```bash
curl http://localhost:5001/health
```

---

## To Use With Your Real Credentials

### Option 1: Quick Start Script (Easiest!)
```bash
python3 quick_start_hinge.py
```

### Option 2: Python Interactive
```python
from dating_agent.profile_aggregator import profile_aggregator

agg = profile_aggregator()

# Request OTP
result = agg.hinge_auth.request_phone_verification(
    "+1-YOUR-PHONE",
    solve_captcha=True
)

# Browser opens for reCAPTCHA...
# SMS sent to your phone...

# Verify OTP
code = input("Enter SMS code: ")
verify = agg.hinge_auth.verify_phone_otp(result['otp_id'], code)

# Sync profiles
sync = agg.run_full_sync(
    hinge_user_id=verify['user_id'],
    limit=50
)

print(f"Fetched {sync['platforms']['hinge']['profiles_fetched']} profiles!")
```

---

## All Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome page with endpoint list |
| GET | `/health` | Health check |
| POST | `/init` | Initialize orchestrator |
| POST | `/authenticate` | Authenticate with apps |
| POST | `/sync` | Sync profiles |
| GET | `/stats` | Get statistics |
| GET | `/matches/mutual` | Get mutual matches |
| GET | `/matches/incoming` | Get incoming likes |
| POST | `/filter-and-rank` | Filter profiles |
| POST | `/search/by-description` | CLIP search |
| POST | `/refresh` | Refresh all data |
| GET | `/profile/<app>/<id>` | Get specific profile |
| GET | `/export/mutual-matches` | Export to JSON |

---

## To Stop Backend

```bash
./STOP_EVERYTHING.sh
```

Or:
```bash
kill $(lsof -ti:5001)
```

---

## Need Help?

- **Full docs**: `README_PRODUCTION.md`
- **Live status**: `LIVE_STATUS.md`
- **Production guide**: `PRODUCTION_COMPLETE.md`
- **Backend logs**: `tail -f backend.log`

---

**Backend Status**: RUNNING  
**URL**: http://localhost:5001  
**Ready**: YES
