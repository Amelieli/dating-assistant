#!/usr/bin/env python3
"""
Hinge API Fetcher - Extract profile data from Hinge API
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path

# Your auth token from mitmproxy
AUTH_TOKEN = "GQPp-NjkvOlykAQAofzwsQQjNJTy3dz8FoVABNbm_4A="

# Hinge API base URL
BASE_URL = "https://prod-api.hingeaws.net"

# Headers from mitmproxy
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "*/*",
    "Accept-Language": "en",
    "Accept-Encoding": "gzip, deflate, br",
    "User-Agent": "Hinge/11695 CFNetwork/3860.700.2 Darwin/25.6.0",
    "x-app-version": "10.4.0",
    "x-build-number": "11695",
    "x-device-platform": "iOS",
    "x-os-version": "26.6.2",
    "x-device-id": "CDF2501C-E362-46EA-98A3-127AC2F3942C",
    "x-session-id": "12D39FE1-BA19-4EDA-9B68-E5B0874890A6",
    "x-app-identifier": "co.hinge.mobile.ios",
    "x-device-model": "unknown",
    "x-device-model-code": "iPhone17,4",
    "x-install-id": "6000A826-986A-4729-9309-AFA6DEF7CB9F",
    "x-device-region": "CN",
}


def fetch_endpoint(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Fetch data from a Hinge API endpoint."""
    url = f"{BASE_URL}{endpoint}"
    print(f"  {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=HEADERS, timeout=30)
        else:
            response = requests.post(url, headers=HEADERS, json=data, timeout=30)
        
        print(f"    Status: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            try:
                return response.json()
            except:
                return {"raw": response.text[:500]}
        else:
            print(f"    Error: {response.text[:300]}")
            return {"error": response.status_code, "message": response.text[:500]}
    except Exception as e:
        print(f"    Exception: {e}")
        return {"error": str(e)}


def discover_endpoints():
    """Try various endpoints to find profile data."""
    print("\n" + "=" * 60)
    print(" Discovering Hinge API Endpoints")
    print("=" * 60)
    
    # Common endpoints to try
    endpoints = [
        # User/Profile
        "/user/v3",
        "/user/v2",
        "/user",
        "/profile/v1",
        "/profile",
        "/me",
        
        # Discovery/Feed
        "/discover/v1",
        "/discover",
        "/feed/v1",
        "/feed",
        "/recommendations/v1",
        "/recommendations",
        
        # Likes
        "/likes/v1",
        "/likes",
        "/likes-you/v1",
        "/likes-you",
        "/incoming/v1",
        "/incoming",
        
        # Matches
        "/matches/v1",
        "/matches",
        "/conversations/v1",
        "/conversations",
        
        # Content
        "/content/v2",
        "/content/v1",
        "/content",
    ]
    
    results = {}
    
    for ep in endpoints:
        result = fetch_endpoint(ep)
        if "error" not in result or result.get("error") != 404:
            results[ep] = result
            # If we got data, print a summary
            if "error" not in result:
                print(f"    SUCCESS! Keys: {list(result.keys())[:5]}")
        time.sleep(0.5)  # Rate limit
    
    return results


def fetch_likes_you(page: int = 0, limit: int = 20):
    """Try to fetch who liked you."""
    # Try different endpoint patterns
    endpoints_to_try = [
        f"/likes-you?page={page}&limit={limit}",
        f"/likes/received?page={page}&limit={limit}",
        f"/incoming-likes?page={page}&limit={limit}",
        f"/feed/likes-you?page={page}&limit={limit}",
    ]
    
    for ep in endpoints_to_try:
        result = fetch_endpoint(ep)
        if "error" not in result:
            return result
    
    return {"error": "No working endpoint found"}


def fetch_discover(page: int = 0, limit: int = 20):
    """Fetch discovery feed."""
    endpoints_to_try = [
        f"/discover?page={page}&limit={limit}",
        f"/feed/discover?page={page}&limit={limit}",
        f"/recommendations?page={page}&limit={limit}",
    ]
    
    for ep in endpoints_to_try:
        result = fetch_endpoint(ep)
        if "error" not in result:
            return result
    
    return {"error": "No working endpoint found"}


def fetch_matches():
    """Fetch your matches."""
    return fetch_endpoint("/matches/v1") or fetch_endpoint("/matches") or fetch_endpoint("/conversations")


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
    print(" Hinge Data Fetcher")
    print("=" * 60)
    
    all_data = {}
    
    # First, discover what endpoints work
    print("\n[1/4] Discovering working endpoints...")
    discovered = discover_endpoints()
    all_data["discovered_endpoints"] = discovered
    
    # Try to get user profile
    print("\n[2/4] Fetching user profile...")
    user = fetch_endpoint("/user/v3")
    all_data["user"] = user
    
    # Try to get content
    print("\n[3/4] Fetching content...")
    content = fetch_endpoint("/content/v2")
    all_data["content"] = content
    
    # Try notifications/inbox
    print("\n[4/4] Fetching notifications...")
    notifications = fetch_endpoint("/notification/v1/inbox")
    all_data["notifications"] = notifications
    
    # Save everything
    print("\n" + "=" * 60)
    save_data(all_data, "hinge_data")
    
    # Summary
    print("\n SUMMARY")
    print("=" * 60)
    working = [k for k, v in discovered.items() if "error" not in v]
    print(f"  Working endpoints: {len(working)}")
    for ep in working:
        print(f"    - {ep}")
    
    print("\nDone!")


if __name__ == "__main__":
    main()
