#!/usr/bin/env python3
"""
Tinder API Fetcher v2 - With full headers and pagination for likes
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path

# Your auth token from mitmproxy
AUTH_TOKEN = "830486d7-2612-4d69-bb17-bade2e572b7e"

# Tinder API base URL
BASE_URL = "https://api.gotinder.com"

# Full headers to mimic real app
HEADERS = {
    "X-Auth-Token": AUTH_TOKEN,
    "Content-Type": "application/json",
    "User-Agent": "Tinder/17.35.1 (iPhone; iOS 26.6.2; Scale/3.00)",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "platform": "ios",
    "tinder-version": "17.35.1",
    "app-version": "7981",
    "os-version": "260000600002",
    "x-supported-image-formats": "webp, jpeg",
    "persistent-device-id": "d7b8a4415ccc4737afa6c1dd2f8fbf35",
    "x-hubble-entity-id": "4d8cffe8-b0bc-4e19-8bc3-60f2130a5305",
    "x-device-ram": "7",
}


def fetch_endpoint(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Fetch data from a Tinder API endpoint."""
    url = f"{BASE_URL}{endpoint}"
    print(f"  {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=HEADERS, timeout=30)
        else:
            response = requests.post(url, headers=HEADERS, json=data, timeout=30)
        
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            print(f"    Error {response.status_code}: {response.text[:200]}")
            return {"error": response.status_code, "message": response.text}
    except Exception as e:
        print(f"    Exception: {e}")
        return {"error": str(e)}


def fetch_fast_match_teasers():
    """Fetch who liked you (teasers/preview) - requires Gold."""
    return fetch_endpoint("/v2/fast-match/teasers")


def fetch_fast_match_count():
    """Fetch count of likes."""
    return fetch_endpoint("/v2/fast-match/count")


def fetch_fast_match_preview():
    """Fetch preview of likes."""
    return fetch_endpoint("/v2/fast-match/preview")


def fetch_likes_you(page_token: str = None):
    """Fetch who liked you with pagination."""
    endpoint = "/v2/fast-match"
    if page_token:
        # Use next_page_token format
        endpoint += f"?page_token={page_token}"
    return fetch_endpoint(endpoint)


def fetch_recommendations():
    """Fetch recommended profiles (discovery feed)."""
    return fetch_endpoint("/v2/recs/core")


def fetch_user_profile(user_id: str):
    """
    Fetch full profile data for a specific user.
    This gets the complete data including height, job, school, etc.
    """
    return fetch_endpoint(f"/user/{user_id}")


def fetch_matches(page_token: str = None):
    """Fetch your matches with pagination."""
    endpoint = "/v2/matches?count=60"
    if page_token:
        endpoint += f"&page_token={page_token}"
    return fetch_endpoint(endpoint)


def fetch_profile():
    """Fetch your own profile."""
    return fetch_endpoint("/v2/profile?include=likes,super_likes,gold")


def fetch_all_likes(max_pages: int = 100):
    """
    Fetch all likes with pagination.
    Rate limited to avoid detection.
    """
    all_likes = []
    page_token = None
    page = 0
    
    print("\nFetching likes (this may take a while)...")
    
    while page < max_pages:
        page += 1
        print(f"\n  Page {page}:")
        
        result = fetch_likes_you(page_token)
        
        if "error" in result:
            print(f"    Error fetching likes: {result}")
            break
        
        # Extract profiles from result
        data = result.get("data", {})
        results = data.get("results", [])
        
        if not results:
            print("    No more results")
            break
        
        all_likes.extend(results)
        print(f"    Got {len(results)} profiles (total: {len(all_likes)})")
        
        # Check for next page - use next_page_token!
        page_token = data.get("next_page_token")
        if not page_token:
            print("    No more pages")
            break
        
        # Rate limit - wait between requests to avoid detection
        time.sleep(2.0)
    
    return all_likes


def fetch_all_matches(max_pages: int = 20, enrich_profiles: bool = True):
    """
    Fetch all matches with pagination.
    If enrich_profiles is True, also fetch full profile data for each match.
    """
    all_matches = []
    page_token = None
    page = 0
    
    print("\nFetching matches...")
    
    while page < max_pages:
        page += 1
        
        result = fetch_matches(page_token)
        
        if "error" in result:
            break
        
        data = result.get("data", {})
        matches = data.get("matches", [])
        
        if not matches:
            break
        
        all_matches.extend(matches)
        print(f"  Page {page}: got {len(matches)} (total: {len(all_matches)})")
        
        page_token = data.get("next_page_token")
        if not page_token:
            break
        
        time.sleep(1)
    
    # Enrich matches with full profile data
    if enrich_profiles and all_matches:
        print(f"\nEnriching {len(all_matches)} match profiles with full data...")
        for i, match in enumerate(all_matches):
            person = match.get("person", {})
            user_id = person.get("_id")
            
            if user_id:
                print(f"  [{i+1}/{len(all_matches)}] Fetching {person.get('name', 'Unknown')}...")
                full_profile = fetch_user_profile(user_id)
                
                if "error" not in full_profile:
                    # Merge full profile into person data
                    full_results = full_profile.get("results", {})
                    if full_results:
                        # Update person with full data, preserving existing fields
                        match["person"] = {**person, **full_results}
                        match["_enriched"] = True
                
                # Rate limit to avoid detection
                time.sleep(1.5)
    
    return all_matches


def save_data(data: dict, filename: str):
    """Save data to a JSON file."""
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = output_dir / f"{filename}_{timestamp}.json"
    
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"\nSaved to: {filepath}")
    return filepath


