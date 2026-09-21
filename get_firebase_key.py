#!/usr/bin/env python3
"""
Extract Real Firebase API Key from Hinge Web

This script helps you get the current Firebase key from Hinge's website.
"""

import webbrowser
import time

print("""
========================================================================
         GET REAL FIREBASE KEY FROM HINGE
========================================================================

This will help you extract the REAL Firebase API key from Hinge.

Steps:
1. Browser will open to Hinge login page
2. Open DevTools (F12 or Cmd+Option+I)
3. Go to Network tab
4. Filter by 'googleapis'
5. Enter your phone number in Hinge
6. Look for request to 'identitytoolkit.googleapis.com'
7. Copy the 'key' parameter from the URL

Example URL you're looking for:
https://identitytoolkit.googleapis.com/v1/recaptchaParams?key=AIzaSy...

The key is the part after '?key=' and looks like:
AIzaSyABCDEF1234567890abcdefghijklmnop (39 characters)

========================================================================
""")

input("Press Enter to open Hinge login page...")

# Open Hinge login
url = "https://hinge.co/login"
print(f"\nOpening: {url}")
webbrowser.open(url)

print("""
========================================================================
                    NOW DO THIS:
========================================================================

1. In the browser that just opened:
   - Press F12 (Windows/Linux) or Cmd+Option+I (Mac)
   - Click the "Network" tab
   - Click the filter icon and select "Fetch/XHR"

2. In Hinge:
   - Enter your phone number: +1-785-431-4064
   - Click "Continue" but DON'T close the DevTools!

3. In the Network tab:
   - Look for a request to "identitytoolkit.googleapis.com"
   - Click on it
   - Look at the URL or Headers
   - Find "?key=AIzaSy..." part
   - Copy JUST the key (starts with AIzaSy, 39 characters)

4. Paste it below!

========================================================================
""")

firebase_key = input("\nPaste the Firebase API key here: ").strip()

if not firebase_key:
    print("\n[ERROR] No key provided!")
    exit(1)

if not firebase_key.startswith("AIzaSy"):
    print(f"\n[WARNING] Key should start with 'AIzaSy', got: {firebase_key[:10]}...")
    confirm = input("Continue anyway? (yes/no): ")
    if confirm.lower() != 'yes':
        exit(1)

if len(firebase_key) != 39:
    print(f"\n[WARNING] Key should be 39 characters, got {len(firebase_key)}")
    confirm = input("Continue anyway? (yes/no): ")
    if confirm.lower() != 'yes':
        exit(1)

print(f"\n[OK] Got key: {firebase_key[:20]}...")

# Update the file
print("\nUpdating hinge_auth_real.py...")

try:
    with open('hinge_auth_real.py', 'r') as f:
        content = f.read()
    
    # Replace the old key
    old_key = 'AIzaSyDyZ4g7OnN3RjL4VqKV0mVjLyy-tlqDk20'
    if old_key in content:
        content = content.replace(old_key, firebase_key)
        
        with open('hinge_auth_real.py', 'w') as f:
            f.write(content)
        
        print("[OK] Updated hinge_auth_real.py!")
    else:
        print("[WARNING] Old key not found, updating manually...")
        print(f"\nUpdate line 27 in hinge_auth_real.py to:")
        print(f'FIREBASE_API_KEY = "{firebase_key}"')
    
    print("""
========================================================================
                        SUCCESS!
========================================================================

The Firebase key has been updated!

Now run:
    python3 quick_start_hinge.py

Or start the UI:
    cd backend && python3 api.py
    # Then open: http://localhost:5001

The authentication should now work with REAL SMS!

========================================================================
""")

except Exception as e:
    print(f"\n[ERROR] Failed to update file: {e}")
    print(f"\nManually update line 27 in hinge_auth_real.py to:")
    print(f'FIREBASE_API_KEY = "{firebase_key}"')
