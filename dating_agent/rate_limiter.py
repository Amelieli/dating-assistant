"""
Rate limiter to prevent getting banned from dating apps.

Implements:
- Per-platform rate limits
- Exponential backoff on errors
- Request throttling
- Ban detection
"""

import time
import random
from typing import Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    
    # Requests per minute
    requests_per_minute: int = 10
    
    # Minimum delay between requests (seconds)
    min_delay: float = 2.0
    
    # Maximum delay between requests (seconds)
    max_delay: float = 5.0
    
    # Exponential backoff multiplier on errors
    backoff_multiplier: float = 2.0
    
    # Maximum backoff delay (seconds)
    max_backoff: float = 300.0  # 5 minutes
    
    # Cool down period after detection (seconds)
    cooldown_period: float = 3600.0  # 1 hour
    
    # Number of consecutive errors before cooldown
    error_threshold: int = 3


@dataclass
class PlatformState:
    """Tracks state for a single platform."""
    
    # Recent request timestamps
    request_times: list = field(default_factory=list)
    
    # Current backoff delay
    current_backoff: float = 0.0
    
    # Consecutive errors
    consecutive_errors: int = 0
    
    # Last error time
    last_error_time: Optional[datetime] = None
    
    # Banned until (if detected)
    banned_until: Optional[datetime] = None
    
    # Total requests made
    total_requests: int = 0
    
    # Total errors
    total_errors: int = 0


