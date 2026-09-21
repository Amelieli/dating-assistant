# Get the REAL Tinder Token (X-Auth-Token)

## The Problem

The APISID cookie alone doesn't work. Tinder web uses a different token called **X-Auth-Token** in API requests.

## The Solution (2 Minutes)

### Step 1: Open Tinder Web

Go to: https://tinder.com

### Step 2: Open DevTools

- Press **F12** (Windows/Linux)
- Or **Cmd+Option+I** (Mac)

### Step 3: Go to Network Tab

- Click the **Network** tab at the top
- Make sure it's recording (red dot should be on)

### Step 4: Filter Requests

- In the filter box, type: **gotinder**
- This shows only Tinder API requests

### Step 5: Trigger an API Call

Do ONE of these:
- Click on someone's profile
- Swipe left/right
- Open your matches
- Refresh the page

### Step 6: Find the Token

You should see requests to `api.gotinder.com`

Click on ANY of them, then:

1. Click the **Headers** tab
2. Scroll down to **Request Headers**
3. Look for **X-Auth-Token**
4. Copy the entire value (long string)

Example:
```
X-Auth-Token: 12345abc-def6-7890-ghij-klmnopqrstuv
```

Copy everything after `X-Auth-Token: `

### Step 7: Save the Token

```bash
# Replace YOUR_TOKEN with what you copied
echo '{"tinder_token": "YOUR_X_AUTH_TOKEN_HERE"}' > tinder_creds.json
```

### Step 8: Sync Profiles

```bash
python3 sync_tinder_now.py
```

---

## Visual Guide

```
DevTools Network Tab
┌─────────────────────────────────────────────────────┐
│ Filter: gotinder                                    │
├─────────────────────────────────────────────────────┤
│ Name          Method  Status  Type                  │
│  profile     GET     200     xhr                   │  <- Click this
│  recs/core   GET     200     xhr                   │
│  matches     GET     200     xhr                   │
└─────────────────────────────────────────────────────┘

Request Headers (scroll down)
┌─────────────────────────────────────────────────────┐
│ :authority: api.gotinder.com                        │
│ :method: GET                                        │
│ accept: application/json                            │
│ user-agent: Mozilla/5.0...                          │
│ X-Auth-Token: 12345abc-def6-7890-ghij-klmnopqr...  │  <- COPY THIS!
│ referer: https://tinder.com/                        │
└─────────────────────────────────────────────────────┘
```

---

## Alternative: Use charles Proxy or mitmproxy

If you can't find the token:

### Charles Proxy (Easier)

1. Download: https://www.charlesproxy.com/
2. Enable SSL Proxying for `*.gotinder.com`
3. Open Tinder web
4. Watch requests in Charles
5. Find X-Auth-Token in headers

### mitmproxy (Command Line)

```bash
# Install
pip install mitmproxy

# Run
mitmweb

# Set browser proxy to localhost:8080
# Visit mitm.it to install cert
# Open tinder.com
# Watch requests at localhost:8081
```

---

## Why APISID Didn't Work

- **APISID**: Google cookie, not Tinder-specific
- **X-Auth-Token**: Tinder's actual auth token
- **Different**: Web cookies != API tokens

Tinder generates X-Auth-Token when you login, and uses it for all API calls.

---

## Quick Commands

```bash
# After you get the X-Auth-Token:

# Save it
echo '{"tinder_token": "YOUR_X_AUTH_TOKEN"}' > tinder_creds.json

# Test it
python3 test_tinder_token.py

# Sync profiles
python3 sync_tinder_now.py

# View in UI
open http://localhost:5001
```

---

## What You're Looking For

The token looks like:
```
12345abc-def6-7890-ghij-klmnopqrstuv
```

- Usually 36 characters
- Has dashes (hyphens)
- Mix of numbers and letters
- Looks like a UUID

**NOT** the APISID cookie we tried (that was wrong!)

---

## Once You Have It

It will work for:
- Fetching recommendations
- Getting your matches  
- Viewing profiles
- All Tinder API features

And the system will:
- Rate limit automatically (4 req/min)
- Add random delays (5-10 sec)
- Protect your account
- Store profiles in database
- Show in dark-themed UI!

---

## Need Help?

Screenshot the Network tab and I can help you find it!

The X-Auth-Token is definitely there if you're logged into Tinder web.
