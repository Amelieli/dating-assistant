"""
Profile fetchers for dating apps.
Wraps the real fetcher implementations with a simpler interface.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from hinge_profile_fetcher_real import HingeProfileFetcherReal
from tinder_profile_fetcher_real import TinderProfileFetcherReal
from dating_agent.rate_limiter import get_rate_limiter, RateLimitConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HingeProfileFetcher:
    """Simplified Hinge profile fetcher with rate limiting."""
    
    def __init__(self):
        # Don't initialize the real fetcher until we have auth
        self._real_fetcher = None
        self._auth_handler = None
        
        # Configure conservative rate limiting for Hinge
        config = RateLimitConfig(
            requests_per_minute=6,  # Conservative: 6 requests/min
            min_delay=3.0,          # At least 3 seconds between requests
            max_delay=7.0,          # Up to 7 seconds
            error_threshold=2       # Cooldown after 2 errors
        )
        self.rate_limiter = get_rate_limiter('hinge', config)
    
    def set_auth(self, auth_handler):
        """Set authentication handler."""
        self._auth_handler = auth_handler
        self._real_fetcher = HingeProfileFetcherReal(auth_handler)
    
    def fetch_matches(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch matches from Hinge with rate limiting.
        
        Returns a list of profile dictionaries.
        """
        if not self._real_fetcher:
            # Return empty if not authenticated
            logger.warning("Hinge: Not authenticated, skipping fetch")
            return []
        
        # Check if platform is healthy
        if not self.rate_limiter.is_healthy('hinge'):
            logger.error("Hinge: Rate limiter unhealthy, aborting fetch")
            return []
        
        try:
            # Wait for rate limit
            self.rate_limiter.wait_if_needed('hinge')
            
            # Fetch matches
            result = self._real_fetcher.fetch_matches(limit=limit)
            
            if result['status'] == 'success':
                # Record success
                self.rate_limiter.record_success('hinge')
                
                # Return the matches as a list
                matches = result.get('matches', [])
                
                # Convert to our standard format
                profiles = []
                for match in matches:
                    profile = self._normalize_profile(match)
                    profiles.append(profile)
                
                logger.info(f"Hinge: Fetched {len(profiles)} profiles")
                return profiles
            else:
                # Record error based on type
                error_msg = result.get('message', '')
                if 'rate limit' in error_msg.lower() or '429' in error_msg:
                    self.rate_limiter.record_error('hinge', 'rate_limit')
                elif '401' in error_msg or '403' in error_msg:
                    self.rate_limiter.record_error('hinge', 'ban')
                else:
                    self.rate_limiter.record_error('hinge', 'general')
                
                logger.error(f"Hinge: Fetch failed - {error_msg}")
                return []
        
        except Exception as e:
            logger.error(f"Hinge: Exception during fetch - {e}")
            self.rate_limiter.record_error('hinge', 'general')
            return []
    
    def _normalize_profile(self, raw_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Hinge API format to our standard format."""
        return {
            'platform_id': raw_profile.get('id', raw_profile.get('_id', '')),
            'name': raw_profile.get('name', ''),
            'age': raw_profile.get('age'),
            'bio': raw_profile.get('bio', raw_profile.get('about', '')),
            'photos': [p.get('url', '') for p in raw_profile.get('photos', [])],
            'interests': raw_profile.get('interests', []),
            'location': raw_profile.get('location', ''),
            'distance_km': raw_profile.get('distance_km'),
            'job': raw_profile.get('job', raw_profile.get('work', '')),
            'education': raw_profile.get('education', raw_profile.get('school', '')),
            'height_cm': raw_profile.get('height_cm'),
            'religion': raw_profile.get('religion'),
            'politics': raw_profile.get('politics'),
            'smoking': raw_profile.get('smoking'),
            'drugs': raw_profile.get('drugs'),
            'match_status': 'matched',
        }


class TinderProfileFetcher:
    """Simplified Tinder profile fetcher with rate limiting."""
    
    def __init__(self):
        # Don't initialize the real fetcher until we have auth
        self._real_fetcher = None
        self._auth_handler = None
        
        # Configure VERY conservative rate limiting for Tinder (stricter than Hinge)
        config = RateLimitConfig(
            requests_per_minute=4,  # Very conservative: 4 requests/min
            min_delay=5.0,          # At least 5 seconds between requests
            max_delay=10.0,         # Up to 10 seconds
            error_threshold=2       # Cooldown after just 2 errors
        )
        self.rate_limiter = get_rate_limiter('tinder', config)
    
    def set_auth(self, auth_handler):
        """Set authentication handler."""
        self._auth_handler = auth_handler
        self._real_fetcher = TinderProfileFetcherReal(auth_handler)
    
    def fetch_matches(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch matches from Tinder with STRICT rate limiting.
        
        Tinder is more aggressive about banning, so we're extra careful.
        
        Returns a list of profile dictionaries.
        """
        if not self._real_fetcher:
            # Return empty if not authenticated
            logger.warning("Tinder: Not authenticated, skipping fetch")
            return []
        
        # Check if platform is healthy
        if not self.rate_limiter.is_healthy('tinder'):
            logger.error("Tinder: Rate limiter unhealthy, aborting fetch")
            return []
        
        try:
            # Wait for rate limit (Tinder is stricter!)
            self.rate_limiter.wait_if_needed('tinder')
            
            # Fetch matches
            result = self._real_fetcher.fetch_matches(limit=limit)
            
            if result['status'] == 'success':
                # Record success
                self.rate_limiter.record_success('tinder')
                
                # Return the matches as a list
                matches = result.get('matches', [])
                
                # Convert to our standard format
                profiles = []
                for match in matches:
                    profile = self._normalize_profile(match)
                    profiles.append(profile)
                
                logger.info(f"Tinder: Fetched {len(profiles)} profiles")
                return profiles
            else:
                # Record error based on type
                error_msg = result.get('message', '')
                if 'rate limit' in error_msg.lower() or '429' in error_msg:
                    self.rate_limiter.record_error('tinder', 'rate_limit')
                    logger.error("Tinder: RATE LIMITED! Backing off aggressively...")
                elif '401' in error_msg or '403' in error_msg:
                    self.rate_limiter.record_error('tinder', 'ban')
                    logger.error("Tinder: BANNED or AUTH ERROR! Entering cooldown...")
                else:
                    self.rate_limiter.record_error('tinder', 'general')
                
                logger.error(f"Tinder: Fetch failed - {error_msg}")
                return []
        
        except Exception as e:
            logger.error(f"Tinder: Exception during fetch - {e}")
            self.rate_limiter.record_error('tinder', 'general')
            return []
    
    def _normalize_profile(self, raw_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Tinder API format to our standard format."""
        # Tinder uses 'distance_mi', convert to km
        distance_mi = raw_profile.get('distance_mi', 0)
        distance_km = distance_mi * 1.60934 if distance_mi else None
        
        return {
            'platform_id': raw_profile.get('_id', raw_profile.get('id', '')),
            'name': raw_profile.get('name', ''),
            'age': raw_profile.get('age'),
            'bio': raw_profile.get('bio', ''),
            'photos': [p.get('url', '') for p in raw_profile.get('photos', [])],
            'interests': raw_profile.get('interests', []),
            'location': raw_profile.get('city', ''),
            'distance_km': distance_km,
            'job': raw_profile.get('company', ''),
            'education': raw_profile.get('schools', [''])[0] if raw_profile.get('schools') else '',
            'height_cm': None,  # Tinder doesn't expose height
            'religion': None,
            'politics': None,
            'smoking': None,
            'drugs': None,
            'match_status': 'matched',
        }
