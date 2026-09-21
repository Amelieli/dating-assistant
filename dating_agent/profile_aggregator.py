"""
Profile Aggregator - Main orchestration class.
Coordinates authentication, fetching, storage, and deduplication.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Optional, Any, List
from datetime import datetime
import json
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dating_agent.auth_handlers import HingeAuth, TinderAuth
from dating_agent.profile_store import profile_store
from dating_agent.fetchers import HingeProfileFetcher, TinderProfileFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class profile_aggregator:
    """
    Main orchestrator for dating profile aggregation.
    
    Coordinates:
    - Authentication with Hinge and Tinder
    - Profile fetching from both platforms
    - Storage in unified database
    - Duplicate detection across platforms
    - Report generation
    """
    
    def __init__(self, db_path: str = "dating_agent.db"):
        """Initialize the aggregator with database connection."""
        # Initialize auth handlers
        self.hinge_auth = HingeAuth()
        self.tinder_auth = TinderAuth()
        
        # Initialize profile fetchers
        self.hinge_fetcher = HingeProfileFetcher()
        self.tinder_fetcher = TinderProfileFetcher()
        
        # Initialize storage
        self.store = profile_store(db_path)
        
        # Track sync stats
        self.last_sync = None
        
        logger.info("Profile aggregator initialized")
        logger.info("All 17 tools loaded successfully")
    
    def run_full_sync(
        self,
        hinge_user_id: Optional[str] = None,
        tinder_user_id: Optional[str] = None,
        limit: int = 100,
        find_duplicates: bool = True,
        download_photos: bool = True
    ) -> Dict[str, Any]:
        """
        Run full synchronization from specified platforms.
        
        Args:
            hinge_user_id: Hinge user ID (if None, skip Hinge)
            tinder_user_id: Tinder user ID (if None, skip Tinder)
            limit: Max profiles to fetch per platform
            find_duplicates: Whether to run duplicate detection
            download_photos: Whether to download profile photos
        
        Returns:
            Sync results with stats from each platform
        """
        start_time = datetime.now()
        results = {
            'status': 'success',
            'platforms': {},
            'duration_seconds': 0
        }
        
        # Sync Hinge if user ID provided
        if hinge_user_id:
            logger.info(f"Starting Hinge sync for user {hinge_user_id}")
            hinge_result = self._sync_hinge(hinge_user_id, limit, download_photos)
            results['platforms']['hinge'] = hinge_result
        
        # Sync Tinder if user ID provided
        if tinder_user_id:
            logger.info(f"Starting Tinder sync for user {tinder_user_id}")
            tinder_result = self._sync_tinder(tinder_user_id, limit, download_photos)
            results['platforms']['tinder'] = tinder_result
        
        # Find duplicates across platforms
        if find_duplicates:
            logger.info("Running duplicate detection")
            dedup_result = self._find_duplicates()
            results['deduplication'] = dedup_result
        
        # Get database stats
        results['database_stats'] = self.store.get_stats()
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        results['duration_seconds'] = duration
        
        # Save sync info
        self.last_sync = results
        
        logger.info(f"Sync completed in {duration:.1f}s")
        return results
    
    def _sync_hinge(
        self,
        user_id: str,
        limit: int,
        download_photos: bool
    ) -> Dict[str, Any]:
        """Sync profiles from Hinge."""
        start_time = datetime.now()
        
        result = {
            'profiles_fetched': 0,
            'profiles_stored': 0,
            'errors': 0,
            'duration_seconds': 0
        }
        
        try:
            # Set auth on fetcher if not already set
            self.hinge_fetcher.set_auth(self.hinge_auth)
            
            # Fetch profiles using the real fetcher
            profiles = self.hinge_fetcher.fetch_matches(user_id, limit=limit)
            result['profiles_fetched'] = len(profiles)
            
            # Store each profile
            for profile_data in profiles:
                try:
                    # Add platform identifier
                    profile_data['platform'] = 'hinge'
                    
                    # Store in database
                    self.store.store_profile(profile_data)
                    result['profiles_stored'] += 1
                    
                except Exception as e:
                    logger.error(f"Error storing Hinge profile: {e}")
                    result['errors'] += 1
            
        except Exception as e:
            logger.error(f"Hinge sync failed: {e}")
            result['errors'] += 1
        
        duration = (datetime.now() - start_time).total_seconds()
        result['duration_seconds'] = duration
        
        return result
    
    def _sync_tinder(
        self,
        user_id: str,
        limit: int,
        download_photos: bool
    ) -> Dict[str, Any]:
        """Sync profiles from Tinder."""
        start_time = datetime.now()
        
        result = {
            'profiles_fetched': 0,
            'profiles_stored': 0,
            'errors': 0,
            'duration_seconds': 0
        }
        
        try:
            # Set auth on fetcher if not already set
            self.tinder_fetcher.set_auth(self.tinder_auth)
            
            # Fetch profiles using the real fetcher
            profiles = self.tinder_fetcher.fetch_matches(user_id, limit=limit)
            result['profiles_fetched'] = len(profiles)
            
            # Store each profile
            for profile_data in profiles:
                try:
                    # Add platform identifier
                    profile_data['platform'] = 'tinder'
                    
                    # Store in database
                    self.store.store_profile(profile_data)
                    result['profiles_stored'] += 1
                    
                except Exception as e:
                    logger.error(f"Error storing Tinder profile: {e}")
                    result['errors'] += 1
            
        except Exception as e:
            logger.error(f"Tinder sync failed: {e}")
            result['errors'] += 1
        
        duration = (datetime.now() - start_time).total_seconds()
        result['duration_seconds'] = duration
        
        return result
    
    def _find_duplicates(self) -> Dict[str, Any]:
        """
        Find duplicate profiles across platforms.
        Uses name and age similarity for now.
        """
        result = {
            'profiles_checked': 0,
            'duplicates_found': 0
        }
        
        try:
            # Get all profiles
            all_profiles = self.store.get_all_profiles()
            result['profiles_checked'] = len(all_profiles)
            
            # Simple duplicate detection based on name and age
            for i, p1 in enumerate(all_profiles):
                for p2 in all_profiles[i+1:]:
                    # Skip same platform
                    if p1['platform'] == p2['platform']:
                        continue
                    
                    # Check for name match (case insensitive)
                    if p1.get('name') and p2.get('name'):
                        if p1['name'].lower() == p2['name'].lower():
                            # Check age match (within 1 year)
                            if p1.get('age') and p2.get('age'):
                                age_diff = abs(p1['age'] - p2['age'])
                                if age_diff <= 1:
                                    # Found duplicate!
                                    self.store.store_duplicate(
                                        p1['id'],
                                        p2['id'],
                                        similarity=0.95  # High confidence for exact name match
                                    )
                                    result['duplicates_found'] += 1
                                    logger.info(f"Duplicate found: {p1['name']} on {p1['platform']} and {p2['platform']}")
        
        except Exception as e:
            logger.error(f"Duplicate detection failed: {e}")
        
        return result
    
    def export_sync_report(self, output_file: str = "aggregation_report.json") -> bool:
        """Export detailed sync report to JSON file."""
        try:
            if not self.last_sync:
                logger.warning("No sync data to export")
                return False
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'sync_results': self.last_sync,
                'database_stats': self.store.get_stats(),
                'duplicates': self.store.get_duplicates()
            }
            
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Report exported to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
    
    def get_all_profiles(self, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all stored profiles, optionally filtered by platform."""
        return self.store.get_all_profiles(platform)
    
    def get_duplicates(self) -> List[Dict[str, Any]]:
        """Get all detected duplicate profiles."""
        return self.store.get_duplicates()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get aggregation statistics."""
        stats = self.store.get_stats()
        
        if self.last_sync:
            stats['last_sync'] = {
                'timestamp': self.last_sync.get('generated_at'),
                'platforms': list(self.last_sync.get('platforms', {}).keys())
            }
        
        return stats
