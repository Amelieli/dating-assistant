"""
Main orchestrator agent that unifies data from all 3 dating apps.
Handles profile aggregation, deduplication, filtering, and matching.
"""
from typing import List, Dict, Optional, Tuple
from models.profile import Profile, MatchStatus, AppSource
from filtering.filter_engine import FilterEngine, FilterConfig
from filtering.clip_matcher import CLIPMatcher
from scrapers.base_scraper import TinderScraper, HingeScraper, MatchScraper
import logging
from dataclasses import asdict

logger = logging.getLogger(__name__)


class DatingAppOrchestrator:
    """
    Orchestrates data from Tinder, Hinge, and Match.
    
    Main responsibilities:
    1. Aggregate profiles from all 3 apps
    2. Detect mutual matches (both parties liked each other)
    3. Apply strict filtering rules
    4. Compute CLIP-based image similarity
    5. Return unified results
    """
    
    def __init__(self, filter_config: FilterConfig, use_clip: bool = True):
        self.filter_config = filter_config
        self.filter_engine = FilterEngine(filter_config)
        self.clip_matcher = CLIPMatcher() if use_clip else None
        
        # Initialize scrapers
        self.scrapers = {
            AppSource.TINDER: TinderScraper(),
            AppSource.HINGE: HingeScraper(),
            AppSource.MATCH: MatchScraper(),
        }
        
        # Storage
        self.all_profiles: Dict[Tuple[str, AppSource], Profile] = {}
        self.your_likes: Dict[Tuple[str, AppSource], Profile] = {}
        self.incoming_likes: Dict[Tuple[str, AppSource], Profile] = {}
    
    def authenticate_all_apps(self, credentials: Dict[str, Dict[str, str]]) -> Dict[AppSource, bool]:
        """
        Authenticate with all dating apps.
        
        Args:
            credentials: Dict like {
                "tinder": {"facebook_token": "..."},
                "hinge": {"session_token": "..."},
                "match": {"username": "...", "password": "..."}
            }
        
        Returns:
            Dict showing which apps authenticated successfully
        """
        results = {}
        
        for app_source, scraper in self.scrapers.items():
            app_name = app_source.value
            if app_name in credentials:
                success = scraper.authenticate(credentials[app_name])
                results[app_source] = success
                logger.info(f"{app_name}: {'authenticated' if success else 'auth failed'}")
            else:
                logger.warning(f"No credentials for {app_name}")
                results[app_source] = False
        
        return results
    
    def sync_all_apps(self) -> Dict[str, int]:
        """
        Fetch data from all 3 dating apps.
        Handles both mutual matches and incoming/outgoing likes.
        
        Returns:
            Stats about what was fetched
        """
        stats = {
            "total_mutual_matches": 0,
            "total_incoming_likes": 0,
            "total_profiles": 0,
        }
        
        for app_source, scraper in self.scrapers.items():
            try:
                # Get your likes
                your_likes = scraper.get_likes_sent()
                self._add_profiles(your_likes, MatchStatus.OUTGOING)
                
                # Get incoming likes
                incoming = scraper.get_likes_received()
                self._add_profiles(incoming, MatchStatus.INCOMING)
                self.incoming_likes.update({
                    (p.app_id, p.app_source): p for p in incoming
                })
                
                # Get mutual matches (only both-ways likes)
                mutual = scraper.get_matches()
                self._add_profiles(mutual, MatchStatus.MUTUAL)
                
                logger.info(
                    f"{app_source.value}: "
                    f"{len(mutual)} mutual, "
                    f"{len(incoming)} incoming, "
                    f"{len(your_likes)} outgoing"
                )
                
            except Exception as e:
                logger.error(f"Error syncing {app_source.value}: {e}")
        
        stats["total_profiles"] = len(self.all_profiles)
        stats["total_incoming_likes"] = len(self.incoming_likes)
        
        return stats
    
    def _add_profiles(self, profiles: List[Profile], status: MatchStatus):
        """Add profiles to storage, updating status if they already exist."""
        for profile in profiles:
            key = (profile.app_id, profile.app_source)
            
            if key in self.all_profiles:
                # Update status (prefer MUTUAL over others)
                existing = self.all_profiles[key]
                if status == MatchStatus.MUTUAL:
                    existing.match_status = MatchStatus.MUTUAL
            else:
                profile.match_status = status
                self.all_profiles[key] = profile
    
    def get_mutual_matches(self) -> List[Profile]:
        """Get profiles where both parties liked each other."""
        mutual = [p for p in self.all_profiles.values() 
                  if p.match_status == MatchStatus.MUTUAL]
        logger.info(f"Found {len(mutual)} mutual matches")
        return mutual
    
    def get_incoming_likes(self) -> List[Profile]:
        """Get profiles who sent you a like."""
        incoming = list(self.incoming_likes.values())
        logger.info(f"Found {len(incoming)} incoming likes")
        return incoming
    
    def filter_and_rank(
        self,
        your_interests: List[str],
        embed_photos: bool = False
    ) -> Dict[str, List[Profile]]:
        """
        Apply strict filters and compute match scores.
        
        Args:
            your_interests: Your interests for matching
            embed_photos: Whether to compute CLIP embeddings (slower)
        
        Returns:
            Dict with filtered results:
            {
                "mutual_matches": [...],  # Both-way likes, filtered & ranked
                "incoming_likes": [...],   # Incoming likes, filtered & ranked
                "potential_matches": [...] # All profiles passing filters, ranked
            }
        """
        results = {}
        
        # 1. Apply strict filters
        all_filtered = self.filter_engine.apply_filters(
            list(self.all_profiles.values())
        )
        logger.info(f"Strict filters passed: {len(all_filtered)}/{len(self.all_profiles)}")
        
        # 2. Optionally embed photos with CLIP
        if embed_photos and self.clip_matcher:
            logger.info("Embedding photos with CLIP...")
            all_filtered = self.clip_matcher.batch_embed_profiles(all_filtered)
        
        # 3. Calculate match scores for all
        for profile in all_filtered:
            profile.match_percentage = self.filter_engine.calculate_match_score(
                profile, your_interests
            )
        
        # 4. Separate and sort by match score
        mutual = [p for p in all_filtered if p.match_status == MatchStatus.MUTUAL]
        incoming = [p for p in all_filtered if p.match_status == MatchStatus.INCOMING]
        
        mutual.sort(key=lambda p: p.match_percentage or 0, reverse=True)
        incoming.sort(key=lambda p: p.match_percentage or 0, reverse=True)
        all_filtered.sort(key=lambda p: p.match_percentage or 0, reverse=True)
        
        results["mutual_matches"] = mutual
        results["incoming_likes"] = incoming
        results["potential_matches"] = all_filtered
        
        logger.info(
            f"After filtering: "
            f"{len(mutual)} mutual, "
            f"{len(incoming)} incoming"
        )
        
        return results
    
    def find_similar_by_description(
        self,
        description: str,
        candidates: Optional[List[Profile]] = None,
        top_k: int = 10
    ) -> List[Tuple[Profile, float]]:
        """
        Find profiles matching a text description using CLIP.
        Example: "athletic blonde woman who loves hiking"
        
        Args:
            description: Text description
            candidates: Profiles to search (default: all)
            top_k: Return top K matches
        
        Returns:
            List of (Profile, similarity_score) tuples
        """
        if not self.clip_matcher:
            raise ValueError("CLIP matching is disabled")
        
        if candidates is None:
            candidates = list(self.all_profiles.values())
        
        # Ensure photos are embedded
        candidates_with_photos = [p for p in candidates if p.photo_embeddings]
        if not candidates_with_photos:
            logger.warning("No profiles with embedded photos")
            return []
        
        return self.clip_matcher.find_by_text_description(
            description, candidates_with_photos, top_k
        )
    
    def deduplicate_across_apps(self) -> int:
        """
        Try to detect the same person across multiple apps.
        Currently a stub - real implementation would use name+photos+age matching.
        
        Returns:
            Number of duplicates found
        """
        # TODO: Implement cross-app deduplication
        # Could use fuzzy name matching + photo similarity
        return 0
    
    def refresh_new_data(self) -> Dict[str, int]:
        """
        Refresh data from all apps and return what changed.
        Useful for checking for new likes without re-filtering everything.
        """
        old_incoming = set(self.incoming_likes.keys())
        
        # Sync fresh data
        self.sync_all_apps()
        
        new_incoming = set(self.incoming_likes.keys())
        new_likes = new_incoming - old_incoming
        
        return {
            "new_likes": len(new_likes),
            "lost_matches": len(old_incoming - new_incoming),
        }
    
    def export_profile_data(self, profile: Profile) -> dict:
        """Export profile as JSON-serializable dict."""
        return profile.to_dict()
    
    def export_all_mutual_matches(self) -> List[dict]:
        """Export all mutual matches as JSON."""
        mutual = self.get_mutual_matches()
        return [self.export_profile_data(p) for p in mutual]
