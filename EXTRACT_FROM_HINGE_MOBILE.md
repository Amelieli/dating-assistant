# Extract Session Token from Hinge Mobile App

Since Hinge doesn't have a web app, we need to extract the session token from the mobile app.

## Method 1: Using Charles Proxy (Easiest)

### Setup (10 minutes)

1. **Download Charles Proxy**
   - https://www.charlesproxy.com/download/
   - Free trial works fine

2. **Configure Your Phone**
   
   **iPhone:**
   - Settings > Wi-Fi > (your network) > Configure Proxy
   - Manual > Server: your.computer.ip > Port: 8888
   - Install Charles SSL certificate (Charles > Help > SSL Proxying)
   
   **Android:**
   - Settings > Wi-Fi > (your network) > Proxy > Manual
   - Hostname: your.computer.ip > Port: 8888
   - Install Charles SSL certificate from chls.pro/ssl

3. **Start Charles Proxy**
   - Open Charles on computer
   - Proxy > SSL Proxying Settings
   - Add: prod-api.hingeaws.net

4. **Open Hinge on Phone**
   - Close and reopen Hinge app
   - Let it load your matches

5. **Find the Token in Charles**
   - Look for requests to `prod-api.hingeaws.net`
   - Check the Headers
   - Find `Authorization: Bearer <token>`
   - Copy the token part

6. **Save Token**
   ```bash
   echo '{"hinge_token": "YOUR_TOKEN_HERE", "user_id": "YOUR_USER_ID"}' > hinge_creds.json
   ```

---

## Method 2: Using mitmproxy (Free, Command Line)

### Setup

```bash
# Install mitmproxy
pip install mitmproxy

# Start proxy
mitmweb
```

### Configure Phone
- Point phone proxy to your computer IP:8080
- Install mitmproxy certificate from mitm.it
- Open Hinge app

### Find Token
- Watch mitmweb interface at http://localhost:8081
- Look for `prod-api.hingeaws.net` requests
- Find Authorization header

---

## Method 3: Android APK Inspection (Technical)

If you have an Android phone:

### Extract APK

```bash
# On phone (with adb)
adb shell pm list packages | grep hinge
adb shell pm path co.hinge.app
adb pull /data/app/~~...../base.apk hinge.apk
```

### Decompile

```bash
# Install jadx
brew install jadx  # or download from github.com/skylot/jadx

# Decompile
jadx hinge.apk -d hinge_source

# Search for Firebase key
grep -r "AIzaSy" hinge_source/
grep -r "FIREBASE" hinge_source/
```

The key will be in the source code somewhere!

---

## Method 4: Use Tinder Instead!

**Easier solution**: Tinder HAS a web app!

```bash
python3 get_tinder_token.py
```

Then:
1. Login at tinder.com
2. Extract token from cookies
3. Use with the system

---

## Using the Extracted Token

Once you have the Hinge token:

```python
from dating_agent.profile_aggregator import profile_aggregator
import json

agg = profile_aggregator()

# Set credentials manually
agg.hinge_auth.credentials = {
    'hinge_token': 'YOUR_TOKEN_HERE',
    'user_id': 'YOUR_USER_ID',
    'authenticated_at': '2026-01-23T12:00:00'
}

# Now you can sync!
sync = agg.run_full_sync(
    hinge_user_id='YOUR_USER_ID',
    limit=50,
    find_duplicates=True
)

print(f"Success! Fetched {sync['platforms']['hinge']['profiles_fetched']} profiles")
```

---

## Recommended Approach

**For quick testing**: Use Tinder (has web app)
```bash
python3 get_tinder_token.py
```

**For Hinge data**: Use Charles Proxy method (easiest mobile extraction)

**For advanced users**: APK decompilation + Firebase key extraction

---

## Why This is Needed

- Hinge is **mobile-only** (no web app)
- Firebase keys are embedded in mobile app
- Session tokens require intercepting mobile traffic
- Or extracting from app binary

This is normal for reverse-engineering mobile-only apps!
