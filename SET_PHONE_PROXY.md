# How to Set Phone Proxy to Charles

## Step 1: Find Your Computer's IP Address

**On Mac:**
```bash
ipconfig getifaddr en0
```
You'll get something like: `192.168.1.100`

**On Windows (Command Prompt):**
```cmd
ipconfig
```
Look for "IPv4 Address" (something like 192.168.x.x)

**On Linux:**
```bash
hostname -I
```

**Write down this IP!** You'll need it in a moment.

---

## Step 2: For iPhone

### Prerequisites:
- iPhone and computer on SAME Wi-Fi network
- Charles Proxy running on computer

### Steps:

1. **Open Settings on iPhone**
   - Tap Settings

2. **Go to Wi-Fi**
   - Tap Wi-Fi
   - You should see your Wi-Fi network name

3. **Tap the Information Icon**
   - Find your Wi-Fi network in the list
   - Tap the small info icon (i) on the right

4. **Configure Proxy**
   - Scroll down to "HTTP PROXY"
   - Tap "Configure Proxy"
   - Select "Manual"

5. **Enter Proxy Settings**
   - Server: **[Your computer IP]** (e.g., 192.168.1.100)
   - Port: **8888**
   - Leave Authentication OFF (unless you set one in Charles)

6. **Tap "Save"**

7. **You should see "Connected with HTTP Proxy"** under your Wi-Fi name

### Visual Example:
```
Settings > Wi-Fi > (i) next to network > HTTP Proxy > Manual
├─ Server: 192.168.1.100
└─ Port: 8888
```

---

## Step 3: For Android

### Prerequisites:
- Android phone and computer on SAME Wi-Fi network
- Charles Proxy running on computer

### Steps:

1. **Open Settings on Android**
   - Tap Settings (gear icon)

2. **Go to Wi-Fi**
   - Tap "Network & Internet" or "Connections"
   - Tap "Wi-Fi"

3. **Select Your Wi-Fi Network**
   - Long-press (hold) on your Wi-Fi network name
   - OR tap the network name then tap "Modify"

4. **Configure Proxy**
   - Find "Advanced options" or similar
   - Tap "Proxy"
   - Select "Manual"

5. **Enter Proxy Settings**
   - Proxy hostname: **[Your computer IP]** (e.g., 192.168.1.100)
   - Proxy port: **8888**
   - Leave other fields blank

6. **Tap "Save"**

### Visual Example:
```
Settings > Network & Internet > Wi-Fi > Long-press network > Modify
├─ Advanced options
├─ Proxy: Manual
├─ Proxy hostname: 192.168.1.100
└─ Proxy port: 8888
```

---

## Step 4: Install Charles Certificate on Phone

**This is CRITICAL!** Without this, you won't see HTTPS traffic.

### For iPhone:

1. **Open Safari on iPhone**
   - Go to: **http://chls.pro/ssl**
   - (Or in Charles: Proxy > SSL Proxying Settings > Install Certificate on iPhone)

2. **Tap "Allow"** when prompted

3. **Go to Settings > General > Profiles**
   - Find "Charles Proxy CA"
   - Tap "Install"
   - Enter your iPhone passcode
   - Tap "Install" again

4. **Go to Settings > General > About > Certificate Trust Settings**
   - Find "Charles Proxy Custom Root Certificate"
   - Toggle it ON (green)

5. **Done!** Certificate is installed

### For Android:

1. **On your computer, open Charles**
   - Help > Install Charles Root Certificate > Android

2. **On Android phone, open browser**
   - Go to: **http://chls.pro/ssl**
   - It will download a .pem file

3. **Go to Settings > Security**
   - Tap "Install certificates from storage"
   - Select the downloaded certificate
   - Name it "Charles Proxy"
   - Tap OK

4. **Done!** Certificate is installed

---

## Step 5: Verify It's Working

### On Your Phone:

1. **Open any app** (like Safari, Chrome, or Hinge)
2. **Load a website**
3. **Look at Charles on your computer**
4. You should see requests appearing!

### What You Should See:

In Charles:
```
Structure tab shows:
├─ domains.com
│  ├─ /path1
│  └─ /path2
├─ api.example.com
│  ├─ /api/endpoint
│  └─ /api/other
```

If you see this, **IT'S WORKING!**

---

## Troubleshooting

