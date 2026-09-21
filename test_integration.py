#!/usr/bin/env python3
"""
Integration Test Script
Tests that all components of the dating agent work together.
"""

import sys
from datetime import datetime


def test_imports():
    """Test that all modules import correctly."""
    print("\n" + "=" * 70)
    print("TEST 1: Module Imports")
    print("=" * 70)
    
    try:
        from dating_agent.profile_aggregator import profile_aggregator
        from dating_agent.profile_store import profile_store
        from dating_agent.auth_handlers import HingeAuth, TinderAuth
        from dating_agent.fetchers import HingeProfileFetcher, TinderProfileFetcher
        
        print("  [OK] All modules import successfully")
        return True
    except Exception as e:
        print(f"  [FAIL] Import error: {e}")
        return False


def test_aggregator_init():
    """Test aggregator initialization."""
    print("\n" + "=" * 70)
    print("TEST 2: Aggregator Initialization")
    print("=" * 70)
    
    try:
        from dating_agent.profile_aggregator import profile_aggregator
        
        agg = profile_aggregator()
        
        # Check components
        assert agg.hinge_auth is not None, "Hinge auth not initialized"
        assert agg.tinder_auth is not None, "Tinder auth not initialized"
        assert agg.hinge_fetcher is not None, "Hinge fetcher not initialized"
        assert agg.tinder_fetcher is not None, "Tinder fetcher not initialized"
        assert agg.store is not None, "Profile store not initialized"
        
        print("  [OK] Aggregator initialized with all components")
        print(f"    - Hinge Auth: {type(agg.hinge_auth).__name__}")
        print(f"    - Tinder Auth: {type(agg.tinder_auth).__name__}")
        print(f"    - Hinge Fetcher: {type(agg.hinge_fetcher).__name__}")
        print(f"    - Tinder Fetcher: {type(agg.tinder_fetcher).__name__}")
        print(f"    - Profile Store: {type(agg.store).__name__}")
        
        return True
    except Exception as e:
        print(f"  [FAIL] Initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_auth_methods():
    """Test that auth methods exist."""
    print("\n" + "=" * 70)
    print("TEST 3: Authentication Methods")
    print("=" * 70)
    
    try:
        from dating_agent.profile_aggregator import profile_aggregator
        
        agg = profile_aggregator()
        
        # Check Hinge auth methods
        assert hasattr(agg.hinge_auth, 'request_phone_verification'), \
            "Hinge auth missing request_phone_verification"
        assert hasattr(agg.hinge_auth, 'verify_phone_otp'), \
            "Hinge auth missing verify_phone_otp"
        assert hasattr(agg.hinge_auth, 'is_authenticated'), \
            "Hinge auth missing is_authenticated"
        
        # Check Tinder auth methods
        assert hasattr(agg.tinder_auth, 'request_phone_verification'), \
            "Tinder auth missing request_phone_verification"
        assert hasattr(agg.tinder_auth, 'verify_phone_otp'), \
            "Tinder auth missing verify_phone_otp"
        assert hasattr(agg.tinder_auth, 'is_authenticated'), \
            "Tinder auth missing is_authenticated"
        
        print("  [OK] All auth methods present")
        print("    Hinge: request_phone_verification, verify_phone_otp, is_authenticated")
        print("    Tinder: request_phone_verification, verify_phone_otp, is_authenticated")
        
        return True
    except Exception as e:
        print(f"  [FAIL] Auth methods error: {e}")
        return False


def test_auth_flow_dry_run():
    """Test auth flow without real credentials."""
    print("\n" + "=" * 70)
    print("TEST 4: Authentication Flow (Dry Run)")
    print("=" * 70)
    
    try:
        from dating_agent.profile_aggregator import profile_aggregator
        
        agg = profile_aggregator()
        
        # Test Hinge request
        result = agg.hinge_auth.request_phone_verification("+1-555-555-5555")
        assert result['status'] == 'success', f"Hinge request failed: {result}"
        assert result['otp_id'] is not None, "Hinge request didn't return OTP ID"
        
        print("  [OK] Hinge phone verification request")
        print(f"    Status: {result['status']}")
        print(f"    OTP ID: {result['otp_id'][:20]}...")
        
        # Test Tinder request
        result = agg.tinder_auth.request_phone_verification("+1-555-555-5555")
        assert result['status'] == 'success', f"Tinder request failed: {result}"
        assert result['otp_id'] is not None, "Tinder request didn't return OTP ID"
        
        print("  [OK] Tinder phone verification request")
        print(f"    Status: {result['status']}")
        print(f"    OTP ID: {result['otp_id'][:20]}...")
        
        return True
    except Exception as e:
        print(f"  [FAIL] Auth flow error: {e}")
        return False


def test_database_operations():
    """Test database operations."""
    print("\n" + "=" * 70)
    print("TEST 5: Database Operations")
    print("=" * 70)
    
    try:
        from dating_agent.profile_store import profile_store
        import os
        
        # Use a test database
        test_db = "test_dating_agent.db"
        
        # Remove if exists
        if os.path.exists(test_db):
            os.remove(test_db)
        
        store = profile_store(test_db)
        
        # Test profile storage
        test_profile = {
            'platform': 'hinge',
            'platform_id': 'test_123',
            'name': 'Test User',
            'age': 28,
            'bio': 'Test bio for integration testing',
            'photos': ['https://example.com/photo1.jpg', 'https://example.com/photo2.jpg'],
            'interests': ['hiking', 'coding', 'coffee'],
            'location': 'San Francisco, CA',
            'distance_km': 5.2,
            'job': 'Software Engineer',
            'education': 'Stanford University',
            'height_cm': 175,
            'match_status': 'matched'
        }
        
        profile_id = store.store_profile(test_profile)
        assert profile_id > 0, "Profile storage returned invalid ID"
        
        print("  [OK] Profile stored successfully")
        print(f"    Profile ID: {profile_id}")
        
        # Test retrieval
        profiles = store.get_all_profiles(platform='hinge')
        assert len(profiles) == 1, f"Expected 1 profile, got {len(profiles)}"
        assert profiles[0]['name'] == 'Test User', "Retrieved profile has wrong name"
        
        print("  [OK] Profile retrieved successfully")
        print(f"    Retrieved: {profiles[0]['name']}, age {profiles[0]['age']}")
        
        # Test stats
        stats = store.get_stats()
        assert stats['total_profiles'] == 1, f"Expected 1 total profile, got {stats['total_profiles']}"
        assert 'hinge' in stats['by_platform'], "Hinge not in platform stats"
        
        print("  [OK] Database stats")
        print(f"    Total profiles: {stats['total_profiles']}")
        print(f"    By platform: {stats['by_platform']}")
        
        # Cleanup
        store.close()
        os.remove(test_db)
        
        return True
    except Exception as e:
        print(f"  [FAIL] Database error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backend_api():
    """Test backend API imports."""
    print("\n" + "=" * 70)
    print("TEST 6: Backend API")
    print("=" * 70)
    
    try:
        import sys
        import os
        
        # Add backend to path
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        sys.path.insert(0, backend_path)
        
        from api import app
        
        assert app is not None, "Flask app not created"
        
        print("  [OK] Backend API imports successfully")
        print(f"    Flask app: {app}")
        print(f"    Available routes:")
        for rule in app.url_map.iter_rules():
            print(f"      {rule.methods} {rule.rule}")
        
        return True
    except Exception as e:
        print(f"  [FAIL] Backend API error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n")
    print("=" * 70)
    print("DATING AGENT INTEGRATION TEST SUITE")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Run tests
    results.append(("Module Imports", test_imports()))
    results.append(("Aggregator Init", test_aggregator_init()))
    results.append(("Auth Methods", test_auth_methods()))
    results.append(("Auth Flow", test_auth_flow_dry_run()))
    results.append(("Database Ops", test_database_operations()))
    results.append(("Backend API", test_backend_api()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nSUCCESS! All integration tests passed!")
        print("\nNext steps:")
        print("  1. Test with real Hinge/Tinder credentials")
        print("  2. Run: python quick_start_hinge.py")
        print("  3. Run: python quick_start_tinder.py")
        print("  4. Start backend: cd backend && python api.py")
        return 0
    else:
        print("\nFAILURE: Some tests failed. See output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
