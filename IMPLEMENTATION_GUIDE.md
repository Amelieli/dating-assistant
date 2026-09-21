# Implementation Guide: Dating App Scrapers

This guide walks you through implementing real scrapers for Tinder, Hinge, and Match.

## Important: Authentication & Legal

Before implementing, understand:

1. **Terms of Service**: Most dating apps prohibit scraping/API access
2. **Rate Limiting**: Implement delays between requests to avoid detection
3. **Account Risk**: Your account could be banned for scraping activity
4. **Data Privacy**: Handle user data responsibly

Proceed at your own risk. This tool is for personal use only.

## Tinder Scraper Implementation

### Step 1: Get Authentication Token

```python
# Option A: From Facebook Token
import requests

def get_tinder_auth_token_via_facebook(facebook_token):
    """Get Tinder X-Auth-Token from Facebook token."""
    
    response = requests.post(
        'https://api.gotinder.com/auth',
        json={
            'facebook_token': facebook_token
        }
    )
    
    data = response.json()
    return data.get('token')

# Option B: From Phone Number
def get_tinder_auth_token_via_phone(phone_number):
    """Get Tinder X-Auth-Token using phone OTP."""
    
    # 1. Request OTP
    response = requests.post(
        'https://api.gotinder.com/v2/auth/sms/send',
        json={'phone_number': phone_number}
    )
    
    # 2. User enters OTP from SMS
    otp = input("Enter OTP: ")
    
    # 3. Verify OTP and get token
    response = requests.post(
        'https://api.gotinder.com/v2/auth/sms/validate',
        json={
            'phone_number': phone_number,
            'otp': otp
        }
    )
    
    data = response.json()
    return data.get('data', {}).get('refresh_token')
```

### Step 2: Implement Tinder Scraper

```python
from scrapers.base_scraper import TinderScraper
from models.profile import Profile, AppSource
import requests
from datetime import datetime

class TinderScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.session = None
        self.auth_token = None
    
    @property
    def source(self) -> AppSource:
        return AppSource.TINDER
    
    def authenticate(self, credentials):
        """Authenticate with Tinder."""
        try:
            self.session = requests.Session()
            
            if 'facebook_token' in credentials:
                token = get_tinder_auth_token_via_facebook(
                    credentials['facebook_token']
                )
            elif 'phone' in credentials:
                token = get_tinder_auth_token_via_phone(
                    credentials['phone']
                )
            else:
                return False
            
            self.auth_token = token
            self.session.headers.update({
                'X-Auth-Token': self.auth_token,
                'User-Agent': 'Mozilla/5.0...'  # Spoof browser
            })
            
            return True
        except Exception as e:
            logger.error(f"Tinder auth failed: {e}")
            return False
    
    def get_matches(self):
        """Fetch mutual matches."""
        try:
            # Your likes
            your_likes_resp = self.session.get(
                'https://api.gotinder.com/v2/recs/core',
                params={'count': 100}
            )
            
            # They like you
            likes_received_resp = self.session.get(
                'https://api.gotinder.com/v2/matches',
            )
            
            your_likes = set()
            for item in your_likes_resp.json().get('data', {}).get('results', []):
                your_likes.add(item['user']['_id'])
            
            mutual_profiles = []
            for match in likes_received_resp.json().get('data', {}).get('matches', []):
                user_id = match.get('_id') or match.get('user', {}).get('_id')
                
                if user_id in your_likes:
                    # Mutual match!
                    profile = self._parse_tinder_user(match.get('person') or match)
                    mutual_profiles.append(profile)
            
            return mutual_profiles
        except Exception as e:
            logger.error(f"Failed to get Tinder matches: {e}")
            return []
    
    def get_likes_received(self):
        """Fetch incoming likes."""
        try:
            response = self.session.get(
                'https://api.gotinder.com/v2/likes/me'
            )
            
            profiles = []
            for item in response.json().get('data', {}).get('results', []):
                profile = self._parse_tinder_user(item['user'])
                profiles.append(profile)
            
            return profiles
        except Exception as e:
            logger.error(f"Failed to get Tinder likes: {e}")
            return []
    
    def get_likes_sent(self):
        """Fetch profiles you've liked."""
        try:
            response = self.session.get(
                'https://api.gotinder.com/v2/likes/recs'
            )
            
            profiles = []
            for item in response.json().get('data', {}).get('results', []):
                profile = self._parse_tinder_user(item)
                profiles.append(profile)
            
            return profiles
        except Exception as e:
            logger.error(f"Failed to get Tinder sent likes: {e}")
            return []
    
    def _parse_tinder_user(self, user_data: dict) -> Profile:
        """Parse Tinder user JSON into Profile."""
        
        photos = [p['url'] for p in user_data.get('photos', [])]
        
        # Extract location
        location = user_data.get('location', {})
        city = location.get('city', '')
        
        # Calculate distance
        distance_km = None
        if 'distance_mi' in user_data:
            distance_km = user_data['distance_mi'] * 1.60934
        
        return Profile(
            app_id=user_data['_id'],
            app_source=AppSource.TINDER,
            name=user_data['name'],
            age=user_data.get('birth_date'),  # Parse properly
            city=city,
            state='',
            country='',
            distance_km=distance_km,
            bio=user_data.get('bio', ''),
            interests=[],  # Tinder doesn't always expose interests
            occupation=user_data.get('job', {}).get('title', ''),
            education=user_data.get('school', {}).get('name', ''),
            drinks=None,
            smokes=None,
            photo_urls=photos,
            verified=user_data.get('verified', False),
        )
```

