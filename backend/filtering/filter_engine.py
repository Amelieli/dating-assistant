"""
Strict filtering engine for profiles.
Enforces user-defined constraints and calculates match scores.
"""
from typing import List, Optional, Callable
from dataclasses import dataclass
from models.profile import Profile
import math


@dataclass
class FilterConfig:
    """User's filtering preferences."""
    
    # Age range
    min_age: int = 18
    max_age: int = 100
    
    # Distance
    max_distance_km: int = 50
    
    # Location-specific (if you want to match only certain areas)
    preferred_cities: Optional[List[str]] = None
    preferred_states: Optional[List[str]] = None
    
    # Interests matching
    min_interest_overlap: int = 1  # At least 1 shared interest
    required_interests: Optional[List[str]] = None  # MUST have these
    blocked_interests: Optional[List[str]] = None  # Never match
    
    # Lifestyle filters (strict)
    must_not_smoke: bool = True
    must_not_use_drugs: bool = True
    min_drink_level: Optional[str] = None  # "no", "socially", "often"
    
    # Religion/Politics
    acceptable_religions: Optional[List[str]] = None
    acceptable_politics: Optional[List[str]] = None
    
    # Other
    must_be_verified: bool = False
    min_distance_km: int = 0


class FilterEngine:
    """Applies strict filters and calculates match compatibility scores."""
    
    def __init__(self, config: FilterConfig):
        self.config = config
    
    def apply_filters(self, profiles: List[Profile]) -> List[Profile]:
        """
        Filter profiles based on strict criteria.
        Returns only profiles that pass ALL filters.
        """
        valid_profiles = []
        
        for profile in profiles:
            if self._passes_all_filters(profile):
                valid_profiles.append(profile)
        
        return valid_profiles
    
    def _passes_all_filters(self, profile: Profile) -> bool:
        """Check if profile passes all strict filters."""
        checks = [
            self._check_age,
            self._check_distance,
            self._check_location,
            self._check_interests,
            self._check_lifestyle,
            self._check_religion,
            self._check_politics,
            self._check_verification,
        ]
        
        return all(check(profile) for check in checks)
    
    def _check_age(self, profile: Profile) -> bool:
        """Age must be within min/max range."""
        return self.config.min_age <= profile.age <= self.config.max_age
    
    def _check_distance(self, profile: Profile) -> bool:
        """Distance must be within max_distance."""
        if profile.distance_km is None:
            return True  # Can't verify, allow it
        
        return (self.config.min_distance_km <= profile.distance_km <= 
                self.config.max_distance_km)
    
    def _check_location(self, profile: Profile) -> bool:
        """If preferred locations set, profile must be in one of them."""
        if not self.config.preferred_cities and not self.config.preferred_states:
            return True  # No preference set
        
        if self.config.preferred_cities:
            if profile.city.lower() in [c.lower() for c in self.config.preferred_cities]:
                return True
        
        if self.config.preferred_states:
            if profile.state.lower() in [s.lower() for s in self.config.preferred_states]:
                return True
        
        return False if (self.config.preferred_cities or self.config.preferred_states) else True
    
    def _check_interests(self, profile: Profile) -> bool:
        """Check interest matching rules."""
        if not profile.interests:
            return self.config.min_interest_overlap == 0
        
        # Check blocked interests (hard stop)
        if self.config.blocked_interests:
            blocked = set(i.lower() for i in self.config.blocked_interests)
            profile_interests = set(i.lower() for i in profile.interests)
            if profile_interests & blocked:
                return False  # Has a blocked interest
        
        # Check required interests (must have all)
        if self.config.required_interests:
            required = set(i.lower() for i in self.config.required_interests)
            profile_interests = set(i.lower() for i in profile.interests)
            if not required.issubset(profile_interests):
                return False
        
        # Check minimum overlap
        if self.config.min_interest_overlap > 0:
            return len(profile.interests) >= self.config.min_interest_overlap
        
        return True
    
    def _check_lifestyle(self, profile: Profile) -> bool:
        """Enforce strict lifestyle filters."""
        if self.config.must_not_smoke and profile.smokes == "yes":
            return False
        
        if self.config.must_not_use_drugs and profile.drugs == "yes":
            return False
        
        if self.config.min_drink_level:
            drink_levels = {"no": 0, "socially": 1, "often": 2}
            min_level = drink_levels.get(self.config.min_drink_level, 0)
            profile_level = drink_levels.get(profile.drinks, -1)
            if profile_level < min_level:
                return False
        
        return True
    
    def _check_religion(self, profile: Profile) -> bool:
        """Check religion preference."""
        if not self.config.acceptable_religions:
            return True
        
        if profile.religion is None:
            return True  # Unknown is acceptable
        
        return profile.religion.lower() in [r.lower() for r in self.config.acceptable_religions]
    
    def _check_politics(self, profile: Profile) -> bool:
        """Check politics preference."""
        if not self.config.acceptable_politics:
            return True
        
        if profile.politics is None:
            return True  # Unknown is acceptable
        
        return profile.politics.lower() in [p.lower() for p in self.config.acceptable_politics]
    
    def _check_verification(self, profile: Profile) -> bool:
        """Check verification requirement."""
        if self.config.must_be_verified:
            return profile.verified
        return True
    
    def calculate_match_score(self, profile: Profile, your_interests: List[str]) -> float:
        """
        Calculate a compatibility score (0-100) based on interests and lifestyle.
        Higher = better match.
        
        ONLY call after profile has passed filters.
        """
        score = 50.0  # Base score
        
        # Interest overlap
        your_interests_lower = set(i.lower() for i in your_interests)
        profile_interests_lower = set(i.lower() for i in profile.interests)
        overlap = len(your_interests_lower & profile_interests_lower)
        interest_score = min(50, overlap * 10)  # Max 50 points
        
        # Distance bonus (closer = better)
        distance_bonus = 0
        if profile.distance_km is not None:
            if profile.distance_km < 5:
                distance_bonus = 10
            elif profile.distance_km < 15:
                distance_bonus = 5
        
        total = score + interest_score + distance_bonus
        return min(100.0, total)


def create_strict_filter(
    min_age: int = 18,
    max_age: int = 100,
    max_distance_km: int = 50,
    must_not_smoke: bool = True,
    required_interests: Optional[List[str]] = None,
    **kwargs
) -> FilterEngine:
    """Factory function for quick filter creation."""
    config = FilterConfig(
        min_age=min_age,
        max_age=max_age,
        max_distance_km=max_distance_km,
        must_not_smoke=must_not_smoke,
        required_interests=required_interests,
        **kwargs
    )
    return FilterEngine(config)
