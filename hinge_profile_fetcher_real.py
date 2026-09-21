"""
Real Hinge Profile Fetcher using squeaky-hinge API approach

Fetches profiles from the actual Hinge API endpoints.
"""

import requests
import json
from typing import Dict, List, Optional, Any
from hinge_auth_real import HingeAuthReal


class HingeProfileFetcherReal:
    """Real Hinge profile fetcher using actual API endpoints."""
    
    API_BASE = "https://prod-api.hingeaws.net"
    
    def __init__(self, auth_handler: HingeAuthReal):
        self.auth = auth_handler
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Hinge API requests."""
        token = self.auth.get_access_token()
        user_id = self.auth.get_user_id()
        
        return {
            "Authorization": f"Bearer {token}" if token else "",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-App-Version": "13.2.0",
            "X-Device-Platform": "Android",
        }
    
    def fetch_recommendations(self, limit: int = 50) -> Dict[str, Any]:
        """
        Fetch recommended profiles from Hinge.
        
        Real endpoint might be:
        - /user/profile/recommendations
        - /discover/recommendations
        - /user/discovery
        """
        try:
            if not self.auth.is_authenticated():
                return {
                    "status": "error",
                    "message": "Not authenticated",
                    "profiles": []
                }
            
            headers = self._get_headers()
            
            # Try potential Hinge endpoints
            endpoints = [
                f"{self.API_BASE}/user/discovery",
                f"{self.API_BASE}/recommendations",
                f"{self.API_BASE}/user/profiles/recommendations",
            ]
            
            print(f"Fetching up to {limit} Hinge recommendations...")
            
            for endpoint in endpoints:
                try:
                    resp = requests.get(
                        endpoint,
                        headers=headers,
                        params={"limit": limit},
                        timeout=15
                    )
                    
                    if resp.ok:
                        data = resp.json()
                        profiles = data.get("data", data.get("results", []))
                        
                        print(f"Fetched {len(profiles)} profiles from Hinge")
                        return {
                            "status": "success",
                            "profiles": profiles,
                            "total": len(profiles),
                            "endpoint_used": endpoint
                        }
                except requests.exceptions.RequestException:
                    continue
            
            # If all endpoints failed
            return {
                "status": "error",
                "message": "Could not fetch recommendations from any endpoint",
                "profiles": []
            }
        
        except Exception as e:
            print(f"Error fetching recommendations: {e}")
            return {
                "status": "error",
                "message": str(e),
                "profiles": []
            }
    
    def fetch_matches(self, limit: int = 20) -> Dict[str, Any]:
        """Fetch user's matches from Hinge."""
        try:
            if not self.auth.is_authenticated():
                return {
                    "status": "error",
                    "message": "Not authenticated",
                    "matches": []
                }
            
            headers = self._get_headers()
            
            print(f"Fetching Hinge matches...")
            
            resp = requests.get(
                f"{self.API_BASE}/user/matches",
                headers=headers,
                params={"limit": limit},
                timeout=15
            )
            
            if not resp.ok:
                return {
                    "status": "error",
                    "message": f"API returned {resp.status_code}",
                    "matches": []
                }
            
            data = resp.json()
            matches = data.get("data", data.get("matches", []))
            
            print(f"Fetched {len(matches)} matches")
            
            return {
                "status": "success",
                "matches": matches,
                "total": len(matches)
            }
        
        except Exception as e:
            print(f"Error fetching matches: {e}")
            return {
                "status": "error",
                "message": str(e),
                "matches": []
            }
    
    def get_profile_details(self, profile_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific profile."""
        try:
            if not self.auth.is_authenticated():
                return {"status": "error", "message": "Not authenticated"}
            
            headers = self._get_headers()
            
            resp = requests.get(
                f"{self.API_BASE}/user/{profile_id}",
                headers=headers,
                timeout=15
            )
            
            if not resp.ok:
                return {
                    "status": "error",
                    "message": f"Could not fetch profile: {resp.status_code}"
                }
            
            profile = resp.json()
            return {
                "status": "success",
                "profile": profile
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


def hinge_profile_fetcher_real(auth_handler: HingeAuthReal):
    """Factory function."""
    return HingeProfileFetcherReal(auth_handler)


if __name__ == "__main__":
    auth = HingeAuthReal()
    if auth.is_authenticated():
        fetcher = HingeProfileFetcherReal(auth)
        recs = fetcher.fetch_recommendations(limit=50)
        print(f"Recommendations: {len(recs.get('profiles', []))} fetched")
