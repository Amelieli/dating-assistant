#!/usr/bin/env python3
"""
Tinder API Fetcher - Extract profile data from Tinder API
"""

import json
import requests
from datetime import datetime
from pathlib import Path

# Your auth token from mitmproxy
AUTH_TOKEN = "07d897f3-4e66-4aac-9510-aa0c740504d9"

# Tinder API base URL
BASE_URL = "https://api.gotinder.com"

# Common headers that Tinder expects
HEADERS = {
    "X-Auth-Token": AUTH_TOKEN,
    "Content-Type": "application/json",
    "User-Agent": "Tinder/14.21.0 (iPhone; iOS 18_0; Scale/3.00)",
    "Accept": "application/json",
    "Accept-Language": "en-US",
    "platform": "ios",
    "app-version": "5594",
}


def fetch_endpoint(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Fetch data from a Tinder API endpoint."""
    url = f"{BASE_URL}{endpoint}"
    print(f"Fetching: {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=HEADERS, timeout=30)
        else:
            response = requests.post(url, headers=HEADERS, json=data, timeout=30)
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            print(f"  Error: {response.text[:200]}")
            return {"error": response.status_code, "message": response.text}
    except Exception as e:
        print(f"  Exception: {e}")
        return {"error": str(e)}


def fetch_recommendations():
    """Fetch recommended profiles (discovery feed)."""
    return fetch_endpoint("/v2/recs/core")


def fetch_fast_match_teasers():
    """Fetch who liked you (teasers/preview)."""
    return fetch_endpoint("/v2/fast-match/teasers")


def fetch_fast_match_teaser():
    """Fetch single teaser."""
    return fetch_endpoint("/v2/fast-match/teaser")


def fetch_matches():
    """Fetch your matches."""
    return fetch_endpoint("/v2/matches?count=60")


def fetch_profile():
    """Fetch your own profile."""
    return fetch_endpoint("/v2/profile?include=likes,super_likes,gold")


def fetch_updates():
    """Fetch updates (matches, messages, etc.)."""
    return fetch_endpoint("/updates", method="POST", data={"last_activity_date": ""})


def save_data(data: dict, filename: str):
    """Save data to a JSON file."""
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = output_dir / f"{filename}_{timestamp}.json"
    
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Saved to: {filepath}")
    return filepath


def main():
    """Main function to fetch all data."""
    print("=" * 50)
    print("Tinder Data Fetcher")
    print("=" * 50)
    
    all_data = {}
    
    # Fetch your own profile first
    print("\n1. Fetching your profile...")
    profile = fetch_profile()
    all_data["my_profile"] = profile
    
    # Fetch recommendations (discovery feed)
    print("\n2. Fetching recommendations...")
    recs = fetch_recommendations()
    all_data["recommendations"] = recs
    
    # Fetch who liked you
    print("\n3. Fetching who liked you (teasers)...")
    teasers = fetch_fast_match_teasers()
    all_data["likes_you"] = teasers
    
    # Fetch matches
    print("\n4. Fetching your matches...")
    matches = fetch_matches()
    all_data["matches"] = matches
    
    # Fetch updates
    print("\n5. Fetching updates...")
    updates = fetch_updates()
    all_data["updates"] = updates
    
    # Save all data
    print("\n" + "=" * 50)
    save_data(all_data, "tinder_data")
    
    # Print summary
    print("\n Summary:")
    if "results" in recs:
        print(f"  - Recommendations: {len(recs.get('results', []))} profiles")
    if "results" in teasers:
        print(f"  - Likes You: {len(teasers.get('results', []))} profiles")
    if "data" in matches and "matches" in matches.get("data", {}):
        print(f"  - Matches: {len(matches.get('data', {}).get('matches', []))} matches")
    
    print("\n Done! Check the 'data' folder for your JSON files.")


if __name__ == "__main__":
    main()
