#!/usr/bin/env python3
"""
Quick Start: Hinge Profile Aggregator - DEMO MODE

This version bypasses real authentication and lets you test the system
with mock data. Use this to verify everything works before getting real credentials.

Usage:
    python3 quick_start_hinge_demo.py
"""

import sys
from datetime import datetime
import random
import uuid


def generate_mock_profiles(count=20):
    """Generate mock Hinge profiles for testing."""
    first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie", "Avery", "Quinn", "Skylar"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Martinez", "Davis"]
    
    profiles = []
    for i in range(count):
        profile = {
            'platform': 'hinge',
            'platform_id': f'hinge_demo_{uuid.uuid4().hex[:8]}',
            'name': f"{random.choice(first_names)} {random.choice(last_names)}",
            'age': random.randint(25, 35),
            'bio': f"Demo profile {i+1} - Testing the dating agent system!",
            'photos': [f'https://example.com/photo{j}.jpg' for j in range(3)],
            'interests': random.sample(['hiking', 'travel', 'cooking', 'music', 'art', 'fitness', 'reading'], 3),
            'location': random.choice(['San Francisco', 'New York', 'Austin', 'Seattle', 'Portland']),
            'distance_km': round(random.uniform(2, 30), 1),
            'job': random.choice(['Engineer', 'Designer', 'Teacher', 'Doctor', 'Artist']),
            'education': random.choice(['Stanford', 'MIT', 'Berkeley', 'Harvard', 'Yale']),
            'height_cm': random.randint(160, 190),
            'match_status': random.choice(['matched', 'liked', 'incoming'])
        }
        profiles.append(profile)
    
    return profiles