def main():
    print("=" * 60)
    print(" Tinder Data Fetcher v2 (with pagination)")
    print("=" * 60)
    
    all_data = {}
    
    # 1. Your profile
    print("\n[1/5] Fetching your profile...")
    profile = fetch_profile()
    all_data["my_profile"] = profile
    
    # Check if we have Gold (needed for likes)
    has_gold = profile.get("data", {}).get("gold", {})
    print(f"  Gold status: {has_gold}")
    
    # 2. Fast match count
    print("\n[2/5] Checking likes count...")
    count = fetch_fast_match_count()
    all_data["likes_count"] = count
    print(f"  Likes count: {count}")
    
    # 3. Try fetching teasers (preview of who liked you)
    print("\n[3/5] Fetching likes teasers...")
    teasers = fetch_fast_match_teasers()
    all_data["teasers"] = teasers
    
    if "error" not in teasers:
        results = teasers.get("data", {}).get("results", [])
        print(f"  Got {len(results)} teaser profiles")
    else:
        print(f"  Teasers error (may need Gold): {teasers.get('error')}")
    
    # 4. Try fetching full likes with pagination
    print("\n[4/5] Fetching all likes (paginated)...")
    likes = fetch_all_likes(max_pages=100)  # Up to 100 pages
    all_data["likes_you"] = likes
    print(f"  Total likes fetched: {len(likes)}")
    
    # 5. Fetch matches
    print("\n[5/5] Fetching all matches...")
    matches = fetch_all_matches()
    all_data["matches"] = matches
    print(f"  Total matches: {len(matches)}")
    
    # 6. Recommendations
    print("\n[Bonus] Fetching recommendations...")
    recs = fetch_recommendations()
    all_data["recommendations"] = recs
    
    # Save everything
    print("\n" + "=" * 60)
    save_data(all_data, "tinder_full_data")
    
    # Summary
    print("\n SUMMARY")
    print("=" * 60)
    print(f"  Likes (who liked you): {len(likes)}")
    print(f"  Matches: {len(matches)}")
    recs_count = len(recs.get("data", {}).get("results", [])) if "data" in recs else 0
    print(f"  Recommendations: {recs_count}")
    print("\nDone!")


if __name__ == "__main__":
    main()
