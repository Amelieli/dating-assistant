#!/usr/bin/env python3
"""
Sync Tinder with ALL headers from the browser
"""

import requests
import json

print("\n" + "="*70)
print("SYNCING TINDER WITH COMPLETE HEADERS")
print("="*70 + "\n")

# Load credentials
with open('tinder_creds.json') as f:
    creds = json.load(f)

token = creds['tinder_token']
print(f"Using token: {token[:20]}...\n")

# Complete headers from your Network tab
headers = {
    'X-Auth-Token': token,
    'User-Session-Id': '0efd1047-1244-45b3-8ffb-d2657758ae36',
    'App-Session-Id': '2ac47386-5737-41ab-b53a-4a2e4ec3bc62',
    'Persistent-Device-Id': '40964802-775d-43b4-a353-275ccf2d0420',
    'Platform': 'web',
    'App-Version': '1073301',
    'Tinder-Version': '7.33.1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en,en-US,zh-CN',
    'Origin': 'https://tinder.com',
    'Referer': 'https://tinder.com/'
}

# Test different endpoints
print("Testing endpoints with complete headers:\n")

endpoints = [
    ("GET", "https://api.gotinder.com/v2/profile?locale=en&include=account", "Your Profile"),
    ("GET", "https://api.gotinder.com/v2/matches?count=60", "Matches"),
    ("GET", "https://api.gotinder.com/v2/recs/core?locale=en", "Recommendations"),
]

working_endpoints = []

for method, url, name in endpoints:
    try:
        print(f"{name}:")
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"  Status: {resp.status_code}")
        
        if resp.status_code == 200:
            print(f"  SUCCESS!")
            data = resp.json()
            
            # Show what we got
            if 'data' in data:
                if isinstance(data['data'], dict):
                    print(f"  Keys: {list(data['data'].keys())[:5]}")
                elif isinstance(data['data'], list):
                    print(f"  Got {len(data['data'])} items")
                    if len(data['data']) > 0:
                        print(f"  First item keys: {list(data['data'][0].keys())[:5]}")
            elif 'results' in data:
                print(f"  Got {len(data['results'])} results")
            
            working_endpoints.append((name, url, data))
        else:
            print(f"  Failed: {resp.status_code}")
            if resp.status_code == 401:
                print(f"  Unauthorized - might need different headers")
    
    except Exception as e:
        print(f"  Error: {e}")
    
    print()

# If we got matches, parse and save them
print("="*70)
if working_endpoints:
    print(f"SUCCESS! {len(working_endpoints)} endpoint(s) working!")
    print()
    
    # Look for matches or profile data
    for name, url, data in working_endpoints:
        print(f"{name}:")
        
        if name == "Matches" and 'data' in data:
            matches = data['data'].get('matches', [])
            print(f"  Found {len(matches)} matches!")
            
            if matches:
                print(f"\n  Sample match:")
                match = matches[0]
                person = match.get('person', {})
                print(f"    Name: {person.get('name', 'Unknown')}")
                print(f"    Age: {person.get('birth_date', 'Unknown')}")
                print(f"    Bio: {person.get('bio', 'No bio')[:50]}...")
        
        elif name == "Recommendations" and 'results' in data:
            recs = data['results']
            print(f"  Found {len(recs)} recommendations!")
            
            if recs:
                print(f"\n  Sample rec:")
                rec = recs[0]
                user = rec.get('user', {})
                print(f"    Name: {user.get('name', 'Unknown')}")
                print(f"    Age: {user.get('age', 'Unknown')}")
                print(f"    Distance: {user.get('distance_mi', 'Unknown')} mi")
        
        print()
    
    # Save raw data
    with open('tinder_raw_data.json', 'w') as f:
        json.dump({
            'endpoints': [
                {'name': name, 'url': url, 'data': data}
                for name, url, data in working_endpoints
            ]
        }, f, indent=2)
    
    print(f"Saved raw data to: tinder_raw_data.json")
    print()

else:
    print("No endpoints worked. The token might be expired.")
    print("Try refreshing tinder.com and getting a new token.")

print("="*70)
