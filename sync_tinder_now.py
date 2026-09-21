#!/usr/bin/env python3
"""
Sync Real Tinder Profiles - Using Your Token!
"""

import json
import sys
from datetime import datetime

print("\n" + "="*70)
print("SYNCING REAL TINDER PROFILES")
print("="*70 + "\n")

# Load your token
try:
    with open('tinder_creds.json') as f:
        creds = json.load(f)
    
    print(f"[OK] Loaded token: {creds['tinder_token'][:20]}...")
    print()
except Exception as e:
    print(f"[ERROR] Failed to load token: {e}")
    sys.exit(1)

# Initialize the aggregator
try:
    from dating_agent.profile_aggregator import profile_aggregator
    
    print("Initializing dating agent...")
    agg = profile_aggregator()
    print("[OK] Aggregator ready!")
    print()
except Exception as e:
    print(f"[ERROR] Failed to initialize: {e}")
    sys.exit(1)

# Set your credentials
print("Setting up Tinder authentication...")
agg.tinder_auth.credentials = {
    'auth_token': creds['tinder_token'],
    'user_id': creds.get('user_id', 'from_web'),
    'device_id': creds.get('device_id', 'web_browser'),
    'authenticated_at': datetime.now().isoformat()
}
print("[OK] Credentials set!")
print()

# Sync profiles with rate limiting
print("="*70)
print("SYNCING PROFILES (this will be slow due to rate limiting)")
print("="*70)
print()
print("Rate limiting settings:")
print("  - 4 requests per minute")
print("  - 5-10 second delays between requests")
print("  - This protects your account!")
print()

try:
    sync_result = agg.run_full_sync(
        tinder_user_id='from_web',
        limit=20,  # Start with 20 profiles
        find_duplicates=True
    )
    
    print("\n" + "="*70)
    print("SYNC COMPLETE!")
    print("="*70 + "\n")
    
    if 'platforms' in sync_result and 'tinder' in sync_result['platforms']:
        tinder = sync_result['platforms']['tinder']
        print(f"Results:")
        print(f"  Profiles fetched: {tinder.get('profiles_fetched', 0)}")
        print(f"  Profiles stored: {tinder.get('profiles_stored', 0)}")
        print(f"  Errors: {tinder.get('errors', 0)}")
        print(f"  Duration: {tinder.get('duration_seconds', 0):.1f}s")
        print()
        
        # Show some profiles
        profiles = agg.get_all_profiles('tinder')
        
        if profiles:
            print(f"Sample of your {len(profiles)} Tinder profiles:")
            print("-" * 70)
            for i, p in enumerate(profiles[:5], 1):
                print(f"\n{i}. {p.get('name', 'Unknown')}, {p.get('age', '?')}")
                if p.get('location'):
                    print(f"   Location: {p['location']}")
                if p.get('distance_km'):
                    print(f"   Distance: {p['distance_km']} km")
                if p.get('bio'):
                    bio = p['bio'][:100] + '...' if len(p['bio']) > 100 else p['bio']
                    print(f"   Bio: {bio}")
            
            if len(profiles) > 5:
                print(f"\n... and {len(profiles) - 5} more profiles!")
        else:
            print("No profiles stored yet. Check for errors above.")
    else:
        print("[WARNING] No Tinder results in sync response")
        print(f"Full response: {sync_result}")
    
    # Show database stats
    print("\n" + "="*70)
    print("DATABASE STATS")
    print("="*70 + "\n")
    
    stats = agg.get_stats()
    print(f"Total profiles: {stats['total_profiles']}")
    print(f"By platform: {stats['by_platform']}")
    print()
    
    # Check rate limiter health
    from dating_agent.rate_limiter import get_rate_limiter
    limiter = get_rate_limiter('tinder')
    limiter_stats = limiter.get_stats('tinder')
    
    print("Rate Limiter Status:")
    print(f"  Total requests: {limiter_stats['total_requests']}")
    print(f"  Total errors: {limiter_stats['total_errors']}")
    print(f"  Healthy: {limiter.is_healthy('tinder')}")
    print()
    
    print("="*70)
    print("SUCCESS! View your profiles at: http://localhost:5001")
    print("="*70)
    
except Exception as e:
    print(f"\n[ERROR] Sync failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
