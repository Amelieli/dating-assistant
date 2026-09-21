# Extract Firebase Key from Hinge Mobile App

Since Hinge is mobile-only, we need to extract the Firebase key from the app. Here are the methods:

---

## Method 1: Charles Proxy (Easiest for iPhone/Android)

### Setup (20 minutes)

**Step 1: Download Charles Proxy**
- Download: https://www.charlesproxy.com/download/
- Free trial works perfectly
- Available for Mac, Windows, Linux

**Step 2: Install Charles SSL Certificate**

On your computer:
1. Open Charles Proxy
2. Go to **Help > Install Charles Root Certificate**
3. It will be installed on your computer

**Step 3: Configure Your Phone**

**For iPhone:**
1. Go to **Settings > Wi-Fi**
2. Select your network > Tap the info icon
3. Scroll to **HTTP Proxy > Configure Proxy > Manual**
4. Set:
   - Server: Your computer's IP (find with `ipconfig getifaddr en0` on Mac)
   - Port: 8888
5. Go to **Settings > General > Profiles > Certificates**
6. Install Charles certificate

**For Android:**
1. Go to **Settings > Wi-Fi**
2. Long-press your network > Modify
3. Check **Show advanced options**
4. Set **Proxy > Manual**
5. Hostname: Your computer's IP
6. Port: 8888
7. Go to Settings > Security > Install from storage
8. Install Charles certificate

**Step 4: Configure Charles for Hinge**

