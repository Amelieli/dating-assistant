# mitmproxy - Complete Setup Guide

mitmproxy is simpler than Charles and works great for this!

---

## Step 1: Install mitmproxy

**On your Mac, open Terminal and run:**

```bash
pip install mitmproxy
```

Wait for it to finish installing.

---

## Step 2: Start mitmproxy

**In Terminal, run:**

```bash
mitmweb
```

This starts:
- mitmproxy service on port 8080
- Web interface on http://localhost:8081

Keep this terminal window open!

---

## Step 3: Configure Phone Proxy

**On iPhone:**

1. Settings > Wi-Fi > (i) icon next to your network
2. HTTP Proxy > Configure Proxy > Manual
3. Server: `192.168.0.175` (your computer IP)
4. Port: `8080` (different from Charles!)
5. Tap Save

---

## Step 4: Install Certificate on Phone

**On iPhone, open Safari and go to:**

```
http://mitm.it
```

You should see a page with platform options.

**Tap: iOS**

This downloads the mitmproxy certificate.

---

## Step 5: Install the Certificate

**On iPhone:**

1. The certificate download should trigger Settings
2. Tap "Install"
3. Enter your passcode
4. Tap "Install" again

---

## Step 6: Trust the Certificate

**On iPhone:**

1. Settings > General > About > [scroll to bottom]
2. Certificate Trust Settings
3. Find "mitmproxy" certificate
4. Toggle it ON (green)

---

## Step 7: Open mitmweb Interface

**On your computer:**

Open browser: `http://localhost:8081`

You should see mitmproxy web dashboard.

---

## Step 8: Open Hinge and Capture Traffic

1. Make sure mitmweb is showing in your browser
2. **Open Hinge app on iPhone**
3. Let it load
4. **Watch mitmweb dashboard - you should see requests appear!**

---

## Step 9: Find the Firebase Key

**In mitmweb, look for:**

- Requests to `prod-api.hingeaws.net`
- Click on one
- Look at the request details

**Find the Firebase key:**
- Look for `AIzaSy...` in the request
- Or search for `firebase` or `apiKey`
- Copy the value!

---

## Complete Flow

```
Terminal:
  mitmweb (running)
        ↓
Browser:
  http://localhost:8081 (watching requests)
        ↓
iPhone:
  Proxy set to: 192.168.0.175:8080
  Certificate installed & trusted
  Hinge app open
        ↓
mitmweb shows:
  prod-api.hingeaws.net requests
        ↓
Find:
  Firebase key (AIzaSy...)
        ↓
Copy & Use!
```

---

## Troubleshooting

### "mitmweb not found"
```bash
pip install mitmproxy
```

### Phone not showing requests in mitmweb
1. Verify proxy is set: 192.168.0.175:8080
2. Restart phone Wi-Fi
3. Refresh mitmweb browser tab

### Certificate error on phone
1. Go to http://mitm.it on phone
2. Download certificate again
3. Install and trust in Settings

### Can't access mitmweb dashboard
```bash
# mitmweb might already be running, kill it:
pkill -f mitmweb

# Start again:
mitmweb
```

---

## Searching for Firebase Key

In mitmweb, once you see hingeaws requests:

1. Click on a request (like `/profile` or `/matches`)
2. Look for tabs: Request, Response, etc.
3. Search in the Request for:
   - `AIzaSy` (Firebase key start)
   - `firebaseKey`
   - `X-Goog-API-Key`
   - `api_key`

The value will look like:
```
AIzaSyDyZ4g7OnN3RjL4VqKV0mVjLyy-tlqDk20
```

Copy that! That's your Firebase key!

---

## Quick Reference

| Step | What | Where |
|------|------|-------|
| Install | `pip install mitmproxy` | Terminal |
| Start | `mitmweb` | Terminal |
| Dashboard | http://localhost:8081 | Browser |
| Phone Proxy | 192.168.0.175:8080 | iPhone Settings |
| Certificate | http://mitm.it | iPhone Safari |
| Get Key | Find `AIzaSy...` | mitmweb Request tab |

---

## Once You Have Firebase Key

1. Update `hinge_auth_real.py` line 27:
   ```python
   FIREBASE_API_KEY = "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
   ```

2. Restart backend:
   ```bash
   ./start_system.sh
   ```

3. Open http://localhost:5001

4. Authenticate with Hinge!

---

## Done!

Once you have the Firebase key, you can get real Hinge profiles!
