"""
Real Tinder Profile Fetcher using documented reverse-engineered API

Uses endpoints from: https://gist.github.com/rtt/10403467
"""

import requests
from typing import Dict, List, Optional, Any
from tinder_auth_real import TinderAuthReal


class TinderProfileFetcherReal:
    """Real Tinder profile fetcher using actual API endpoints."""
    
    API_BASE = "https://api.gotinder.com"
    
    def __init__(self, auth_handler: TinderAuthReal):
        self.auth = auth_handler
    
    def fetch_recommendations(self, limit: int = 50) -> Dict[str, Any]:
        """
        Fetch recommended profiles using real Tinder API.
        
        Endpoint: GET /user/recs
        Documentation: https://gist.github.com/rtt/10403467
        
        Response includes:
        - _id: user ID
        - name: user name
        - age: age
        - bio: biography
        - photos: list of photo objects with multiple sizes
        - distance_mi: distance
        - gender: gender (0=woman, 1=man)
        - common_likes: mutual likes
        - common_friends: mutual friends
        """
        try:
            if not self.auth.is_authenticated():
                return {
                    "status": "error",
                    "message": "Not authenticated",
                    "profiles": []
                }
            
            print(f"Fetching {limit} Tinder recommendations...")
            
            # Use real Tinder API endpoint
            resp = requests.get(
                f"{self.API_BASE}/user/recs",
                headers=self.auth._get_headers(self.auth.get_auth_token()),
                params={"limit": limit},
                timeout=15
            )
            
            if not resp.ok:
                print(f"Tinder API error: {resp.status_code}")
                if resp.status_code == 401:
                    return {
                        "status": "error",
                        "message": "Authentication failed - token may be expired",
                        "profiles": []
                    }
                elif resp.status_code == 429:
                    return {
                        "status": "error",
                        "message": "Rate limited by Tinder",
                        "profiles": []
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"API returned {resp.status_code}",
                        "error_body": resp.text,
                        "profiles": []
                    }
            
            data = resp.json()
            profiles = data.get("results", [])
            
            print(f"Fetched {len(profiles)} Tinder profiles")
            
            # Extract key fields from real Tinder response
            normalized_profiles = []
            for p in profiles:
                normalized_profiles.append({
                    "_id": p.get("_id"),
                    "name": p.get("name"),
                    "age": p.get("age"),
                    "bio": p.get("bio", ""),
                    "gender": p.get("gender"),  # 0=woman, 1=man
                    "distance_mi": p.get("distance_mi"),
                    "photos": p.get("photos", []),
                    "common_likes": p.get("common_like_count", 0),
                    "common_friends": p.get("common_friend_count", 0),
                    "ping_time": p.get("ping_time"),  # Last active
                    "birth_date": p.get("birth_date"),
                })
            
            return {
                "status": "success",
                "profiles": normalized_profiles,
                "total": len(normalized_profiles)
            }
        
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": "Request timeout - Tinder server not responding",
                "profiles": []
            }
        except requests.exceptions.ConnectionError as e:
            return {
                "status": "error",
                "message": f"Connection error: {e}",
                "profiles": []
            }
        except Exception as e:
            print(f"Error fetching Tinder recommendations: {e}")
            return {
                "status": "error",
                "message": str(e),
                "profiles": []
            }
    
    def like_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Like a profile using real Tinder API.
        
        Endpoint: POST /like/{user_id}
        Returns: {match: boolean}
        """
        try:
            if not self.auth.is_authenticated():
                return {"status": "error", "message": "Not authenticated"}
            
            print(f"Liking profile: {profile_id}")
            
            resp = requests.post(
                f"{self.API_BASE}/like/{profile_id}",
                headers=self.auth._get_headers(self.auth.get_auth_token()),
                timeout=10
            )
            
            if not resp.ok:
                return {
                    "status": "error",
                    "message": f"Like failed: {resp.status_code}"
                }
            
            data = resp.json()
            matched = data.get("match", False)
            
            print(f"Like result: matched={matched}")
            
            return {
                "status": "success",
                "profile_id": profile_id,
                "matched": matched
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def pass_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Pass on a profile using real Tinder API.
        
        Endpoint: POST /pass/{user_id}
        """
        try:
            if not self.auth.is_authenticated():
                return {"status": "error", "message": "Not authenticated"}
            
            print(f"Passing profile: {profile_id}")
            
            resp = requests.post(
                f"{self.API_BASE}/pass/{profile_id}",
                headers=self.auth._get_headers(self.auth.get_auth_token()),
                timeout=10
            )
            
            if not resp.ok:
                return {
                    "status": "error",
                    "message": f"Pass failed: {resp.status_code}"
                }
            
            return {
                "status": "success",
                "profile_id": profile_id,
                "action": "passed"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def fetch_matches(self, limit: int = 10) -> Dict[str, Any]:
        """
        Fetch matches using real Tinder API.
        
        Endpoint: GET /user/matches
        """
        try:
            if not self.auth.is_authenticated():
                return {
                    "status": "error",
                    "message": "Not authenticated",
                    "matches": []
                }
            
            print(f"Fetching {limit} Tinder matches...")
            
            resp = requests.get(
                f"{self.API_BASE}/user/matches",
                headers=self.auth._get_headers(self.auth.get_auth_token()),
                params={"limit": limit},
                timeout=15
            )
            
            if not resp.ok:
                return {
                    "status": "error",
                    "message": f"Matches fetch failed: {resp.status_code}",
                    "matches": []
                }
            
            data = resp.json()
            matches = data.get("matches", [])
            
            print(f"Fetched {len(matches)} matches")
            
            return {
                "status": "success",
                "matches": matches,
                "total": len(matches)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "matches": []
            }


def tinder_profile_fetcher_real(auth_handler: TinderAuthReal):
    """Factory function."""
    return TinderProfileFetcherReal(auth_handler)


if __name__ == "__main__":
    auth = TinderAuthReal()
    
    # Simulate auth
    auth.authenticate_with_phone("+1-555-123-4567")
    
    if auth.is_authenticated():
        fetcher = TinderProfileFetcherReal(auth)
        recs = fetcher.fetch_recommendations(limit=50)
        print(f"Recommendations: {len(recs.get('profiles', []))} fetched")