On your computer in Charles:
1. **Proxy > SSL Proxying Settings**
2. Click **Add**
3. Host: `*.hingeaws.net` (Hinge's API server)
4. Port: 443
5. Click OK

**Step 5: Capture Hinge Traffic**

1. Open Charles (should be recording)
2. Open Hinge app on your phone
3. Let it load (you'll see traffic in Charles)
4. Look for requests to `prod-api.hingeaws.net` or `hingeaws.net`

**Step 6: Find Firebase Key**

In Charles, look for requests with these patterns:
- Any POST/GET to `prod-api.hingeaws.net`
- Click on the request
- Go to **Request > Headers** tab
- Look for:
  - `Authorization: Bearer <token>`
  - `X-Firebase-Token: ...`
  - `Firebase-Key: ...`

**Step 7: Find API Key in Response**

Or check the **Request > JSON** tab if it's a POST:
```json
{
  "firebaseKey": "AIzaSy...",
  "apiKey": "..."
}
```

---

## Method 2: mitmproxy (Free, Command Line)

### Quick Setup

```bash
# Install mitmproxy
pip install mitmproxy

# Start mitmproxy web interface
mitmweb
```

Open: http://localhost:8081

**Configure phone:**
- Settings > Wi-Fi > Manual Proxy
- Hostname: Your computer IP
- Port: 8080
- Install cert from mitm.it

**Capture Hinge:**
1. Open Hinge app
2. Watch requests in mitmweb
3. Filter by "hingeaws"
4. Look for Firebase key in headers/responses

---

## Method 3: Android APK Decompilation (Advanced)

### For Android Users Only

**Step 1: Extract APK**

```bash
# List Hinge package
adb shell pm list packages | grep hinge

# Find Hinge package path
adb shell pm path co.hinge.app

# Pull APK
adb pull /data/app/.../base.apk hinge.apk
```

**Step 2: Decompile APK**

```bash
# Install jadx
# Mac: brew install jadx
# Or download from: https://github.com/skylot/jadx/releases

# Decompile
jadx hinge.apk -d hinge_source
```

**Step 3: Find Firebase Key**

```bash
# Search for Firebase key
cd hinge_source
grep -r "AIzaSy" .
grep -r "FIREBASE" .
grep -r "firebase_key" .
grep -r "hingeaws" .

# Or search for specific strings
grep -r "prod-api.hingeaws.net" .
```

**Step 4: Look in These Files**

Common locations:
- `values/strings.xml` - Contains API keys
- `BuildConfig.java` - Build-time constants
- `res/values/build_config.xml`
- Any file with "firebase" in the name

---

## Method 4: Frida (Dynamic Instrumentation - Advanced)

For advanced users who want to hook the app:

```bash
# Install frida
pip install frida frida-tools

# Start frida server on phone
frida-server &

# Create hook script (hook.js)
```

```javascript
// hook.js
Java.perform(function() {
    var Firebase = Java.use("com.google.firebase.FirebaseApp");
    
    Firebase.getInstance.overload().implementation = function() {
        var result = this.getInstance();
        console.log("Firebase instance obtained!");
        return result;
    };
    
    // Hook HTTP requests
    var OkHttp = Java.use("okhttp3.OkHttpClient");
    OkHttp.newCall.overload("okhttp3.Request").implementation = function(request) {
        console.log("Request: " + request.url());
        console.log("Headers: " + request.headers());
        return this.newCall(request);
    };
});
```

```bash
# Run hook
frida -U -l hook.js -f co.hinge.app
```

---

## Method 5: Burp Suite Community (Free)

Similar to Charles Proxy but open-source alternative:

1. Download: https://portswigger.net/burp/communitydownload
2. Configure phone proxy to Burp Suite (default port 8080)
3. Install Burp certificate
4. Filter traffic for "hingeaws"
5. Find API key in requests

---

## What You're Looking For

The Firebase key looks like:

```
AIzaSyDyZ4g7OnN3RjL4VqKV0mVjLyy-tlqDk20
```

**Characteristics:**
- Starts with `AIzaSy`
- About 39 characters total
- Mix of letters, numbers, hyphens
- Used for Firebase authentication

---

## Where It's Used

Once you have it, the Hinge auth will:

```python
from dating_agent.profile_aggregator import profile_aggregator

agg = profile_aggregator()

# Set Firebase key
agg.hinge_auth.credentials = {
    'firebase_key': 'AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    'user_id': 'your_hinge_user_id'
}

# Then request OTP
result = agg.hinge_auth.request_phone_verification('+1-555-123-4567')
```

---

## Recommended Method

**For Most Users: Charles Proxy**

Why?
- Visual interface (easier than command line)
- Works on both iOS and Android
- No APK decompilation needed
- One-time setup, reusable for future

**Difficulty: Medium**  
**Time: 20-30 minutes**  
**Success Rate: High**

---

## Troubleshooting

### "Can't see Hinge traffic"

1. Verify phone proxy is set correctly
2. Check Charles is recording (red dot enabled)
3. Restart Hinge app
4. Make sure SSL proxying is enabled for `*.hingeaws.net`

### "Certificate errors on phone"

1. Uninstall certificate
2. Reinstall from Charles > Help
3. Restart phone
4. Try again

### "No requests showing"

1. Is phone on same WiFi as computer?
2. Is firewall blocking port 8888?
3. Restart Charles and phone
4. Try a different request (swipe, open profile, etc.)

### "APK decompilation failing"

1. Make sure you have correct APK (base.apk)
2. Update jadx: `brew upgrade jadx`
3. Try online decompiler: https://www.decompiler.com/

---

## Quick Reference

**Charles Proxy Steps:**
```
1. Download Charles
2. Install cert on computer
3. Set phone proxy to Charles (port 8888)
4. Install cert on phone
5. Configure SSL proxying for *.hingeaws.net
6. Open Hinge app
7. Find requests to hingeaws.net
8. Look for Firebase key in headers or JSON
```

**APK Decompilation Steps:**
```
1. adb pull base.apk
2. jadx hinge.apk -d hinge_source
3. grep -r "AIzaSy" hinge_source/
4. Find and copy key
```

---

## Once You Have the Key

Update `hinge_auth_real.py`:

```python
FIREBASE_API_KEY = "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

Then use the system:

```bash
# Request OTP
curl -X POST http://localhost:5001/hinge/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1-555-123-4567"}'

# Verify OTP
curl -X POST http://localhost:5001/hinge/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"otp_id": "...", "code": "123456"}'

# Sync profiles
curl -X POST http://localhost:5001/hinge/sync \
  -H "Content-Type: application/json" \
  -d '{"user_id": "your_user_id", "limit": 50}'
```

---

## Why This Works

- Hinge API requires Firebase authentication
- Firebase key is embedded in the app
- Proxying intercepts the requests where the key is used
- APK decompilation extracts it from the binary

---

**I recommend Charles Proxy for easiest results!**

Let me know which method you want to try and I'll guide you through it step-by-step.
