"""
Profile Ranking Algorithm for Dating Agent

Scores profiles based on compatibility, profile quality, and user preferences.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class RankingConfig:
    """User preferences for ranking."""
    # Age preferences
    min_age: int = 25
    max_age: int = 45
    ideal_age: Optional[int] = None  # If set, profiles closer to this age score higher
    
    # Distance preferences
    max_distance_km: int = 50
    distance_penalty_per_km: float = 0.5
    
    # Lifestyle deal-breakers
    must_not_smoke: bool = True
    must_not_use_drugs: bool = True
    prefer_moderate_drinker: bool = False
    
    # Must-haves
    must_be_verified: bool = False
    must_have_bio: bool = False
    must_have_photos: bool = True
    
    # Bonus weights (adjust these to tune ranking)
    mutual_match_bonus: int = 25
    verified_bonus: int = 15
    has_bio_bonus: int = 8
    has_occupation_bonus: int = 5
    has_education_bonus: int = 5
    has_height_bonus: int = 3
    photo_bonus_per_photo: int = 2
    max_photo_bonus: int = 12
    age_in_range_bonus: int = 10
    no_smoking_bonus: int = 10
    ethnicity_match_bonus: int = 10
    
    # Preferred ethnicities (empty = no preference)
    preferred_ethnicities: List[str] = None


def calculate_profile_score(profile: Dict[str, Any], config: RankingConfig) -> Dict[str, Any]:
    """
    Calculate a ranking score for a profile.
    
    Returns dict with:
        - total_score: overall ranking score
        - breakdown: dict explaining each component
        - flags: list of any red flags
        - bonuses: list of positive attributes
    """
    score = 50  # Base score
    breakdown = {"base": 50}
    flags = []
    bonuses = []
    
    # --- MATCH STATUS ---
    if profile.get("match_status") == "mutual":
        score += config.mutual_match_bonus
        breakdown["mutual_match"] = config.mutual_match_bonus
        bonuses.append("Mutual match!")
    
    # --- VERIFICATION ---
    if profile.get("verified"):
        score += config.verified_bonus
        breakdown["verified"] = config.verified_bonus
        bonuses.append("Verified profile")
    elif config.must_be_verified:
        score -= 50  # Major penalty if verification required
        breakdown["not_verified_penalty"] = -50
        flags.append("Not verified")
    
    # --- DISTANCE ---
    distance = profile.get("distance_km")
    if distance is not None:
        if distance <= config.max_distance_km:
            # Closer is better
            distance_penalty = distance * config.distance_penalty_per_km
            score -= distance_penalty
            breakdown["distance"] = -round(distance_penalty, 1)
        else:
            # Beyond max distance - big penalty
            score -= 30
            breakdown["distance"] = -30
            flags.append(f"Too far ({distance:.0f} km)")
    
    # --- AGE ---
    age = profile.get("age")
    if age:
        if config.min_age <= age <= config.max_age:
            score += config.age_in_range_bonus
            breakdown["age_in_range"] = config.age_in_range_bonus
            bonuses.append(f"Age {age} in range")
            
            # Bonus for being close to ideal age
            if config.ideal_age:
                age_diff = abs(age - config.ideal_age)
                ideal_bonus = max(0, 5 - age_diff)
                score += ideal_bonus
                breakdown["ideal_age_bonus"] = ideal_bonus
        else:
            # Outside age range
            age_penalty = min(20, abs(age - (config.min_age + config.max_age) / 2))
            score -= age_penalty
            breakdown["age_outside_range"] = -age_penalty
            flags.append(f"Age {age} outside range")
    
    # --- LIFESTYLE: SMOKING ---
    lifestyle = profile.get("lifestyle", {})
    smokes = lifestyle.get("smokes") or profile.get("smokes")
    
    if smokes:
        smokes_lower = smokes.lower() if isinstance(smokes, str) else ""
        if "no" in smokes_lower or "never" in smokes_lower:
            score += config.no_smoking_bonus
            breakdown["no_smoking"] = config.no_smoking_bonus
            bonuses.append("Non-smoker")
        elif config.must_not_smoke and ("yes" in smokes_lower or "social" in smokes_lower or "often" in smokes_lower):
            score -= 25
            breakdown["smoker_penalty"] = -25
            flags.append("Smokes")
    
    # --- LIFESTYLE: DRINKING ---
    drinks = lifestyle.get("drinks") or profile.get("drinks")
    if drinks and config.prefer_moderate_drinker:
        drinks_lower = drinks.lower() if isinstance(drinks, str) else ""
        if "no" in drinks_lower or "rarely" in drinks_lower or "social" in drinks_lower:
            score += 5
            breakdown["moderate_drinker"] = 5
    
    # --- LIFESTYLE: DRUGS ---
    drugs = lifestyle.get("drugs") or profile.get("drugs")
    if drugs and config.must_not_use_drugs:
        drugs_lower = drugs.lower() if isinstance(drugs, str) else ""
        if "yes" in drugs_lower or "often" in drugs_lower or "sometimes" in drugs_lower:
            score -= 20
            breakdown["drugs_penalty"] = -20
            flags.append("Uses drugs")
    
    # --- PROFILE COMPLETENESS ---
    # Bio
    bio = profile.get("bio", "")
    if bio and len(bio) > 20:
        score += config.has_bio_bonus
        breakdown["has_bio"] = config.has_bio_bonus
        bonuses.append("Has bio")
    elif config.must_have_bio:
        score -= 15
        breakdown["no_bio_penalty"] = -15
        flags.append("No bio")
    
    # Occupation
    occupation = profile.get("occupation", "")
    if occupation and occupation.lower() not in ["unknown", ""]:
        score += config.has_occupation_bonus
        breakdown["has_occupation"] = config.has_occupation_bonus
        bonuses.append("Has job listed")
    
    # Education
    education = profile.get("education", "")
    if education and education.lower() not in ["unknown", ""]:
        score += config.has_education_bonus
        breakdown["has_education"] = config.has_education_bonus
        bonuses.append("Has education")
    
    # Height
    height = profile.get("height_cm")
    if height:
        score += config.has_height_bonus
        breakdown["has_height"] = config.has_height_bonus
    
    # Photos
    photos = profile.get("photo_urls", [])
    if photos:
        photo_bonus = min(len(photos) * config.photo_bonus_per_photo, config.max_photo_bonus)
        score += photo_bonus
        breakdown["photos"] = photo_bonus
        if len(photos) >= 4:
            bonuses.append(f"{len(photos)} photos")
    elif config.must_have_photos:
        score -= 20
        breakdown["no_photos_penalty"] = -20
        flags.append("No photos")
    
    # --- ETHNICITY PREFERENCE ---
    if config.preferred_ethnicities:
        ethnicity = profile.get("ethnicity", "")
        if ethnicity:
            ethnicity_lower = ethnicity.lower()
            for pref in config.preferred_ethnicities:
                if pref.lower() in ethnicity_lower:
                    score += config.ethnicity_match_bonus
                    breakdown["ethnicity_match"] = config.ethnicity_match_bonus
                    bonuses.append(f"Ethnicity: {ethnicity}")
                    break
    
    # Ensure score doesn't go below 0
    score = max(0, score)
    
    return {
        "total_score": round(score, 1),
        "breakdown": breakdown,
        "flags": flags,
        "bonuses": bonuses,
    }


def rank_profiles(profiles: List[Dict], config: RankingConfig = None) -> List[Dict]:
    """
    Rank a list of profiles and return them sorted by score.
    
    Each profile in the result will have added fields:
        - _rank: position (1 = best)
        - _score: total score
        - _breakdown: score breakdown
        - _flags: red flags
        - _bonuses: positive attributes
    """
    if config is None:
        config = RankingConfig()
    
    # Calculate scores for all profiles
    scored_profiles = []
    for profile in profiles:
        score_result = calculate_profile_score(profile, config)
        profile_with_score = {
            **profile,
            "_score": score_result["total_score"],
            "_breakdown": score_result["breakdown"],
            "_flags": score_result["flags"],
            "_bonuses": score_result["bonuses"],
        }
        scored_profiles.append(profile_with_score)
    
    # Sort by score (highest first)
    scored_profiles.sort(key=lambda p: p["_score"], reverse=True)
    
    # Add rank
    for i, profile in enumerate(scored_profiles):
        profile["_rank"] = i + 1
    
    return scored_profiles


def get_top_matches(profiles: List[Dict], n: int = 20, config: RankingConfig = None) -> List[Dict]:
    """Get the top N ranked profiles."""
    ranked = rank_profiles(profiles, config)
    return ranked[:n]
