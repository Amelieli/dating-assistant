# iOS Certificate Trust Settings - Fix

## Problem

You can't find "Certificate Trust Settings" in Settings > General > About

## Solution (Different iOS versions)

### iOS 17+ (Latest)

Go to:
**Settings > General > About > Certificate Trust Settings**

If you don't see it there, try:

**Settings > General > VPN & Device Management > Certificates**

Or:

**Settings > General > Profiles and Device Management**

### iOS 16 and Earlier

Go to:
**Settings > General > Profiles**

(NOT "About" - just "Profiles")

Look for "Charles Proxy CA" certificate and tap it

---

## Step-by-Step for Latest iOS

### Step 1: Check if Certificate is Installed

1. Go to: **Settings > General > VPN & Device Management**
2. Look for "Charles Proxy CA" or "Charles" certificate
3. If you see it, great! Skip to Step 2
4. If NOT, you need to reinstall it (see below)

### Step 2: Trust the Certificate

If you found it:
1. Tap on it
2. You should see an "Install" button or similar
3. Tap it and confirm
4. You might see a toggle to "Trust" it - toggle ON

OR:

1. Go to: **Settings > General > About**
2. Scroll all the way down
3. Look for "Certificate Trust Settings"
4. Find "Charles Proxy Custom Root Certificate"
5. Toggle the switch ON (it should turn green)

---

## If You Can't Find It Anywhere

### Reinstall the Certificate

**Step 1: Remove Old Certificate**
1. Go to: **Settings > General > VPN & Device Management** (or Profiles)
2. Find "Charles Proxy"
3. Tap it and select "Remove" or "Delete"
4. Confirm

**Step 2: Reinstall Certificate**
1. **Make sure Charles proxy is still set!**
   - Settings > Wi-Fi > (i) icon
   - Verify it still shows your computer IP:8888

2. **Open Safari on iPhone**
3. Go to: **http://chls.pro/ssl**
4. You should see a download prompt
5. Tap "Allow"
6. Go to: **Settings > General > VPN & Device Management** (or Profiles)
7. You should see "Charles Proxy CA"
8. Tap it and select "Install"
9. Enter your passcode
10. Tap "Install" again

**Step 3: Trust the Certificate**
1. Go to: **Settings > General > About**
2. Scroll DOWN to the very bottom
3. Look for "Certificate Trust Settings"
4. Find "Charles Proxy Custom Root Certificate"
5. Toggle it ON (green)

---

## Different iOS Versions Locations

| iOS Version | Path |
|-------------|------|
| iOS 18+ | Settings > General > About > Certificate Trust Settings |
| iOS 17 | Settings > General > About > Certificate Trust Settings |
| iOS 16 | Settings > General > Profiles |
| iOS 15 | Settings > General > Profiles |
| iOS 14 | Settings > General > Profiles |

---

## Visual Guide

### Finding it in iOS 17+:

```
Settings
├─ General
│  ├─ About
│  │  └─ [Scroll to bottom]
│  │     └─ Certificate Trust Settings
│  │        └─ Charles Proxy Custom Root Certificate [TOGGLE ON]
│  └─ VPN & Device Management
│     └─ Charles Proxy CA [Tap to trust]
```

### Finding it in iOS 16 and earlier:

```
Settings
├─ General
│  └─ Profiles
│     └─ Charles Proxy CA [Tap to install]
```

---

## If Still Not Working

Try these:

### Option 1: Different Safari Tab
1. Open new Safari tab
2. Go to: **http://chls.pro/ssl** (NOT https, just http!)
3. Should download certificate

### Option 2: Check Proxy is Set
1. Settings > Wi-Fi > (i) icon
2. Verify you see "HTTP Proxy" section with:
   - Server: Your computer IP
   - Port: 8888
3. If not set, set it again!

### Option 3: Restart iPhone
1. Hold power button
2. Slide to turn off
3. Wait 10 seconds
4. Turn back on
5. Try certificate installation again

### Option 4: Try Different Network
1. Disconnect from Wi-Fi
2. Reconnect to Wi-Fi
3. Try to download certificate again

---

## How to Verify It's Actually Installed

### Test 1: Open Safari on iPhone
1. Go to any website (like google.com)
2. Look at Charles on your computer
3. You should see the request
4. If you do, it's working!

### Test 2: Look for Encrypted Traffic
1. Open Safari > google.com
2. In Charles, you should see encrypted traffic
3. If you see gibberish (not JSON), certificate might not be trusted
4. If you see plain text, it's working!

---

## Common Mistakes

**Mistake 1: Using HTTPS instead of HTTP**
- Wrong: `https://chls.pro/ssl`
- Right: `http://chls.pro/ssl` (no S!)

**Mistake 2: Not Toggling Trust**
- Installing certificate ≠ Trusting it
- Must BOTH install AND toggle trust

**Mistake 3: Wrong proxy set**
- Check Settings > Wi-Fi shows correct IP:8888
- If not set, set it first!

**Mistake 4: Certificate installed but not trusted**
- Go to Settings > General > About
- Scroll to bottom
- Find Certificate Trust Settings
- Toggle Charles ON

---

## Charles Proxy on Computer

Make sure Charles is:
1. **Running** (obviously)
2. **Recording** (look for red dot/indicator)
3. **Proxy tab selected** (to see traffic)

If Charles isn't showing your phone traffic:
1. Computer and phone on same Wi-Fi? YES
2. Proxy set on phone? YES
3. Certificate installed? YES
4. Certificate trusted? YES
5. Then restart Charles!

---

## If You're Still Stuck

Do this:

1. **Remove everything**
   - Remove Charles proxy from phone
   - Remove certificate from phone
   - Restart phone

2. **Start fresh**
   - Set proxy again: IP:8888
   - Visit http://chls.pro/ssl
   - Install certificate
   - Trust certificate in Certificate Trust Settings
   - Test with Safari

3. **Verify Charles**
   - Open Charles on computer
   - Make sure recording is ON
   - Open Safari on phone
   - Go to google.com
   - Should see traffic in Charles

---

## Quick Checklist

- [ ] Charles Proxy installed on computer
- [ ] Charles is running
- [ ] Charles is recording (red dot visible)
- [ ] Phone on same Wi-Fi as computer
- [ ] Phone proxy set to computer IP:8888
- [ ] Certificate downloaded from http://chls.pro/ssl
- [ ] Certificate installed in Settings > General > VPN & Device Management
- [ ] Certificate trusted in Certificate Trust Settings (toggle ON)

If all checked, you're ready!

---

## Next Steps

Once certificate is properly trusted:

1. Open Charles on computer
2. Open Hinge on phone
3. Wait for requests to appear
4. Look for `prod-api.hingeaws.net`
5. Find Firebase key in Request Headers
6. Copy and use!
