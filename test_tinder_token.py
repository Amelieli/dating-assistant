#!/usr/bin/env python3
"""
Test Tinder Token - Direct API Call
"""

import requests
import json

print("\n" + "="*70)
print("TESTING TINDER TOKEN")
print("="*70 + "\n")

# Load token
with open('tinder_creds.json') as f:
    creds = json.load(f)

token = creds['tinder_token']
print(f"Testing token: {token[:20]}...\n")

# Tinder API endpoints to try
endpoints = [
    ("GET", "https://api.gotinder.com/v2/profile?include=account", "Profile"),
    ("GET", "https://api.gotinder.com/v2/recs/core", "Recommendations"),
    ("GET", "https://api.gotinder.com/v2/matches", "Matches"),
]

print("Trying different header combinations:\n")

# Method 1: X-Auth-Token header (mobile app)
print("Method 1: X-Auth-Token header")
print("-" * 70)
for method, url, name in endpoints:
    try:
        response = requests.get(
            url,
            headers={
                "X-Auth-Token": token,
                "User-Agent": "Tinder/13.0.0 (iPhone; iOS 15.0; Scale/3.00)",
                "Accept": "application/json"
            },
            timeout=10
        )
        print(f"  {name}: {response.status_code}")
        if response.status_code == 200:
            print(f"    SUCCESS! This works!")
            data = response.json()
            print(f"    Response keys: {list(data.keys())[:5]}")
        elif response.status_code == 401:
            print(f"    Unauthorized - wrong token format")
        elif response.status_code == 403:
            print(f"    Forbidden - might be banned")
    except Exception as e:
        print(f"  {name}: Error - {e}")

print()

# Method 2: Cookie header (web app)
print("Method 2: Cookie header")
print("-" * 70)
for method, url, name in endpoints:
    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "application/json"
            },
            cookies={
                "APISID": token
            },
            timeout=10
        )
        print(f"  {name}: {response.status_code}")
        if response.status_code == 200:
            print(f"    SUCCESS! This works!")
            data = response.json()
            print(f"    Response keys: {list(data.keys())[:5]}")
    except Exception as e:
        print(f"  {name}: Error - {e}")

print()

# Method 3: Try to get token from web session
print("Method 3: Check what Tinder web actually uses")
print("-" * 70)
print("The APISID cookie might need to be combined with other cookies.")
print("Try this:")
print()
print("1. Open tinder.com in DevTools")
print("2. Go to Network tab")
print("3. Click on someone's profile")
print("4. Look at the request headers")
print("5. Find 'X-Auth-Token' or 'Authorization' header")
print("6. That's the real token!")
print()
print("The APISID cookie alone might not be enough.")
print()

print("="*70)
print("If none of these worked, you need the X-Auth-Token from Network tab")
print("="*70)
