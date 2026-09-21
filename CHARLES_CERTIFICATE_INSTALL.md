# Charles Certificate Installation - Fix

## Problem

`http://chls.pro/ssl` doesn't work or shows "Website is invalid"

## Solution

The URL might be blocked or not working. Here are alternatives:

---

## Method 1: Charles Desktop App (Easier)

**Do this on your COMPUTER, not phone:**

### Step 1: Open Charles on Computer
- Charles should be running

### Step 2: Generate Certificate
- Menu: **Proxy > SSL Proxying Settings**
- Click **"Install Charles Root Certificate"**
- Choose your operating system (Mac/Windows/Linux)

### Step 3: Certificate File
- Charles will open Finder/File Explorer
- A certificate file will be downloaded: `charles-ssl-proxying-certificate.pem`

### Step 4: Transfer to Phone

**Option A: Email to yourself**
1. Email the `.pem` file to yourself
2. Open email on iPhone
3. Tap the attachment
4. Tap "Open in..."
5. Select "Settings"
6. It should install

**Option B: Use AirDrop (Mac)**
1. Drag certificate to AirDrop
2. Select iPhone
3. Accept on iPhone
4. Go to Settings and install

**Option C: USB Transfer**
1. Connect iPhone to computer
2. Use iTunes/Finder to transfer file
3. Open on iPhone
4. Install

---

## Method 2: Direct Download from Charles

### Step 1: Phone Proxy NOT Set Yet

**IMPORTANT:** Temporarily turn OFF your phone proxy first!
- Settings > Wi-Fi > (i) icon
- Set HTTP Proxy to "Off"

### Step 2: Try Download

On iPhone Safari:
- Type: `http://charlesproxy.com/download/` 
- Or: `http://127.0.0.1:8888/` (your computer's IP:8888)

Wait - first disable proxy, then try!

---

## Method 3: Manual Certificate Installation

If automatic download doesn't work, do this manually:

### Step 1: On Computer - Find Charles Config

**Mac:**
```bash
cat ~/.charles/ca.pem
```

Copy the entire certificate text.

**Windows:**
```
C:\Users\[YourUsername]\AppData\Roaming\Charles\ca.pem
```

Right-click > Open with Notepad > Copy all text

### Step 2: Create File on Phone

1. On iPhone, open **Notes** app
2. Create new note
3. Paste the certificate text
4. Title it "Charles CA"
5. Share it: **Share > More > Copy**

Actually, this is complicated. Let's use Method 1 instead.

---

## Method 4: Use iPhone Mail

### Step 1: On Computer
- Open Charles
- **Proxy > SSL Proxying Settings > Install Certificate**
- Choose your OS
- Certificate will download: `charles-ssl-proxying-certificate.pem`

### Step 2: Email Certificate

1. Attach the `.pem` file to an email
2. Send to your iPhone email address
3. On iPhone, open email
4. Tap the attachment
5. Choose "Open in Settings"
6. Install

---

## EASIEST FIX - Just Use the IP Address

Instead of chls.pro/ssl, try:

**On iPhone Safari, type:**
```
http://192.168.1.100:8888
```

(Replace `192.168.1.100` with YOUR computer's actual IP)

This should show Charles' certificate installation page!

---

## Step by Step - The IP Address Method

### Step 1: Get Your Computer IP

**Mac:**
```bash
ipconfig getifaddr en0
```

Example output: `192.168.1.100`

**Windows:**
```cmd
ipconfig
```
Look for "IPv4 Address"

### Step 2: Set Phone Proxy (if not already done)

- Settings > Wi-Fi > (i) icon
- HTTP Proxy > Manual
- Server: `192.168.1.100` (your IP)
- Port: `8888`

### Step 3: Open Safari on iPhone

Type in address bar:
```
http://192.168.1.100:8888
```

Press Enter

### Step 4: You Should See Charles Interface

You'll see Charles' web interface with options to:
- Install certificate
- View traffic
- Configure settings

### Step 5: Install Certificate

Look for a button or link that says:
- "Install Charles Root Certificate"
- "Download Certificate"
- Or similar

Tap it and follow prompts

---

## If Still Not Working

Try this order:

1. **Verify computer IP**
   ```bash
   ipconfig getifaddr en0  # Mac
   ```

2. **Verify phone proxy is set**
   - Settings > Wi-Fi > (i) > HTTP Proxy
   - Should show your IP:8888

3. **Make sure Charles is running**
   - Open Charles app on computer
   - Should be recording (look for indicator)

4. **Try different URL on phone**
   - http://192.168.1.100:8888
   - Or just http://192.168.1.100:8888/
   - Or http://charlesproxy.com

5. **Restart Charles**
   - Quit Charles completely
   - Reopen it
   - Try again

---

## Alternative: Don't Need Certificate?

Actually, wait - do you NEED the certificate?

**You need it IF:**
- You want to see HTTPS traffic (encrypted requests)
- You want to see the content of HTTPS requests

**You DON'T need it IF:**
- You only care about HTTP traffic
- Or you're okay seeing encrypted gibberish

For Hinge, the Firebase key might be sent as HTTP (unencrypted), so you might see it even without the certificate!

Try opening Hinge without installing certificate first:
1. Set proxy to Charles
2. Open Hinge on phone
3. Look at Charles traffic
4. Do you see Firebase key? 
   - YES: You don't need certificate!
   - NO: Install certificate then try again

---

## Quick Checklist

- [ ] Computer IP address correct?
- [ ] Phone proxy set to computer IP:8888?
- [ ] Charles running on computer?
- [ ] Charles is recording?
- [ ] Tried http://192.168.1.100:8888 in Safari?
- [ ] Downloaded certificate?
- [ ] Installed certificate in Settings?

---

## Most Reliable Method

1. **On your computer:**
   - Open Charles
   - Proxy > SSL Proxying Settings
   - Click "Install Charles Root Certificate"
   - Save the .pem file

2. **Email yourself the file**
   - Attach the .pem to an email
   - Send to your iPhone email

3. **On iPhone:**
   - Open email app
   - Download the attachment
   - Tap it
   - Choose "Open in Settings"
   - Install

This method works 100% because you're not relying on network connectivity!

---

## Need Help?

Tell me:
1. What's your computer's IP? (run: ipconfig getifaddr en0)
2. What happens when you try http://192.168.1.100:8888 in Safari?
3. Does Charles show any traffic from your phone?

Then I can help debug!
