#!/usr/bin/env python3
"""
Hydrate the Dating Agent Orchestrator with Tinder data.
Loads JSON data and posts it to the backend API.
"""

import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional


API_BASE = "http://localhost:5001"


def calculate_age(birth_date_str: str) -> int:
    """Calculate age from birth date string."""
    try:
        birth_date = datetime.fromisoformat(birth_date_str.replace("Z", "+00:00"))
        today = datetime.now(birth_date.tzinfo)
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    except:
        return 30  # Default


def convert_tinder_user_to_profile(user: dict, match_status: str = "incoming") -> dict:
    """Convert a Tinder user object to our Profile format."""
    
    # Extract photos
    photos = []
    for photo in user.get("photos", []):
        if "url" in photo:
            photos.append(photo["url"])
        elif "processedFiles" in photo and photo["processedFiles"]:
            photos.append(photo["processedFiles"][0].get("url", ""))
    
    # Extract job info
    jobs = user.get("jobs", [])
    occupation = ""
    if jobs:
        job = jobs[0]
        title = job.get("title", {}).get("name", "") if isinstance(job.get("title"), dict) else ""
        company = job.get("company", {}).get("name", "") if isinstance(job.get("company"), dict) else ""
        occupation = f"{title} @ {company}".strip(" @")
    
    # Extract school
    schools = user.get("schools", [])
    education = schools[0].get("name", "") if schools else ""
    
    # Extract city
    city_data = user.get("city", {})
    city = city_data.get("name", "") if isinstance(city_data, dict) else ""
    
    # Extract lifestyle from selected_descriptors
    height_cm = None
    smokes = None
    drinks = None
    
    for descriptor in user.get("selected_descriptors", []):
        desc_id = descriptor.get("id", "")
        desc_name = descriptor.get("name", "").lower()
        choices = descriptor.get("choice_selections", [])
        choice_names = [c.get("name", "").lower() for c in choices]
        
        # Height (de_30)
        if desc_id == "de_30" or "height" in desc_name:
            # Height is stored in a special format
            measurement = descriptor.get("measurable_selection", {})
            if measurement:
                value = measurement.get("value")
                unit = measurement.get("unit", "cm")
                if value:
                    if unit == "cm":
                        height_cm = int(value)
                    elif unit == "inch":
                        height_cm = int(value * 2.54)
        
        # Smoking
        if "smoking" in desc_name or desc_id == "de_11":
            if any("non" in c or "never" in c for c in choice_names):
                smokes = "no"
            elif any("social" in c or "when drinking" in c for c in choice_names):
                smokes = "socially"
            elif choice_names:
                smokes = "yes"
        
        # Drinking
        if "drinking" in desc_name or "drink" in desc_name or desc_id == "de_22":
            if any("never" in c or "don't" in c or "not" in c for c in choice_names):
                drinks = "no"
            elif any("social" in c for c in choice_names):
                drinks = "socially"
            elif any("frequent" in c or "often" in c for c in choice_names):
                drinks = "often"
            elif choice_names:
                drinks = "socially"
        
        # Education (if not found in schools)
        if ("education" in desc_name or desc_id == "de_3") and not education:
            if choices:
                education = choices[0].get("name", "")
    
    # Check verification from badges
    verified = False
    for badge in user.get("badges", []):
        if badge.get("type") in ["selfie_verified", "id_verified", "photo_verified"]:
            verified = True
            break
    
    return {
        "app_id": user.get("_id", ""),
        "app_source": "tinder",
        "name": user.get("name", "Unknown"),
        "age": calculate_age(user["birth_date"]) if "birth_date" in user else 30,
        "city": city,
        "state": "",
        "country": "US",
        "bio": user.get("bio", ""),
        "interests": [],
        "occupation": occupation,
        "education": education,
        "photo_urls": photos[:6],
        "match_status": match_status,
        "verified": verified or user.get("is_verified", False),
        "distance_km": user.get("distance_mi", 0) * 1.6 if user.get("distance_mi") else None,
        "height_cm": height_cm,
        "smokes": smokes,
        "drinks": drinks,
    }


def convert_tinder_match_to_profile(match: dict) -> dict:
    """Convert a Tinder match object to our Profile format."""
    person = match.get("person", {})
    profile = convert_tinder_user_to_profile(person, match_status="mutual")
    
    # Add last message if available
    messages = match.get("messages", [])
    if messages:
        profile["last_message"] = messages[-1].get("message", "")
    
    return profile