class RateLimiter:
    """
    Intelligent rate limiter for dating app APIs.
    
    Features:
    - Per-platform rate tracking
    - Random delays (appear more human)
    - Exponential backoff on errors
    - Ban detection and cooldown
    - Request statistics
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self.platforms: Dict[str, PlatformState] = {}
    
    def _get_platform_state(self, platform: str) -> PlatformState:
        """Get or create platform state."""
        if platform not in self.platforms:
            self.platforms[platform] = PlatformState()
        return self.platforms[platform]
    
    def wait_if_needed(self, platform: str):
        """
        Wait if rate limit would be exceeded.
        
        Args:
            platform: Platform name ('hinge', 'tinder', etc.)
        """
        state = self._get_platform_state(platform)
        now = datetime.now()
        
        # Check if banned/cooling down
        if state.banned_until and now < state.banned_until:
            wait_seconds = (state.banned_until - now).total_seconds()
            logger.warning(
                f"{platform}: In cooldown period. "
                f"Waiting {wait_seconds:.0f} seconds..."
            )
            time.sleep(wait_seconds)
            state.banned_until = None
            state.consecutive_errors = 0
        
        # Clean old request times (older than 1 minute)
        cutoff = now - timedelta(minutes=1)
        state.request_times = [
            t for t in state.request_times 
            if t > cutoff
        ]
        
        # Check rate limit
        if len(state.request_times) >= self.config.requests_per_minute:
            # Too many requests, wait until oldest expires
            oldest = min(state.request_times)
            wait_until = oldest + timedelta(minutes=1)
            wait_seconds = (wait_until - now).total_seconds()
            
            if wait_seconds > 0:
                logger.info(
                    f"{platform}: Rate limit reached. "
                    f"Waiting {wait_seconds:.1f}s..."
                )
                time.sleep(wait_seconds)
        
        # Add random delay to appear human
        base_delay = random.uniform(
            self.config.min_delay,
            self.config.max_delay
        )
        
        # Add backoff delay if in backoff state
        total_delay = base_delay + state.current_backoff
        
        if total_delay > self.config.min_delay:
            logger.debug(
                f"{platform}: Delaying {total_delay:.2f}s "
                f"(base: {base_delay:.2f}s, backoff: {state.current_backoff:.2f}s)"
            )
        
        time.sleep(total_delay)
        
        # Record this request
        state.request_times.append(now)
        state.total_requests += 1
    
    def record_success(self, platform: str):
        """
        Record successful request.
        
        Resets error counters and backoff.
        """
        state = self._get_platform_state(platform)
        
        # Reset error state on success
        if state.consecutive_errors > 0:
            logger.info(f"{platform}: Request successful, resetting error state")
        
        state.consecutive_errors = 0
        state.current_backoff = 0.0
    
    def record_error(self, platform: str, error_type: str = 'general'):
        """
        Record failed request.
        
        Args:
            platform: Platform name
            error_type: Type of error ('rate_limit', 'auth_error', 'general', 'ban')
        """
        state = self._get_platform_state(platform)
        now = datetime.now()
        
        state.consecutive_errors += 1
        state.total_errors += 1
        state.last_error_time = now
        
        # Calculate backoff
        if error_type == 'rate_limit':
            # Aggressive backoff for rate limits
            state.current_backoff = min(
                state.current_backoff * 3.0 + 60.0,  # At least 1 minute
                self.config.max_backoff
            )
            logger.warning(
                f"{platform}: Rate limited! "
                f"Backing off {state.current_backoff:.0f}s"
            )
        
        elif error_type == 'ban':
            # Detected ban - trigger cooldown
            state.banned_until = now + timedelta(
                seconds=self.config.cooldown_period
            )
            logger.error(
                f"{platform}: BAN DETECTED! "
                f"Entering cooldown until {state.banned_until.strftime('%H:%M:%S')}"
            )
        
        else:
            # Regular error - exponential backoff
            if state.current_backoff == 0:
                state.current_backoff = self.config.min_delay
            else:
                state.current_backoff = min(
                    state.current_backoff * self.config.backoff_multiplier,
                    self.config.max_backoff
                )
            
            logger.warning(
                f"{platform}: Error #{state.consecutive_errors}. "
                f"Backoff: {state.current_backoff:.1f}s"
            )
        
        # Trigger cooldown if too many errors
        if state.consecutive_errors >= self.config.error_threshold:
            state.banned_until = now + timedelta(
                seconds=self.config.cooldown_period
            )
            logger.error(
                f"{platform}: Too many errors ({state.consecutive_errors}). "
                f"Forcing cooldown until {state.banned_until.strftime('%H:%M:%S')}"
            )
    
    def get_stats(self, platform: str) -> Dict:
        """Get statistics for a platform."""
        state = self._get_platform_state(platform)
        now = datetime.now()
        
        # Calculate requests in last minute
        cutoff = now - timedelta(minutes=1)
        recent_requests = len([
            t for t in state.request_times 
            if t > cutoff
        ])
        
        return {
            'total_requests': state.total_requests,
            'total_errors': state.total_errors,
            'consecutive_errors': state.consecutive_errors,
            'requests_last_minute': recent_requests,
            'current_backoff': state.current_backoff,
            'is_cooling_down': state.banned_until is not None and now < state.banned_until,
            'cooldown_remaining': (
                (state.banned_until - now).total_seconds()
                if state.banned_until and now < state.banned_until
                else 0.0
            ),
            'error_rate': (
                state.total_errors / state.total_requests 
                if state.total_requests > 0 
                else 0.0
            )
        }
    
    def is_healthy(self, platform: str) -> bool:
        """Check if platform is in good state."""
        stats = self.get_stats(platform)
        
        # Not healthy if cooling down
        if stats['is_cooling_down']:
            return False
        
        # Not healthy if high error rate
        if stats['error_rate'] > 0.3:  # 30% errors
            return False
        
        # Not healthy if many consecutive errors
        if stats['consecutive_errors'] >= 3:
            return False
        
        return True


# Global rate limiter instances
_rate_limiters: Dict[str, RateLimiter] = {}


def get_rate_limiter(platform: str, config: Optional[RateLimitConfig] = None) -> RateLimiter:
    """
    Get or create rate limiter for a platform.
    
    Args:
        platform: Platform name
        config: Optional custom configuration
    
    Returns:
        RateLimiter instance
    """
    if platform not in _rate_limiters:
        _rate_limiters[platform] = RateLimiter(config)
    return _rate_limiters[platform]