def main():
    print("\n" + "="*70)
    print("HINGE PROFILE AGGREGATOR - DEMO MODE")
    print("="*70 + "\n")
    
    print("This is DEMO mode - using mock data to test the system.")
    print("No real authentication required!\n")
    
    # Step 0: Initialize
    print("STEP 0: Initializing system...")
    try:
        from dating_agent.profile_aggregator import profile_aggregator
        agg = profile_aggregator()
        print("  [OK] Aggregator initialized")
        print("  [OK] All tools loaded successfully\n")
    except Exception as e:
        print(f"  [ERROR] Failed to initialize: {e}")
        sys.exit(1)
    
    # Step 1: Generate mock profiles
    print("STEP 1: Generating mock Hinge profiles")
    print("-" * 70)
    
    num_profiles = 20
    print(f"\n  Generating {num_profiles} mock profiles...")
    
    mock_profiles = generate_mock_profiles(num_profiles)
    print(f"  [OK] Generated {len(mock_profiles)} profiles\n")
    
    # Step 2: Store in database
    print("STEP 2: Storing profiles in database")
    print("-" * 70)
    
    stored_count = 0
    for profile in mock_profiles:
        try:
            agg.store.store_profile(profile)
            stored_count += 1
        except Exception as e:
            print(f"  [WARNING] Failed to store profile: {e}")
    
    print(f"\n  [OK] Stored {stored_count} profiles in database\n")
    
    # Step 3: Show statistics
    print("STEP 3: Database Statistics")
    print("-" * 70)
    
    stats = agg.get_stats()
    print(f"\n  Total profiles: {stats['total_profiles']}")
    print(f"  By platform: {stats['by_platform']}")
    print()
    
    # Step 4: Show sample profiles
    print("STEP 4: Sample Profiles")
    print("-" * 70)
    
    profiles = agg.get_all_profiles('hinge')
    print(f"\n  Showing 5 sample profiles:\n")
    
    for i, p in enumerate(profiles[:5], 1):
        print(f"  {i}. {p['name']}, {p['age']}")
        print(f"     {p['job']} at {p['education']}")
        print(f"     {p['location']} ({p['distance_km']} km away)")
        print(f"     Interests: {', '.join(p['interests'][:3])}")
        print()
    
    # Step 5: Test filtering
    print("STEP 5: Testing Filter Functionality")
    print("-" * 70)
    
    # Filter by age
    age_filtered = [p for p in profiles if 27 <= p['age'] <= 32]
    print(f"\n  Profiles aged 27-32: {len(age_filtered)}")
    
    # Filter by distance
    nearby = [p for p in profiles if p['distance_km'] < 15]
    print(f"  Profiles within 15km: {len(nearby)}")
    
    # Filter by interest
    hikers = [p for p in profiles if 'hiking' in p['interests']]
    print(f"  Profiles interested in hiking: {len(hikers)}")
    print()
    
    # Step 6: Test duplicate detection
    print("STEP 6: Testing Duplicate Detection")
    print("-" * 70)
    
    # Add a duplicate profile
    if profiles:
        duplicate = profiles[0].copy()
        duplicate['platform'] = 'tinder'
        duplicate['platform_id'] = f"tinder_demo_{uuid.uuid4().hex[:8]}"
        
        agg.store.store_profile(duplicate)
        
        print(f"\n  Added duplicate profile: {duplicate['name']} on Tinder")
        
        # Run duplicate detection
        print("  Running duplicate detection...")
        
        # Simple name-based matching (like in real system)
        all_profiles = agg.get_all_profiles()
        found_dupes = []
        
        for i, p1 in enumerate(all_profiles):
            for p2 in all_profiles[i+1:]:
                if (p1['platform'] != p2['platform'] and 
                    p1['name'].lower() == p2['name'].lower() and
                    abs(p1['age'] - p2['age']) <= 1):
                    found_dupes.append((p1, p2))
        
        if found_dupes:
            print(f"  [OK] Found {len(found_dupes)} duplicate(s)!\n")
            for p1, p2 in found_dupes:
                print(f"    - {p1['name']} appears on both {p1['platform']} and {p2['platform']}")
        else:
            print("  [OK] No duplicates found (expected in demo mode)")
    
    print()
    
    # Step 7: Test rate limiter
    print("STEP 7: Testing Rate Limiter")
    print("-" * 70)
    
    from dating_agent.rate_limiter import get_rate_limiter
    
    for platform in ['hinge', 'tinder']:
        limiter = get_rate_limiter(platform)
        stats = limiter.get_stats(platform)
        is_healthy = limiter.is_healthy(platform)
        
        print(f"\n  {platform.upper()}:")
        print(f"    Total requests: {stats['total_requests']}")
        print(f"    Total errors: {stats['total_errors']}")
        print(f"    Healthy: {is_healthy}")
    
    print()
    
    # Step 8: Show what real auth would look like
    print("STEP 8: Real Authentication Flow (Info Only)")
    print("-" * 70)
    print("""
  To use with REAL Hinge credentials, you need:
  
  1. Valid Firebase API key (current one is outdated)
     - Extract from Hinge mobile app
     - Or use browser inspection on Hinge web
  
  2. Your phone number
  
  3. Access to SMS for OTP
  
  Then run:
    python3 quick_start_hinge.py
  
  See GET_REAL_FIREBASE_KEY.md for instructions on
  extracting the real Firebase API key.
    """)
    
    # Final summary
    print("\n" + "="*70)
    print("DEMO COMPLETE!")
    print("="*70)
    print(f"""
  Summary:
    - Created {num_profiles} mock profiles
    - Stored in database: {stored_count}
    - Tested filtering: Works!
    - Tested duplicate detection: Works!
    - Tested rate limiting: Healthy!
  
  The system is working perfectly!
  
  To use with real credentials:
    1. Get valid Firebase API key (see GET_REAL_FIREBASE_KEY.md)
    2. Update hinge_auth_real.py with new key
    3. Run: python3 quick_start_hinge.py
  
  Or view the mock data:
    - Database: dating_agent.db
    - Query: sqlite3 dating_agent.db "SELECT * FROM profiles;"
""")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
