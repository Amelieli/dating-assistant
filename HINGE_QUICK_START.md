# Hinge Firebase Key - Quick Start

## TL;DR - Charles Proxy Method (Fastest)

**Time: 20 minutes | Difficulty: Medium | Works: Both iPhone and Android**

### Step 1: Download Charles Proxy
```
https://www.charlesproxy.com/download/
```

### Step 2: Find Your Computer's IP
```bash
# Mac
ipconfig getifaddr en0

# Linux
hostname -I

# Windows
ipconfig | findstr IPv4
```

### Step 3: On Your Computer - Install Certificate
- Open Charles
- **Help > Install Charles Root Certificate**
- System will ask for password

### Step 4: On Your Phone - Set Proxy

**iPhone:**
1. Settings > Wi-Fi > Your Network > Info icon
2. HTTP Proxy > Manual
3. Server: **[Your computer IP from Step 2]**
4. Port: **8888**
5. Settings > General > Profiles > Install Charles Cert

**Android:**
1. Settings > Wi-Fi > Long-press network > Modify
2. Advanced options > Proxy > Manual
3. Hostname: **[Your computer IP]**
4. Port: **8888**
5. Settings > Security > Install cert from storage

### Step 5: Configure Charles for Hinge
- **Proxy > SSL Proxying Settings > Add**
- Host: `*.hingeaws.net`
- Port: 443
- Click OK

### Step 6: Capture Traffic
1. Make sure Charles is recording (red dot enabled)
2. Open Hinge app on phone
3. Click on a profile or perform any action
4. Look in Charles for requests to `prod-api.hingeaws.net`

### Step 7: Extract Firebase Key

Click on a request to hingeaws.net:
- Click **Request** tab (top right)
- Scroll down to see the full request
- Look for these in the JSON or headers:
  - `"firebaseKey": "AIzaSy..."`
  - `X-Firebase-Token: ...`
  - Authorization header

**Or check Response:**
- Click **Response** tab
- Search for `AIzaSy` (Firebase key start)

### Step 8: Save the Key

Once you find it (looks like: `AIzaSyDyZ4g7OnN3RjL4VqKV0mVjLyy-tlqDk20`):

```bash
# Update the code
# Edit: hinge_auth_real.py, line 27
FIREBASE_API_KEY = "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

### Step 9: Test It!

```bash
# Request OTP
curl -X POST http://localhost:5001/hinge/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1-785-431-4064"}'

# You should get: {"status": "success"}
```

---

## APK Decompilation (Android Only - Advanced)

**If Charles Proxy doesn't work:**

```bash
# 1. Extract APK
adb shell pm list packages | grep hinge
adb shell pm path co.hinge.app
adb pull /data/app/.../base.apk

# 2. Decompile (requires jadx)
# Mac: brew install jadx
jadx base.apk -d hinge_source

# 3. Find Firebase key
grep -r "AIzaSy" hinge_source/
grep -r "firebase" hinge_source/ | grep -i key

# 4. Look in these files:
# - hinge_source/resources/values/strings.xml
# - Any Java file with "firebase" in name
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No traffic in Charles | Check phone proxy is set to correct IP and port 8888 |
| Certificate errors | Uninstall and reinstall Charles cert on phone |
| 403 Forbidden in Charles | Make sure SSL proxying is enabled for `*.hingeaws.net` |
| Can't find key in traffic | Try different requests (swipe profile, open matches, etc.) |
| APK extraction fails | Use online decompiler: https://www.decompiler.com/ |

---

## What You Need

- Charles Proxy or mitmproxy
- Your phone on same WiFi as computer
- Hinge app installed on phone
- Your computer's IP address

---

## Alternative: mitmproxy (Command Line)

```bash
# Install
pip install mitmproxy

# Start
mitmweb

# Phone proxy: localhost:8080
# Then open http://localhost:8081 in browser
```

---

## Once You Have the Key

The system is ready! Just:

1. Update `hinge_auth_real.py` with the Firebase key
2. Run:
   ```bash
   ./start_system.sh
   ```
3. Open http://localhost:5001
4. Use the Hinge authentication form
5. Get your matches!

---

## Key Location Hints

The Firebase key might be in:
- Network request headers (easiest)
- JSON response body
- App initialization code
- `strings.xml` in APK
- BuildConfig files

Common header names:
- `X-Firebase-Token`
- `Authorization`
- `X-Goog-API-Key`
- Custom headers

---

**Recommended: Start with Charles Proxy!**

It's the easiest visual method and works great.

Once you get the key, everything else just works!