def load_latest_tinder_data() -> dict:
    """Load the most recent Tinder data file."""
    data_dir = Path("data")
    
    # Try full data first, then regular data
    files = sorted(data_dir.glob("tinder_full_data_*.json"), reverse=True)
    if not files:
        files = sorted(data_dir.glob("tinder_data_*.json"), reverse=True)
    
    if not files:
        raise FileNotFoundError("No Tinder data files found. Run tinder_fetcher.py first!")
    
    latest_file = files[0]
    print(f"Loading: {latest_file}")
    
    with open(latest_file, "r") as f:
        return json.load(f)


def init_orchestrator():
    """Initialize the orchestrator with default config."""
    config = {
        "min_age": 18,
        "max_age": 100,
        "max_distance_km": 100,
        "must_not_smoke": False,
        "must_not_use_drugs": False,
        "use_clip": False,  # Disable CLIP for now
    }
    
    print("Initializing orchestrator...")
    response = requests.post(f"{API_BASE}/init", json=config)
    
    if response.status_code == 200:
        print("  Orchestrator initialized!")
        return True
    else:
        print(f"  Failed: {response.text}")
        return False


def hydrate_profiles(profiles: list):
    """Send profiles to the backend."""
    # Check if there's an endpoint to add profiles directly
    # If not, we need to add one to the API
    
    print(f"\nHydrating {len(profiles)} profiles...")
    
    response = requests.post(
        f"{API_BASE}/hydrate",
        json={"profiles": profiles}
    )
    
    if response.status_code == 200:
        print("  Profiles hydrated successfully!")
        return response.json()
    elif response.status_code == 404:
        print("  /hydrate endpoint not found. Adding it to the API...")
        return None
    else:
        print(f"  Failed: {response.text}")
        return None


def main():
    print("=" * 60)
    print(" HYDRATE DATING AGENT WITH TINDER DATA")
    print("=" * 60)
    
    # Load Tinder data
    data = load_latest_tinder_data()
    
    # Convert recommendations
    recs = data.get("recommendations", {}).get("data", {}).get("results", [])
    rec_profiles = []
    for rec in recs:
        if "user" in rec:
            profile = convert_tinder_user_to_profile(rec["user"], match_status="incoming")
            rec_profiles.append(profile)
    
    print(f"\nConverted {len(rec_profiles)} recommendations")
    
    # Convert likes_you (people who liked you)
    likes_you = data.get("likes_you", [])
    likes_profiles = []
    for like in likes_you:
        if "user" in like:
            profile = convert_tinder_user_to_profile(like["user"], match_status="incoming")
            likes_profiles.append(profile)
    
    print(f"Converted {len(likes_profiles)} likes (who liked you)")
    
    # Convert matches (handle both data structures)
    matches_raw = data.get("matches", [])
    if isinstance(matches_raw, dict):
        matches = matches_raw.get("data", {}).get("matches", [])
    else:
        matches = matches_raw  # Already a list
    match_profiles = []
    for match in matches:
        if "person" in match:
            profile = convert_tinder_match_to_profile(match)
            match_profiles.append(profile)
    
    print(f"Converted {len(match_profiles)} matches")
    
    # All profiles
    all_profiles = rec_profiles + match_profiles + likes_profiles
    print(f"\nTotal profiles to hydrate: {len(all_profiles)}")
    
    # Initialize orchestrator
    if not init_orchestrator():
        print("Failed to initialize. Is the backend running?")
        return
    
    # Try to hydrate
    result = hydrate_profiles(all_profiles)
    
    if result is None:
        print("\nThe /hydrate endpoint doesn't exist yet.")
        print("Let me add it to the API...")
        
        # Save profiles to a temp file so the API can load them
        temp_file = Path("data/profiles_to_hydrate.json")
        with open(temp_file, "w") as f:
            json.dump(all_profiles, f, indent=2)
        print(f"Saved profiles to: {temp_file}")
        print("\nNeed to add /hydrate endpoint to backend/api.py")
    
    print("\n" + "=" * 60)
    print(" SUMMARY")
    print("=" * 60)
    print(f"  Recommendations: {len(rec_profiles)}")
    print(f"  Matches: {len(match_profiles)}")
    print(f"  Total: {len(all_profiles)}")


if __name__ == "__main__":
    main()
