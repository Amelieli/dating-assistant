#!/usr/bin/env python3
"""
Analyze and display Tinder profile data in a readable format.
"""

import json
from datetime import datetime
from pathlib import Path


def calculate_age(birth_date_str: str) -> int:
    """Calculate age from birth date string."""
    birth_date = datetime.fromisoformat(birth_date_str.replace("Z", "+00:00"))
    today = datetime.now(birth_date.tzinfo)
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def parse_user(user: dict) -> dict:
    """Extract key info from a user profile."""
    return {
        "id": user.get("_id", "N/A"),
        "name": user.get("name", "N/A"),
        "age": calculate_age(user["birth_date"]) if "birth_date" in user else "N/A",
        "bio": user.get("bio", "")[:200] + "..." if len(user.get("bio", "")) > 200 else user.get("bio", ""),
        "distance_mi": user.get("distance_mi", "N/A"),
        "city": user.get("city", {}).get("name", "N/A") if isinstance(user.get("city"), dict) else "N/A",
        "job_title": user.get("jobs", [{}])[0].get("title", {}).get("name", "N/A") if user.get("jobs") else "N/A",
        "company": user.get("jobs", [{}])[0].get("company", {}).get("name", "N/A") if user.get("jobs") else "N/A",
        "school": user.get("schools", [{}])[0].get("name", "N/A") if user.get("schools") else "N/A",
        "photo_count": len(user.get("photos", [])),
        "first_photo_url": user.get("photos", [{}])[0].get("url", "N/A") if user.get("photos") else "N/A",
    }


def print_profile(profile: dict, index: int):
    """Print a profile in a readable format."""
    print(f"\n{'='*60}")
    print(f" #{index + 1}: {profile['name']}, {profile['age']}")
    print(f"{'='*60}")
    print(f"  Distance: {profile['distance_mi']} miles")
    print(f"  City: {profile['city']}")
    print(f"  Job: {profile['job_title']} @ {profile['company']}")
    print(f"  School: {profile['school']}")
    print(f"  Photos: {profile['photo_count']}")
    print(f"  Bio: {profile['bio']}")


def analyze_data(filepath: str):
    """Load and analyze the Tinder data file."""
    with open(filepath, "r") as f:
        data = json.load(f)
    
    print("\n" + "=" * 60)
    print(" TINDER DATA ANALYSIS")
    print("=" * 60)
    
    # Recommendations (discovery feed)
    recs = data.get("recommendations", {}).get("data", {}).get("results", [])
    print(f"\n>> RECOMMENDATIONS ({len(recs)} profiles)")
    
    for i, rec in enumerate(recs[:10]):  # Show first 10
        if "user" in rec:
            profile = parse_user(rec["user"])
            print_profile(profile, i)
    
    # Matches
    matches = data.get("matches", {}).get("data", {}).get("matches", [])
    print(f"\n\n>> MATCHES ({len(matches)} total)")
    
    for i, match in enumerate(matches[:10]):  # Show first 10
        if "person" in match:
            profile = parse_user(match["person"])
            last_msg = match.get("messages", [{}])[-1].get("message", "No messages") if match.get("messages") else "No messages"
            print_profile(profile, i)
            print(f"  Last message: {last_msg[:100]}...")
    
    # Summary stats
    print("\n\n" + "=" * 60)
    print(" SUMMARY")
    print("=" * 60)
    print(f"  Total recommendations: {len(recs)}")
    print(f"  Total matches: {len(matches)}")
    
    if recs:
        ages = [calculate_age(r["user"]["birth_date"]) for r in recs if "user" in r and "birth_date" in r.get("user", {})]
        if ages:
            print(f"  Recommendation age range: {min(ages)} - {max(ages)}")
            print(f"  Average age: {sum(ages) / len(ages):.1f}")


def main():
    # Find the most recent data file
    data_dir = Path("data")
    files = sorted(data_dir.glob("tinder_data_*.json"), reverse=True)
    
    if not files:
        print("No data files found! Run tinder_fetcher.py first.")
        return
    
    latest_file = files[0]
    print(f"Analyzing: {latest_file}")
    analyze_data(str(latest_file))


if __name__ == "__main__":
    main()
