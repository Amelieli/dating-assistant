#!/usr/bin/env python3
"""
Quick Start: Hinge Profile Aggregator

This script walks you through the complete workflow:
1. Authenticate with Hinge
2. Fetch profiles
3. Store in database
4. Find duplicates
5. Export report

Usage:
    python quick_start_hinge.py
"""

import sys
from datetime import datetime


def main():
    print("\n" + "="*70)
    print("HINGE PROFILE AGGREGATOR - QUICK START")
    print("="*70 + "\n")
    
    # Step 0: Initialize
    print("STEP 0: Initializing system...")
    try:
        from dating_agent.profile_aggregator import profile_aggregator
        agg = profile_aggregator()
        print("  [OK] Aggregator initialized")
        print("  [OK] All 15 tools loaded successfully\n")
    except Exception as e:
        print(f"  [ERROR] Failed to initialize: {e}")
        print("\n  Make sure you're in the right directory")
        print("  and all dating_agent modules are available.")
        sys.exit(1)
    
    # Step 1: Request phone verification
    print("STEP 1: Request phone verification")
    print("-" * 70)
    phone = input("\nEnter your phone number (format: +1-555-123-4567): ").strip()
    
    if not phone:
        print("[CANCEL] No phone entered")
        sys.exit(0)
    
    print(f"\n  Requesting OTP for {phone}...")
    auth = agg.hinge_auth
    
    try:
        req = auth.request_phone_verification(phone)
        
        if req['status'] != 'success':
            print(f"  [ERROR] {req['message']}")
            sys.exit(1)
        
        otp_id = req['otp_id']
        print(f"  [OK] OTP sent to {req['message']}")
        print(f"  [OK] OTP ID: {otp_id[:20]}...")
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        sys.exit(1)
    
    # Step 2: Verify OTP
    print("\nSTEP 2: Verify OTP code")
    print("-" * 70)
    code = input("\nEnter the 6-digit code from SMS: ").strip()
    
    if not code or len(code) != 6 or not code.isdigit():
        print("[ERROR] Invalid code format. Must be 6 digits.")
        sys.exit(1)
    
    print(f"\n  Verifying code {code}...")
    
    try:
        verify = auth.verify_phone_otp(otp_id, code)
        
        if verify['status'] != 'success':
            print(f"  [ERROR] {verify['message']}")
            sys.exit(1)
        
        user_id = verify['user_id']
        session_id = verify['session_id']
        
        print(f"  [OK] Authentication successful!")
        print(f"  [OK] User ID: {user_id}")
        print(f"  [OK] Session ID: {session_id[:20]}...")
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        sys.exit(1)
    
    # Step 3: Run full sync
    print("\nSTEP 3: Fetching and storing profiles")
    print("-" * 70)
    print(f"\n  Starting profile sync for {user_id}...")
    print("  This may take 2-5 minutes depending on network speed.\n")
    
    try:
        result = agg.run_full_sync(
            hinge_user_id=user_id,
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
        
        # Hinge results
        if 'platforms' in result and 'hinge' in result['platforms']:
            hinge = result['platforms']['hinge']
            print(f"\n  Hinge Results:")
            print(f"    - Profiles fetched: {hinge['profiles_fetched']}")
            print(f"    - Profiles stored: {hinge['profiles_stored']}")
            print(f"    - Errors: {hinge['errors']}")
            print(f"    - Duration: {hinge['duration_seconds']:.1f}s")
        
        # Deduplication results
        if 'deduplication' in result:
            dedup = result['deduplication']
            print(f"\n  Deduplication Results:")
            print(f"    - Profiles checked: {dedup['profiles_checked']}")
            print(f"    - Duplicates found: {dedup['duplicates_found']}")
        
        # Database stats
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
    
    report_file = f"hinge_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
    
    # Step 6: Show what's next
    print("\nSTEP 6: What's next?")
    print("-" * 70)
    print("""
  Your data is now stored in:
    - dating_agent.db (SQLite database)
    - dating_agent_photos/ (downloaded photos)
    - aggregation_report.json (detailed report)
    - hinge_auth_log.json (authentication events)

  You can now:
    1. Query the database for profiles
    2. Analyze the exported data
    3. Build additional integrations (Tinder, League)
    4. Set up automated syncs

  To query the database:
    from dating_agent.profile_store import profile_store
    store = profile_store()
    all_profiles = store.get_all_profiles()
    
  To check statistics:
    stats = store.get_stats()
    print(f"Total profiles: {stats['total_profiles']}")
    """)
    
    # Final summary
    print("\n" + "="*70)
    print("SUCCESS! Your Hinge profiles are now aggregated.")
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
