#!/usr/bin/env python3
"""
Hydrate the Dating Agent app with Hinge data from mitmproxy flows.
"""

import json
import requests
from dataclasses import dataclass, asdict
from typing import List, Optional

API_BASE = "http://localhost:5001"


@dataclass
class Profile:
    app_id: str  # Changed from id
    name: str
    age: int
    bio: str
    photo_urls: List[str]
    city: str
    state: str
    distance_km: Optional[int]
    interests: List[str]
    occupation: str
    education: str
    height_cm: Optional[int]
    smokes: str
    drinks: str
    drugs: str
    religion: Optional[str]
    politics: Optional[str]
    verified: bool
    match_status: str
    app_source: str  # Changed from source_app
    ethnicity: Optional[str] = None


# Hinge ethnicity code mapping
HINGE_ETHNICITY_MAP = {
    1: "Black",
    2: "East Asian",
    3: "Hispanic/Latino",
    4: "Middle Eastern",
    5: "Native American",
    6: "Pacific Islander",
    7: "South Asian",
    8: "White",
    9: "Other",
}


def load_hinge_data() -> dict:
    """Load extracted Hinge data."""
    with open("data/hinge_extracted.json", "r") as f:
        return json.load(f)


def convert_hinge_profile(user_data: dict, content_data: dict, match_status: str = "incoming") -> Profile:
    """Convert Hinge user/content data to our Profile model."""
    profile = user_data.get("profile", {})
    if not isinstance(profile, dict):
        raise ValueError(f"Profile is not a dict: {type(profile)}")
    
    content = content_data.get("content", {})
    if not isinstance(content, dict):
        content = {}
    
    # Get location
    location = profile.get("location", {})
    if isinstance(location, dict):
        city = location.get("name", "")
        state = location.get("adminArea1Short", "")
    else:
        city = str(location) if location else ""
        state = ""
    
    # Get photos
    photos = content.get("photos", [])
    photo_urls = []
    for p in photos:
        if isinstance(p, dict):
            url = p.get("url", "")
            if not url and p.get("cdnId"):
                url = f"https://media.hingenexus.com/image/upload/{p.get('cdnId')}.jpg"
            if url:
                photo_urls.append(url)
    
    # Get prompts as bio
    prompts = content.get("prompts", [])
    bio_parts = []
    for prompt in prompts[:3]:
        if isinstance(prompt, dict):
            q = prompt.get("question", "")
            a = prompt.get("answer", "")
            if q and a:
                bio_parts.append(f"{q}: {a}")
    bio = "\n".join(bio_parts) if bio_parts else ""
    
    # Get lifestyle values (Hinge uses numeric codes - directly as ints)
    drinking_map = {1: "no", 2: "rarely", 3: "socially", 4: "often"}
    smoking_map = {1: "no", 2: "socially", 3: "often"}
    drugs_map = {1: "no", 2: "sometimes", 3: "often"}
    
    drinking = profile.get("drinking", 0)
    smoking = profile.get("smoking", 0)
    drugs = profile.get("drugs", 0)
    marijuana = profile.get("marijuana", 0)
    
    # Handle both int and dict formats
    if isinstance(drinking, dict):
        drinking = drinking.get("value", 0)
    if isinstance(smoking, dict):
        smoking = smoking.get("value", 0)
    if isinstance(drugs, dict):
        drugs = drugs.get("value", 0)
    if isinstance(marijuana, dict):
        marijuana = marijuana.get("value", 0)
    
    # Get education
    educations = profile.get("educations", [])
    if isinstance(educations, dict):
        educations = educations.get("value", [])
    education = educations[0] if educations else ""
    
    # Get job
    job_title = profile.get("jobTitle", "")
    if isinstance(job_title, dict):
        job_title = job_title.get("value", "")
    works = profile.get("works", "")
    if isinstance(works, dict):
        works = works.get("value", "")
    occupation = job_title or works
    
    # Get ethnicity
    ethnicities = profile.get("ethnicities", [])
    if isinstance(ethnicities, dict):
        ethnicities = ethnicities.get("value", [])
    ethnicity_names = [HINGE_ETHNICITY_MAP.get(e, "Other") for e in ethnicities if isinstance(e, int)]
    ethnicity = ", ".join(ethnicity_names) if ethnicity_names else None
    
    return Profile(
        app_id=str(user_data.get("userId", "")),
        name=profile.get("firstName", "Unknown"),
        age=profile.get("age", 0),
        bio=bio,
        photo_urls=photo_urls,
        city=city,
        state=state,
        distance_km=None,
        interests=[],
        occupation=occupation if isinstance(occupation, str) else "",
        education=education if isinstance(education, str) else "",
        height_cm=profile.get("height"),
        smokes=smoking_map.get(smoking, "unknown"),
        drinks=drinking_map.get(drinking, "unknown"),
        drugs=drugs_map.get(drugs or marijuana, "unknown"),
        religion=None,
        politics=None,
        verified=profile.get("selfieVerified", False),
        match_status=match_status,
        app_source="hinge",
        ethnicity=ethnicity,
    )