## Hinge Scraper Implementation

```python
class HingeScraper(BaseScraper):
    
    def authenticate(self, credentials):
        """Authenticate with Hinge using session token."""
        try:
            self.session = requests.Session()
            
            # Set auth headers with session token
            token = credentials.get('session_token')
            self.session.headers.update({
                'Authorization': f'Bearer {token}',
                'User-Agent': credentials.get('user_agent', 'Mozilla/5.0...'),
                'X-Requested-With': 'XMLHttpRequest'
            })
            
            # Verify auth works
            response = self.session.get('https://hinge.co/api/users/me')
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Hinge auth failed: {e}")
            return False
    
    def get_matches(self):
        """Fetch mutual matches from Hinge."""
        try:
            # Get your likes
            your_likes = self._get_your_likes()
            
            # Get incoming likes
            incoming = self._get_incoming_likes()
            
            # Find mutual
            your_like_ids = {(p.app_id, p.app_source) for p in your_likes}
            
            mutual = [
                p for p in incoming 
                if (p.app_id, p.app_source) in your_like_ids
            ]
            
            return mutual
        except Exception as e:
            logger.error(f"Failed to get Hinge matches: {e}")
            return []
    
    def _get_your_likes(self):
        """Get profiles you've liked on Hinge."""
        try:
            response = self.session.get(
                'https://hinge.co/api/users/me/likes/sent',
                params={'limit': 100}
            )
            
            profiles = []
            for item in response.json().get('data', []):
                profile = self._parse_hinge_user(item['profile'])
                profiles.append(profile)
            
            return profiles
        except Exception as e:
            logger.error(f"Failed to get Hinge sent likes: {e}")
            return []
    
    def _get_incoming_likes(self):
        """Get profiles who liked you on Hinge."""
        try:
            response = self.session.get(
                'https://hinge.co/api/users/me/likes/received',
                params={'limit': 100}
            )
            
            profiles = []
            for item in response.json().get('data', []):
                profile = self._parse_hinge_user(item['profile'])
                profiles.append(profile)
            
            return profiles
        except Exception as e:
            logger.error(f"Failed to get Hinge received likes: {e}")
            return []
    
    def _parse_hinge_user(self, user_data: dict) -> Profile:
        """Parse Hinge user JSON into Profile."""
        
        photos = [p['url'] for p in user_data.get('photos', [])]
        interests = user_data.get('interests', [])
        
        return Profile(
            app_id=user_data['id'],
            app_source=AppSource.HINGE,
            name=user_data['name'],
            age=user_data.get('age', 0),
            city=user_data.get('city', ''),
            state=user_data.get('state', ''),
            country=user_data.get('country', ''),
            distance_km=user_data.get('distance_km'),
            bio=user_data.get('about', ''),
            interests=interests,
            occupation=user_data.get('occupation', ''),
            education=user_data.get('education', ''),
            photo_urls=photos,
            verified=user_data.get('verified', False),
        )
```

