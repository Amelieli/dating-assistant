#!/usr/bin/env python3
"""
Quick Start: Tinder Profile Aggregator

WARNING: Tinder actively detects and blocks scrapers.
This tool uses reverse-engineered APIs.
Use responsibly and at your own risk.

This script:
1. Authenticates with Tinder
2. Fetches profiles
3. Stores in unified database (together with Hinge profiles)
4. Finds duplicates across platforms
5. Generates report

Usage:
    python quick_start_tinder.py
"""

import sys
from datetime import datetime


def main():
    print("\n" + "="*70)
    print("TINDER PROFILE AGGREGATOR - QUICK START")
    print("="*70 + "\n")
    
    # IMPORTANT WARNING
    print("WARNING: IMPORTANT LEGAL & SAFETY INFORMATION")
    print("-" * 70)
    print("""
Tinder explicitly prohibits automated scrapers in their Terms of Service.
Using this tool may:
  - Violate Tinder's TOS and get your account banned
  - Trigger legal action from Tinder
  - Result in IP bans
  - Violate the CFAA (Computer Fraud and Abuse Act)

This implementation uses reverse-engineered APIs which may change
without notice and can result in bans.

Anti-Detection Measures:
  - User-Agent rotation (appears as different iOS versions)
  - Random delays between requests
  - Device fingerprinting
  - Rate limiting (very conservative)
  - Ban detection and automatic cooldown

Even with these measures, you WILL likely get banned if you're
too aggressive with fetching.

Recommendations:
  - Use on test/throwaway accounts only
  - Don't fetch thousands of profiles
  - Space out requests over time
  - Monitor for rate limit errors (429)
  - Watch for auth errors (401) or bans (403)
  - Check ban_detected status frequently

By continuing, you accept all risks.
    """)
    
    response = input("Do you understand the risks? (yes/no): ").strip().lower()
    if response != 'yes':
        print("\n[CANCELLED] Not proceeding.")
        sys.exit(0)
    
    # Step 0: Initialize
    print("\n\nSTEP 0: Initializing system...")
    try:
        from dating_agent.profile_aggregator import profile_aggregator
        agg = profile_aggregator()
        print("  [OK] Aggregator initialized")
        print("  [OK] All 17 tools loaded successfully\n")
    except Exception as e:
        print(f"  [ERROR] Failed to initialize: {e}")
        sys.exit(1)
    
    # Step 1: Tinder authentication
    print("STEP 1: Request Tinder phone verification")
    print("-" * 70)
    phone = input("\nEnter your phone number (format: +1-555-123-4567): ").strip()
    
    if not phone:
        print("[CANCEL] No phone entered")
        sys.exit(0)
    
    print(f"\n  Requesting OTP for {phone}...")
    auth = agg.tinder_auth
    
    try:
        req = auth.request_phone_verification(phone)
        
        if req['status'] != 'success':
            print(f"  [ERROR] {req['message']}")
            sys.exit(1)
        
        otp_id = req['otp_id']
        print(f"  [OK] OTP sent to {req['message']}")
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        sys.exit(1)
    
    # Step 2: Verify OTP
    print("\nSTEP 2: Verify OTP code")
    print("-" * 70)
    code = input("\nEnter the 6-digit code from SMS: ").strip()
    
    if not code or len(code) != 6 or not code.isdigit():
        print("[ERROR] Invalid code. Must be 6 digits.")
        sys.exit(1)
    
    print(f"\n  Verifying code {code}...")
    
    try:
        verify = auth.verify_phone_otp(otp_id, code)
        
        if verify['status'] != 'success':
            print(f"  [ERROR] {verify['message']}")
            sys.exit(1)
        
        user_id = verify['user_id']
        device_id = verify['device_id']
        
        print(f"  [OK] Authentication successful!")
        print(f"  [OK] User ID: {user_id}")
        print(f"  [OK] Device ID: {device_id[:8]}...")
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        sys.exit(1)
    
    # Step 3: Run Tinder sync
    print("\nSTEP 3: Fetching and storing Tinder profiles")
    print("-" * 70)
    print(f"\n  Starting Tinder sync for {user_id}...")
    print("  This may take 3-10 minutes depending on how aggressive we need to be.")
    print("  Watch for rate limit messages (429) - the system will automatically back off.\n")
    
    try:
        result = agg.run_full_sync(
            hinge_user_id=None,  # Skip Hinge for now
            tinder_user_id=user_id,
            limit=100,
            find_duplicates=True,
            download_photos=True
        )
        
        print("\n  [OK] Sync completed!")
        
    except Exception as e:
        print(f"\n  [ERROR] Sync failed: {e}")
        sys.exit(1)
    
    # Step 4: Display results
    print("\nSTEP 4: Results")
    print("-" * 70)
    
    if result['status'] == 'success':
        print("\n  SUMMARY:")
        
        # Tinder results
        if 'platforms' in result and 'tinder' in result['platforms']:
            tinder = result['platforms']['tinder']
            print(f"\n  Tinder Results:")
            print(f"    - Profiles fetched: {tinder['profiles_fetched']}")
            print(f"    - Profiles stored: {tinder['profiles_stored']}")
            print(f"    - Errors: {tinder['errors']}")
            print(f"    - Duration: {tinder['duration_seconds']:.1f}s")
            
            # Check for ban detection
            if tinder['errors'] > 10:
                print(f"\n  [WARNING] High error rate detected!")
                print(f"            Account may be at risk of ban.")
                print(f"            Stop fetching and wait 24+ hours.")
        
        # Deduplication
        if 'deduplication' in result:
            dedup = result['deduplication']
            print(f"\n  Deduplication Results:")
            print(f"    - Profiles checked: {dedup['profiles_checked']}")
            print(f"    - Duplicates found: {dedup['duplicates_found']}")
        
        # Database
        if 'database_stats' in result:
            db = result['database_stats']
            print(f"\n  Database Stats:")
            print(f"    - Total profiles: {db['total_profiles']}")
            print(f"    - By platform: {db['by_platform']}")
            print(f"    - Duplicate pairs: {db['duplicate_pairs']}")
        
        print(f"\n  Total time: {result['duration_seconds']:.1f} seconds")
        
    else:
        print(f"\n  ERROR: {result.get('message', 'Unknown error')}")
        sys.exit(1)
    
    # Step 5: Export report
    print("\nSTEP 5: Exporting report")
    print("-" * 70)
    
    report_file = f"tinder_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    print(f"\n  Exporting to {report_file}...")
    
    try:
        success = agg.export_sync_report(report_file)
        
        if success:
            print(f"  [OK] Report exported!")
            print(f"  [OK] File: {report_file}")
        else:
            print(f"  [WARNING] Could not export report")
            
    except Exception as e:
        print(f"  [WARNING] Export failed: {e}")
    
    # Step 6: Next steps
    print("\nSTEP 6: What's next?")
    print("-" * 70)
    print("""
  Your Tinder data is now merged with Hinge data in:
    - dating_agent.db (unified SQLite database)
    - dating_agent_photos/ (all profile photos)
    - tinder_sync_*.json (detailed report)

  Important:
    1. Monitor ban_detected status in logs
    2. Wait 24+ hours before syncing again
    3. Check error rates - stop if >20% errors
    4. Watch for 429 (rate limit) responses
    5. Watch for 403 (forbidden/ban) responses

  You can now:
    1. Query profiles from both Hinge and Tinder
    2. Find duplicates across platforms
    3. Export combined data
    4. Analyze combined dataset

  To find same person on both platforms:
    from dating_agent.profile_store import profile_store
    store = profile_store()
    duplicates = store.get_duplicates()
    for dup in duplicates:
        if dup['platform_1'] != dup['platform_2']:
            print(f"Same person: {dup['name_1']} on Hinge & Tinder")

  To check ban status:
    auth_status = agg.tinder_auth.get_auth_status()
    print(f"Ban detected: {auth_status['ban_detected']}")
    print(f"Users: {auth_status['authenticated_user_ids']}")
    """)
    
    # Final status
    print("\n" + "="*70)
    print("SUCCESS! Tinder profiles merged with existing data.")
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
