# Getting REAL Data - Your Options

## The Situation

**Hinge**: Mobile-only app (iOS/Android) - NO web version  
**Tinder**: Has web app at tinder.com - EASY to use  
**Match.com**: Has web app - Medium difficulty

---

## EASIEST Option: Use Tinder (Recommended!)

Tinder has a **real web app** at https://tinder.com

### Quick Start (5 minutes)

```bash
# Step 1: Extract your Tinder token
python3 get_tinder_token.py
```

This will:
1. Open https://tinder.com in your browser
2. You login with your account
3. Extract your session token from cookies
4. Save it to `tinder_creds.json`

### Then Sync Profiles

```python
# Use the token to fetch real profiles
python3 << 'EOF'
from dating_agent.profile_aggregator import profile_aggregator
import json

# Load your token
with open('tinder_creds.json') as f:
    creds = json.load(f)

agg = profile_aggregator()

# Set credentials
agg.tinder_auth.credentials = {
    'auth_token': creds['tinder_token'],
    'user_id': 'from_web',
    'device_id': 'web_browser'
}

# Sync with rate limiting
sync = agg.run_full_sync(
    tinder_user_id='from_web',
    limit=50,
    find_duplicates=True
)

print(f"Success! Fetched {sync['platforms']['tinder']['profiles_fetched']} profiles")

# View profiles
profiles = agg.get_all_profiles('tinder')
for p in profiles[:5]:
    print(f"- {p['name']}, {p['age']} ({p['location']})")
EOF
```

**That's it!** Real Tinder data with rate limiting.

---

## Medium Option: Extract from Hinge Mobile

Since Hinge doesn't have a web app, you need to extract from the mobile app.

### Method A: Charles Proxy (Easiest)

1. **Download Charles Proxy**  
   https://www.charlesproxy.com/download/

2. **Configure your phone**
   - Point proxy to your computer
   - Install Charles SSL certificate

3. **Open Hinge app**
   - Watch Charles for requests to `prod-api.hingeaws.net`
   - Find `Authorization: Bearer <token>` header
   - Copy the token

4. **Use the token**
   ```python
   agg.hinge_auth.credentials = {
       'hinge_token': 'YOUR_TOKEN_HERE',
       'user_id': 'YOUR_USER_ID'
   }
   ```

**Full guide**: `EXTRACT_FROM_HINGE_MOBILE.md`

### Method B: APK Decompilation (Advanced)

For Android users:

```bash
# Extract APK
adb pull /data/app/.../hinge.apk

# Decompile
jadx hinge.apk -d hinge_source

# Find Firebase key
grep -r "AIzaSy" hinge_source/
```

Update `hinge_auth_real.py` with the key you find.

---

## Comparison

| Method | Difficulty | Time | Data Source |
|--------|-----------|------|-------------|
| **Tinder Web** | Easy | 5 min | tinder.com |
| **Charles Proxy** | Medium | 15 min | Hinge mobile |
| **APK Decompile** | Hard | 30 min | Hinge mobile |

---

## My Recommendation

### For Quick Testing:
```bash
python3 get_tinder_token.py
```

**Why?**
- Tinder has web app
- Easy token extraction
- Same features as Hinge
- Works immediately

### For Hinge Data:
Use Charles Proxy method (see `EXTRACT_FROM_HINGE_MOBILE.md`)

**Why?**
- Visual interface
- Works for both iOS and Android
- One-time setup

---

## What Works Right Now

### Backend + UI
- **Running**: http://localhost:5001
- **Status**: Ready for tokens

### Features Ready
- Rate limiting (4-6 req/min)
- Database storage
- Duplicate detection
- Profile filtering
- Export to JSON

### What You Need
- Valid auth token (Tinder OR Hinge)

---

## Quick Commands

### Get Tinder Token (Easiest!)
```bash
python3 get_tinder_token.py
```

### Test with Python
```python
from dating_agent.profile_aggregator import profile_aggregator
agg = profile_aggregator()
# Set token, then sync
```

### Open UI
```
http://localhost:5001
```

---

## Next Steps

1. **Choose your platform**:
   - Tinder (easy, 5 min)
   - Hinge (medium, 15 min)

2. **Extract token**:
   - Tinder: `python3 get_tinder_token.py`
   - Hinge: Follow `EXTRACT_FROM_HINGE_MOBILE.md`

3. **Sync profiles**:
   - Use Python or UI
   - Rate limiting protects you
   - Real data appears!

---

## Files Created

- `get_tinder_token.py` - Extract from Tinder web (EASY)
- `EXTRACT_FROM_HINGE_MOBILE.md` - Extract from Hinge mobile
- `REAL_DATA_OPTIONS.md` - This file

---

## Bottom Line

**Tinder is easier** because it has a web app.  
**Hinge is possible** but requires mobile app extraction.  

Both work with the same system once you have a token!

**Start here:**
```bash
python3 get_tinder_token.py
```

Then you'll have REAL data in 5 minutes!