## Match Scraper Implementation

```python
class MatchScraper(BaseScraper):
    
    def authenticate(self, credentials):
        """Authenticate with Match using username/password."""
        try:
            self.session = requests.Session()
            
            # Login
            response = self.session.post(
                'https://www.match.com/auth/login',
                json={
                    'email': credentials['username'],
                    'password': credentials['password']
                }
            )
            
            if response.status_code != 200:
                return False
            
            # Extract session/auth tokens from response
            self.auth_token = response.json().get('token')
            
            self.session.headers.update({
                'Authorization': f'Bearer {self.auth_token}',
                'User-Agent': 'Mozilla/5.0...'
            })
            
            return True
        except Exception as e:
            logger.error(f"Match auth failed: {e}")
            return False
    
    def get_matches(self):
        """Fetch mutual matches from Match."""
        try:
            # Similar logic to Hinge
            # Get your likes and incoming likes, find mutual
            pass
        except Exception as e:
            logger.error(f"Failed to get Match matches: {e}")
            return []
```

## Testing Your Scrapers

```python
# test_scrapers.py

from scrapers.base_scraper import TinderScraper, HingeScraper, MatchScraper

def test_tinder():
    scraper = TinderScraper()
    
    # Test auth
    success = scraper.authenticate({
        'facebook_token': 'your_token_here'
    })
    print(f"Auth successful: {success}")
    
    # Test fetching data
    matches = scraper.get_matches()
    print(f"Found {len(matches)} mutual matches")
    
    for match in matches[:3]:
        print(f"  - {match.name}, {match.age} from {match.city}")

def test_hinge():
    scraper = HingeScraper()
    success = scraper.authenticate({
        'session_token': 'your_token_here'
    })
    print(f"Hinge auth: {success}")
    
    likes = scraper.get_likes_received()
    print(f"Received {len(likes)} likes")

if __name__ == '__main__':
    test_tinder()
    test_hinge()
```

## Rate Limiting & Anti-Detection

To avoid being detected/banned:

```python
import time
import random

class SlowScraper:
    def __init__(self):
        self.min_delay = 2  # seconds
        self.max_delay = 5
    
    def _delay(self):
        """Random delay between requests."""
        time.sleep(random.uniform(self.min_delay, self.max_delay))
    
    def get_matches(self):
        # ... code ...
        self._delay()
        response = self.session.get(url)
        self._delay()
        return data
```

## Handling Auth Expiration

```python
class ResilientScraper:
    
    def _request_with_retry(self, method, url, max_retries=3):
        """Make request with automatic re-auth on 401."""
        
        for attempt in range(max_retries):
            response = getattr(self.session, method)(url)
            
            if response.status_code == 401:
                # Token expired, re-authenticate
                logger.info("Token expired, re-authenticating...")
                if self.authenticate(self.stored_credentials):
                    continue  # Retry with new token
            
            return response
        
        raise Exception(f"Failed after {max_retries} attempts")
```

## Next Steps

1. Get fresh auth tokens for each app
2. Implement one scraper at a time
3. Test with small batches first
4. Add proper error handling & retries
5. Deploy with monitoring for failures
6. Use VPN/proxy to avoid IP bans if needed

Good luck!