def main():
    print("=" * 60)
    print(" HYDRATE DATING AGENT WITH HINGE DATA")
    print("=" * 60)
    
    # Load extracted Hinge data
    data = load_hinge_data()
    
    # Build user profile and content dictionaries
    user_profiles = {}
    content_by_user = {}
    
    users = data.get("POST /user/v3/public", {}).get("data", [])
    for user in users:
        uid = user.get("userId")
        if uid:
            user_profiles[uid] = user
    
    contents = data.get("POST /content/v2/public", {}).get("data", [])
    for content in contents:
        uid = content.get("userId")
        if uid:
            content_by_user[uid] = content
    
    print(f"Loaded {len(user_profiles)} user profiles")
    print(f"Loaded {len(content_by_user)} content entries")
    
    # Get connections (matches)
    connections_data = data.get("GET /connection/v2", {}).get("data", {})
    connections = connections_data.get("connections", [])
    
    # Get standouts
    standouts_data = data.get("GET /standouts/v3", {}).get("data", {})
    standouts = standouts_data.get("standouts", [])
    
    # Get discover feed
    rec_data = data.get("POST /rec/v2", {}).get("data", {})
    feeds = rec_data.get("feeds", [])
    discover_subjects = []
    for feed in feeds:
        subjects = feed.get("subjects", [])
        discover_subjects.extend(subjects)
    
    print(f"Connections: {len(connections)}")
    print(f"Standouts: {len(standouts)}")
    print(f"Discover subjects: {len(discover_subjects)}")
    
    # Convert profiles
    all_profiles = []
    converted_ids = set()
    
    # Convert user profiles we have full data for
    for uid, user_data in user_profiles.items():
        if uid in converted_ids:
            continue
        
        content_data = content_by_user.get(uid, {"content": {}})
        
        # Check if this is a match
        is_match = any(c.get("subjectId") == uid or c.get("initiatorId") == uid for c in connections)
        match_status = "mutual" if is_match else "incoming"
        
        try:
            profile = convert_hinge_profile(user_data, content_data, match_status)
            all_profiles.append(profile)
            converted_ids.add(uid)
        except Exception as e:
            print(f"  Error converting {uid}: {e}")
    
    print(f"\nConverted {len(all_profiles)} Hinge profiles")
    
    # Hydrate the app via API
    print(f"\nHydrating {len(all_profiles)} profiles via API...")
    
    profiles_data = [asdict(p) for p in all_profiles]
    
    try:
        response = requests.post(
            f"{API_BASE}/hydrate",
            json={"profiles": profiles_data},
            timeout=30
        )
        
        if response.status_code == 200:
            print("  Profiles hydrated successfully!")
        else:
            print(f"  Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"  Error posting to API: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(" SUMMARY")
    print("=" * 60)
    
    matches = sum(1 for p in all_profiles if p.match_status == "mutual")
    likes = sum(1 for p in all_profiles if p.match_status == "incoming")
    
    print(f"  Hinge profiles: {len(all_profiles)}")
    print(f"  Matches: {matches}")
    print(f"  Incoming likes: {likes}")
    
    # Show sample profiles
    print("\n  Sample profiles:")
    for p in all_profiles[:5]:
        photos = len(p.photo_urls) if p.photo_urls else 0
        print(f"    - {p.name}, {p.age}, {p.city} ({photos} photos)")


if __name__ == "__main__":
    main()
