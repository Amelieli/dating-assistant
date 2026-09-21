# Which Tinder Cookie to Get

## From Your Screenshot

Looking at your cookies list, grab this one:

```
APISID
```

**That's the main auth token for Tinder!**

## Backup Cookies (if APISID doesn't work)

Also copy these values:

```
HSID
__Secure-1PAPISID
__Secure-3PAPISID
```

## How to Get the Values

### Method 1: DevTools (Easiest)

1. **Open tinder.com and login**

2. **Open DevTools**
   - Press F12 (Windows/Linux)
   - Or Cmd+Option+I (Mac)

3. **Go to Application Tab**
   - Click "Cookies" on left sidebar
   - Click "https://tinder.com"

4. **Find APISID**
   - Look in the list for "APISID"
   - Double-click the VALUE column
   - Copy the value (long string)

5. **Run the script**
   ```bash
   python3 get_tinder_token.py
   ```
   
6. **Paste the APISID value** when prompted

## What Each Cookie Does

| Cookie | Purpose | Need It? |
|--------|---------|----------|
| **APISID** | Main auth token | YES! |
| **HSID** | Session ID | Maybe |
| **__Secure-1PAPISID** | Secure session | Backup |
| **__Secure-3PAPISID** | Cross-site auth | Backup |
| `__ps_did` | Device ID | No |
| `_ga` | Google Analytics | No |
| `AWSALB*` | Load balancer | No |
| `lang` | Language setting | No |

## Quick Test

Once you have the APISID value:

```python
import requests

# Your APISID value
apisid = "YOUR_APISID_VALUE_HERE"

# Test it
response = requests.get(
    "https://api.gotinder.com/v2/recs/core",
    headers={
        "X-Auth-Token": apisid,
        "User-Agent": "Mozilla/5.0"
    }
)

if response.status_code == 200:
    print("Token works! You have access!")
    print(f"Found {len(response.json().get('results', []))} profiles")
else:
    print(f"Error: {response.status_code}")
    print("Try the backup cookies")
```

## If APISID Doesn't Work

Try this order:

1. **APISID** (most common)
2. **HSID** (alternate session ID)
3. **Check Network tab** for actual API requests
   - Filter by "gotinder.com"
   - Look at request headers
   - Find "X-Auth-Token" or "Authorization"

## Example Cookie Values

Your cookie value will look something like:

```
APISID: AJfY9f8j3KLmno2PqrstUvwxYz1234567890ABCDEFG
```

**Copy everything after the colon!**

## Using the Token

Once you have it:

```bash
# Save to file
echo '{"tinder_token": "YOUR_APISID_HERE"}' > tinder_creds.json

# Then sync profiles
python3 << 'EOF'
from dating_agent.profile_aggregator import profile_aggregator
import json

with open('tinder_creds.json') as f:
    creds = json.load(f)

agg = profile_aggregator()
agg.tinder_auth.credentials = {
    'auth_token': creds['tinder_token'],
    'user_id': 'from_web'
}

sync = agg.run_full_sync(tinder_user_id='from_web', limit=50)
print(f"Success! Got {sync['platforms']['tinder']['profiles_fetched']} profiles")
EOF
```

## Troubleshooting

### "Invalid token" error?
- Make sure you copied the full value
- No extra spaces or quotes
- Try the backup cookies (HSID, etc.)

### "Unauthorized" error?
- Your session might have expired
- Logout and login to Tinder again
- Get a fresh APISID value

### Still not working?
- Use Network tab method instead
- Look for actual X-Auth-Token in API requests
- That's the real auth token Tinder uses

---

## Summary

**Grab this cookie: APISID**

Then run:
```bash
python3 get_tinder_token.py
# Paste the APISID value when asked
```

That's it! You'll have real Tinder data with rate limiting!
