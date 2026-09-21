# Where to Find Firebase Key

## Quick Answer

**The Firebase key is embedded inside the Hinge mobile app.**

It's NOT in:
- Cookies (like we got Tinder token)
- Public websites
- Browser

It IS in:
- Hinge iOS app binary
- Hinge Android APK
- Network requests when app communicates with Hinge servers

---

## Three Locations to Find It

### Location 1: Network Traffic (EASIEST)

When Hinge app makes requests to its servers, it includes the Firebase key in:
- **Request Headers**
- **Request Body (JSON)**
- **Authorization headers**

**How to get it:**
- Intercept requests with Charles Proxy or mitmproxy
- Open Hinge app
- Firebase key appears in the traffic

**Time:** 20-30 minutes

---

### Location 2: App Binary (Android)

Inside the APK (Android app file):
- `strings.xml` - Plain text configuration
- `BuildConfig.java` - Compiled code
- `res/values/` directory

**How to get it:**
```bash
# Extract APK from phone
adb pull /data/app/.../base.apk

# Decompile to source code
jadx base.apk -d hinge_source

# Search for Firebase key
grep -r "AIzaSy" hinge_source/
```

**Time:** 30-45 minutes

---

### Location 3: Obfuscated Code (iOS)

Inside the IPA (iOS app file):
- Embedded in binary code
- Obfuscated/encrypted
- Harder to find than Android

**How to get it:**
- Use Frida to hook the app at runtime
- Intercept API calls
- Or use Charles Proxy (easier)

**Time:** 45+ minutes (more complex)

---

## Why It's There

Hinge uses Firebase (Google's authentication service).

**Firebase needs an API key to:**
1. Validate phone numbers
2. Send SMS codes
3. Verify OTP
4. Generate auth tokens

**So the key is:**
- Hard-coded in the app
- Used by mobile app to talk to Firebase
- NOT secret (it's in the app binary)
- NOT dangerous to expose (Firebase controls access)

---

## What the Key Looks Like

```
AIzaSyDyZ4g7OnN3RjL4VqKV0mVjLyy-tlqDk20
```

**Format:**
- Starts with: `AIzaSy`
- Length: 39 characters
- Contains: Letters, numbers, hyphens, underscores

---

## Where EXACTLY to Find It

### In Network Traffic (Charles Proxy):

Look in these places:

**1. Request Headers**
```
X-Goog-API-Key: AIzaSy...
X-Firebase-Token: AIzaSy...
Authorization: Bearer AIzaSy...
```

**2. Request JSON Body**
```json
{
  "apiKey": "AIzaSy...",
  "firebaseKey": "AIzaSy...",
  "key": "AIzaSy..."
}
```

**3. URL Parameters**
```
https://identitytoolkit.googleapis.com/v1/accounts/sendOobCode?key=AIzaSy...
```

### In Android APK:

**1. strings.xml**
```bash
grep -r "AIzaSy" hinge_source/resources/values/strings.xml
```

**2. BuildConfig or Constants**
```bash
find hinge_source -name "*.java" | xargs grep "AIzaSy"
```

**3. Config files**
```bash
ls hinge_source/resources/values/
cat hinge_source/resources/values/config.xml
```

---

## Simplest Method: Charles Proxy

**Why this is easiest:**
1. Visual interface (easier to understand)
2. No APK decompilation needed
3. Doesn't require Android knowledge
4. Works on both iPhone and Android
5. Shows you exactly where it is

**Steps:**
```
1. Open Charles
2. Set phone proxy to Charles
3. Open Hinge app
4. Look at requests to prod-api.hingeaws.net
5. Find "AIzaSy..." in headers or JSON
6. Copy it!
```

**Time: 20-30 minutes**

---

## If Charles Proxy Doesn't Show It

Try these alternatives:

**1. mitmproxy** (Similar to Charles, free)
```bash
pip install mitmproxy
mitmweb
# Phone proxy: localhost:8080
```

**2. Burp Suite** (Like Charles but different UI)
https://portswigger.net/burp/communitydownload

**3. Wireshark** (Advanced network sniffer)
https://www.wireshark.org/

**4. APK Decompilation** (Extract from app binary)
```bash
jadx base.apk -d hinge_source
grep -r "AIzaSy" hinge_source/
```

---

## Common Mistakes

### Mistake 1: Looking in Cookies
- Cookies are for browser/web
- Hinge app doesn't use cookies
- Firebase key is NOT in cookies

### Mistake 2: Looking in Response Headers
- Request headers have the key
- Response headers might not
- Always check Request, not Response

### Mistake 3: Wrong Endpoint
- Must be requests to `hingeaws.net`
- Other requests won't have Firebase key
- Filter for "hingeaws" in Charles

### Mistake 4: Not Installing Certificate
- Charles/mitmproxy HTTPS won't work without cert
- You won't see the request details
- Install certificate on phone!

---

## Firebase Key Security

**Important:** The Firebase key is:
- NOT a secret
- Publicly visible in app
- Designed to be in clients
- Authenticated by user credentials
- Safe to share (we need it to authenticate YOU)

**Google designed it this way:**
- Client (app) has key
- User provides credentials (phone + SMS)
- Firebase validates with your credentials
- Gives you auth token

---

## Once You Have It

Use it for Hinge authentication:

```bash
# Update the code
echo 'FIREBASE_API_KEY = "YOUR_KEY_HERE"' > hinge_firebase_key.txt

# Or edit hinge_auth_real.py line 27:
FIREBASE_API_KEY = "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Then test:
curl -X POST http://localhost:5001/hinge/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1-555-123-4567"}'
```

---

## TL;DR

**Where is Firebase key?**
- Inside Hinge mobile app (embedded in code)

**How to get it?**
- Charles Proxy (intercept network traffic) - 20 min EASIEST
- mitmproxy (free alternative) - 20 min
- APK decompilation (extract from Android) - 45 min

**What it looks like?**
- Starts with `AIzaSy`
- 39 characters total
- Example: `AIzaSyDyZ4g7OnN3RjL4VqKV0mVjLyy-tlqDk20`

**What to do next?**
- Read: `HINGE_QUICK_START.md`
- Download Charles Proxy
- Extract the key (20 minutes)
- Update code
- Done!

---

## Recommended: Start with Charles Proxy

It's the **easiest, fastest, most visual** method.

1. Download: https://www.charlesproxy.com/download/
2. Follow: `HINGE_QUICK_START.md`
3. Takes: ~20 minutes
4. Success rate: Very high

---

**The Firebase key is definitely in the Hinge app. Charles Proxy is the easiest way to find it!**
