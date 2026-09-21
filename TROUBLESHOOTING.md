# Troubleshooting Guide

## FIXED: "Nothing is working"

**Problem**: Backend was up but endpoints returned errors

**Cause**: Orchestrator wasn't initialized

**Solution**: Now fixed! Use the startup script:

```bash
./start_system.sh
```

This automatically:
1. Starts the backend
2. Initializes the orchestrator
3. Tests all endpoints
4. Reports status

---

## Common Issues & Fixes

### Issue 1: Backend won't start

**Symptoms**:
- Port 5001 already in use
- Can't connect to localhost:5001

**Fix**:
```bash
# Stop everything
./stop_system.sh

# Start fresh
./start_system.sh
```

**Manual fix**:
```bash
# Kill process on port 5001
lsof -ti:5001 | xargs kill -9

# Start backend
cd backend && python3 api.py
```

---

### Issue 2: Orchestrator not initialized

**Symptoms**:
```json
{"error": "Orchestrator not initialized"}
```

**Fix**:
```bash
curl -X POST http://localhost:5001/init \
  -H "Content-Type: application/json" \
  -d '{"min_age": 18, "max_age": 100, "use_clip": true}'
```

Or just use:
```bash
./start_system.sh
```

---

### Issue 3: UI loads but shows no data

**Symptoms**:
- UI appears (dark theme visible)
- Stats show all zeros
- No profiles

**Expected**: This is normal! You haven't synced any profiles yet.

**Fix**: Get your Tinder X-Auth-Token and sync profiles:
```bash
# See: GET_REAL_TINDER_TOKEN.md
python3 sync_tinder_now.py
```

---

### Issue 4: 400/401 errors on endpoints

**Symptoms**:
```
400 Bad Request
401 Unauthorized
```

**Causes**:
1. Orchestrator not initialized → Use `start_system.sh`
2. Invalid token → Get real X-Auth-Token from Network tab
3. Expired token → Login to Tinder again, get new token

**Fix**:
```bash
# Restart with auto-init
./start_system.sh

# Test token
python3 test_tinder_token.py
```

---

### Issue 5: Can't get Tinder token

**Problem**: APISID cookie doesn't work

**Solution**: You need the **X-Auth-Token** from Network tab, NOT the cookie!

**Steps**:
1. Open tinder.com in browser
2. DevTools (F12) > Network tab
3. Filter: "gotinder"
4. Click someone's profile
5. Look at Request Headers for "X-Auth-Token"
6. Copy that value

**Full guide**: GET_REAL_TINDER_TOKEN.md

---

### Issue 6: Rate limited / banned

**Symptoms**:
```
ERROR: Rate limited by Tinder
ERROR: BAN DETECTED
```

**Fix**: The system automatically enters cooldown (1 hour)

**Check status**:
```python
from dating_agent.rate_limiter import get_rate_limiter
limiter = get_rate_limiter('tinder')
stats = limiter.get_stats('tinder')
print(f"Cooldown remaining: {stats['cooldown_remaining']:.0f}s")
```

**Prevention**: The rate limiter is already conservative (4 req/min). This shouldn't happen unless you used the wrong token.

---

### Issue 7: Dark theme not showing

**Symptoms**: UI looks white/bright instead of dark

**Fix**: Hard refresh the page:
- Windows/Linux: Ctrl + Shift + R
- Mac: Cmd + Shift + R

Or clear cache:
```bash
# Restart backend
./start_system.sh
```

---

### Issue 8: Database errors

**Symptoms**:
```
table profiles has no column named platform_id
```

**Fix**: Database schema was already fixed. If you still see this:
```bash
# Delete old database
rm dating_agent.db

# Restart system (creates fresh DB)
./start_system.sh
```

---

### Issue 9: Frontend not loading

**Symptoms**:
- Can't open http://localhost:5001
- Connection refused

**Fix**:
```bash
# Check if backend is actually running
curl http://localhost:5001/health

# If not, start it
./start_system.sh

# Check logs
tail -f backend.log
```

---

### Issue 10: Python module errors

**Symptoms**:
```
ModuleNotFoundError: No module named 'flask'
ModuleNotFoundError: No module named 'dating_agent'
```

**Fix**:
```bash
# Install dependencies
uv pip install Flask Flask-CORS requests numpy Pillow pydantic

# Make sure you're in the right directory
pwd
# Should show: .../dating-agent

# Check if dating_agent exists
ls dating_agent/
```

---

## Quick Diagnostics

Run this to check everything:

```bash
#!/bin/bash
echo "=== SYSTEM DIAGNOSTICS ==="
echo ""

echo "1. Backend status:"
if curl -s http://localhost:5001/health > /dev/null 2>&1; then
    echo "   [OK] Backend is running"
else
    echo "   [FAIL] Backend is NOT running"
fi

echo "2. Orchestrator status:"
STATS=$(curl -s http://localhost:5001/stats)
if echo "$STATS" | grep -q "error"; then
    echo "   [FAIL] Orchestrator not initialized"
else
    echo "   [OK] Orchestrator ready"
fi

echo "3. Database:"
if [ -f dating_agent.db ]; then
    echo "   [OK] Database exists"
else
    echo "   [WARN] No database yet"
fi

echo "4. Credentials:"
if [ -f tinder_creds.json ]; then
    echo "   [OK] Tinder creds found"
else
    echo "   [WARN] No Tinder token yet"
fi

echo ""
echo "=== END DIAGNOSTICS ==="
```

---

## Working System Checklist

If everything is working, you should see:

- [ ] Backend responds at http://localhost:5001
- [ ] `/health` returns `{"status": "ok"}`
- [ ] `/stats` returns counts (not "error")
- [ ] `/matches/mutual` returns `{"count": 0, "matches": []}`
- [ ] UI loads with dark theme
- [ ] No errors in browser console (F12)
- [ ] No errors in backend.log

---

## Getting Help

If nothing here fixes your issue:

1. **Check logs**:
   ```bash
   tail -50 backend.log
   ```

2. **Test endpoints manually**:
   ```bash
   curl http://localhost:5001/health
   curl http://localhost:5001/stats
   ```

3. **Check what's running**:
   ```bash
   lsof -i :5001
   ps aux | grep python
   ```

4. **Full restart**:
   ```bash
   ./stop_system.sh
   sleep 2
   ./start_system.sh
   ```

5. **Fresh start**:
   ```bash
   ./stop_system.sh
   rm dating_agent.db
   rm .backend.pid
   ./start_system.sh
   ```

---

## System Requirements

Make sure you have:
- Python 3.7+
- Flask, Flask-CORS, requests
- Modern web browser
- Tinder account (for token)

---

## Current Status

After running `./start_system.sh`, you should see:

```
========================================================================
                    SYSTEM READY!
========================================================================

Backend:     http://localhost:5001        [RUNNING]
UI:          http://localhost:5001        [DARK THEME]
```

If you don't see this, something went wrong. Check the logs!

---

## Quick Fixes Summary

| Problem | Quick Fix |
|---------|-----------|
| Nothing works | `./start_system.sh` |
| Backend down | `cd backend && python3 api.py &` |
| Not initialized | `curl -X POST http://localhost:5001/init -d '{}'` |
| Wrong token | Get X-Auth-Token from Network tab |
| Database errors | `rm dating_agent.db` then restart |
| UI not loading | Hard refresh (Ctrl+Shift+R) |
| Rate limited | Wait for cooldown (~1 hour) |

---

**Most common issue**: Orchestrator not initialized  
**Most common fix**: Run `./start_system.sh`