### Problem 1: No Requests Showing in Charles

**Cause:** Phone not using proxy

**Fix:**
1. Verify IP address is correct
   - On Mac: `ipconfig getifaddr en0`
   - Double-check it matches what you entered on phone

2. Verify port is 8888 on phone

3. Restart Charles

4. Restart phone's Wi-Fi
   - Settings > Wi-Fi > Turn off
   - Wait 10 seconds
   - Turn back on

5. Reboot phone

### Problem 2: "Cannot Connect to Proxy"

**Cause:** Computer IP is wrong OR computer is not on same Wi-Fi

**Fix:**
1. Verify computer IP:
   ```bash
   ipconfig getifaddr en0  # Mac
   ```

2. Verify phone is on SAME Wi-Fi as computer
   - Check phone and computer both show same network name

3. Disable firewall temporarily
   - Mac: System Preferences > Security & Privacy > Firewall OFF
   - Windows: Turn off Windows Defender

4. Try different IP address
   - Some routers use different IPs
   - Try pinging your computer from phone

### Problem 3: Certificate Error on Phone

**Cause:** Certificate not installed properly

**Fix:**
1. Uninstall old certificate
   - iPhone: Settings > General > Profiles > Delete
   - Android: Settings > Security > Clear credentials

2. Reinstall certificate
   - iPhone: http://chls.pro/ssl
   - Android: http://chls.pro/ssl

3. For iPhone only:
   - Go to Settings > General > About > Certificate Trust Settings
   - Toggle Charles certificate ON

### Problem 4: Certificate Not Trusted

**Cause:** Didn't enable certificate in iOS

**Fix:**
1. Go to: Settings > General > About > Certificate Trust Settings
2. Find "Charles Proxy Custom Root Certificate"
3. Toggle it **ON** (switch should be green)

### Problem 5: Only Seeing Some Traffic

**Cause:** Charles SSL Proxying not configured

**Fix:**
1. In Charles: **Proxy > SSL Proxying Settings**
2. Click **Add**
3. Host: `*` (wildcard)
4. Port: `443`
5. Click **OK**
6. Restart Charles

---

## Quick Checklist

Before you open Hinge:

- [ ] Computer IP address written down
- [ ] Phone is on SAME Wi-Fi as computer
- [ ] Phone proxy set to computer IP:8888
- [ ] Charles certificate installed on phone
- [ ] Charles certificate TRUSTED on iPhone (Settings > General > About > Certificate Trust Settings)
- [ ] Charles is running on computer
- [ ] Charles is recording (look for red dot/indicator)

---

## When You're Ready for Hinge

1. **Phone proxy is set to Charles** (verified above)
2. **Open Charles on your computer**
3. **Make sure it's recording** (should be default)
4. **Open Hinge app on phone**
5. **Wait for it to load**
6. **Look at Charles**
7. **You should see requests to `prod-api.hingeaws.net`**
8. **Click on them to see Firebase key in headers/JSON**

---

## Charles Key Areas

Once set up, in Charles you'll see:

**Proxy tab:**
- Shows all traffic from your phone
- Filter by "hingeaws" to see Hinge traffic

**Breakdown tab:**
- View by domain
- Easier to find hingeaws requests

**Request tab (when you click a request):**
- See what was sent
- Look for Firebase key here

**Headers tab:**
- Shows all request headers
- This is where X-Goog-API-Key usually appears

---

## Summary

**3 Main Steps:**

1. **Find computer IP** (`ipconfig getifaddr en0` on Mac)

2. **Set phone proxy:**
   - iPhone: Settings > Wi-Fi > (i) > HTTP Proxy > Manual
   - Android: Settings > Wi-Fi > Long-press > Proxy > Manual
   - Server: Your computer IP
   - Port: 8888

3. **Install certificate:**
   - Both: Visit http://chls.pro/ssl on phone
   - iPhone: Also enable in Certificate Trust Settings
   - Android: Install from storage

4. **Verify:** Open an app on phone, see traffic in Charles

**Then open Hinge and look for Firebase key!**

---

## Need Help?

If something isn't working:

1. Check your computer IP is correct
2. Verify phone is on same Wi-Fi
3. Restart Charles
4. Restart phone's Wi-Fi
5. Reinstall certificate on phone

**Most common issue:** Wrong IP address or certificate not installed!
