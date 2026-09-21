"""
Unified profile schema across all dating apps.
Maps different app's data structures to a common format.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
from datetime import datetime


class AppSource(Enum):
    TINDER = "tinder"
    HINGE = "hinge"
    MATCH = "match"


class MatchStatus(Enum):
    MUTUAL = "mutual"  # They liked you AND you liked them
    INCOMING = "incoming"  # They liked you, status unknown on your end
    OUTGOING = "outgoing"  # You liked them, status unknown on their end
    REJECTED = "rejected"  # You rejected them


@dataclass
class Profile:
    """Unified profile across all dating apps."""
    
    # Core identity
    app_id: str  # Original ID from the app
    app_source: AppSource
    name: str
    age: int
    
    # Location
    city: str
    state: str
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_km: Optional[float] = None  # From you
    
    # Bio & Interests
    bio: str = ""
    interests: List[str] = field(default_factory=list)
    occupation: str = ""
    education: str = ""
    
    # Lifestyle
    drinks: Optional[str] = None  # "no", "socially", "often"
    smokes: Optional[str] = None
    drugs: Optional[str] = None
    religion: Optional[str] = None
    politics: Optional[str] = None
    ethnicity: Optional[str] = None
    height_cm: Optional[int] = None
    
    # Media
    photo_urls: List[str] = field(default_factory=list)
    photo_embeddings: List[Optional[List[float]]] = field(default_factory=list)  # CLIP embeddings
    
    # Matching status
    match_status: MatchStatus = MatchStatus.INCOMING
    
    # Timestamps
    last_seen: datetime = field(default_factory=datetime.now)
    profile_created_at: Optional[datetime] = None
    
    # Metadata
    verified: bool = False
    match_percentage: Optional[float] = None  # Our computed similarity
    
    def __hash__(self):
        """Hash by app_id and source for deduplication."""
        return hash((self.app_id, self.app_source.value))
    
    def __eq__(self, other):
        """Equality based on app_id and source."""
        if not isinstance(other, Profile):
            return False
        return (self.app_id == other.app_id and 
                self.app_source == other.app_source)
    
    @property
    def full_location(self) -> str:
        """Formatted location string."""
        parts = [self.city, self.state, self.country]
        return ", ".join([p for p in parts if p])
    
    @property
    def has_photos(self) -> bool:
        """Check if profile has photos."""
        return bool(self.photo_urls)
    
    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        return {
            "app_id": self.app_id,
            "app_source": self.app_source.value,
            "name": self.name,
            "age": self.age,
            "location": self.full_location,
            "distance_km": self.distance_km,
            "bio": self.bio,
            "interests": self.interests,
            "occupation": self.occupation,
            "education": self.education,
            "lifestyle": {
                "drinks": self.drinks,
                "smokes": self.smokes,
                "drugs": self.drugs,
                "religion": self.religion,
                "politics": self.politics,
            },
            "photo_urls": self.photo_urls,
            "match_status": self.match_status.value,
            "verified": self.verified,
            "match_percentage": self.match_percentage,
            "last_seen": self.last_seen.isoformat(),
            "ethnicity": self.ethnicity,
            "height_cm": self.height_cm,
        }
