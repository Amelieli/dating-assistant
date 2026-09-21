#!/usr/bin/env python3
"""
Extract Tinder Session Token from Web

Tinder HAS a web app, unlike Hinge!
"""

import webbrowser
import time

print("""
========================================================================
         GET TINDER SESSION TOKEN (REAL WEB APP!)
========================================================================

Good news: Tinder has a real web app at tinder.com!

This will help you extract your Tinder session token.

Steps:
1. Browser will open to Tinder web
2. Login with your phone number (or Facebook)
3. Open DevTools
4. Copy your session token
5. Use it to fetch REAL profiles!

========================================================================
""")

input("Press Enter to open Tinder web app...")

# Open Tinder web
url = "https://tinder.com"
print(f"\nOpening: {url}")
webbrowser.open(url)

print("""
========================================================================
                    NOW DO THIS:
========================================================================

1. LOGIN TO TINDER:
   - Use your phone number or Facebook
   - Complete the login flow
   - You should see your Tinder feed

2. OPEN DEVTOOLS:
   - Press F12 (Windows/Linux) or Cmd+Option+I (Mac)
   - Click "Application" tab (Chrome) or "Storage" tab (Firefox)
   - Click "Cookies" on the left
   - Find "https://tinder.com"

3. FIND YOUR TOKEN:
   Look for these cookies (in order of importance):
   
   MOST IMPORTANT:
   - "APISID" <- This is usually the one!
   
   BACKUP (copy these too if APISID doesn't work):
   - "HSID"
   - "__Secure-1PAPISID"
   - "__Secure-3PAPISID"
   
   Copy the VALUE of APISID (long string)

4. ALTERNATIVELY - From Network Tab:
   - Go to Network tab
   - Filter by "XHR" or "Fetch"
   - Swipe on someone or load matches
   - Look for requests to "api.gotinder.com"
   - Check Headers for "X-Auth-Token" or "Authorization"

========================================================================
""")

token = input("\nPaste your Tinder auth token here: ").strip()

if not token:
    print("\n[ERROR] No token provided!")
    exit(1)

print(f"\n[OK] Got token: {token[:20]}...")

# Save to file
print("\nSaving token...")

try:
    import json
    
    token_data = {
        'tinder_token': token,
        'extracted_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'source': 'tinder_web'
    }
    
    with open('tinder_creds.json', 'w') as f:
        json.dump(token_data, f, indent=2)
    
    print("[OK] Token saved to tinder_creds.json!")
    
    print("""
========================================================================
                        SUCCESS!
========================================================================

Your Tinder token has been saved!

Now you can fetch REAL Tinder profiles:

Option 1: Use the UI
--------------------
1. Open: http://localhost:5001
2. Go to Tinder section
3. Click "Sync Tinder Profiles"

Option 2: Use Python directly
-----------------------------
python3 << 'EOF'
from dating_agent.profile_aggregator import profile_aggregator
import json

# Load token
with open('tinder_creds.json') as f:
    creds = json.load(f)

agg = profile_aggregator()

# Set credentials directly
agg.tinder_auth.credentials = {
    'auth_token': creds['tinder_token'],
    'user_id': 'from_token',
    'device_id': 'web_browser'
}

# Sync profiles (with rate limiting!)
sync = agg.run_full_sync(
    tinder_user_id='from_token',
    limit=50
)

print(f"Fetched {sync['platforms']['tinder']['profiles_fetched']} profiles!")
EOF

========================================================================
""")

except Exception as e:
    print(f"\n[ERROR] Failed to save: {e}")
    print(f"\nManually create tinder_creds.json with:")
    print(f'{{"tinder_token": "{token}"}}')
