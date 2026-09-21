# Architecture Overview

## System Design

```
┌─────────────────────────────────────────────────────────────────┐
│                     React Frontend (Port 3000)                  │
│  ┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Mutual Matches   │  │ Incoming     │  │ Smart Filters &  │  │
│  │   Dashboard      │  │ Likes View   │  │ CLIP Search      │  │
│  └──────────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP/REST (JSON)
┌─────────────────────┴───────────────────────────────────────────┐
│               Flask API Server (Port 5000)                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  /init          /authenticate      /sync                 │  │
│  │  /matches/*     /filter-and-rank    /search/by-desc     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼──────┐ ┌───▼───────┐ ┌──▼─────────┐
│ Orchestrator │ │   Filter  │ │    CLIP    │
│   Agent      │ │  Engine   │ │  Matcher   │
└───────┬──────┘ └───────────┘ └────────────┘
        │
┌───────┴─────────────────────────────────────────┐
│         Scraper Layer (Stub Implementation)      │
│  ┌──────────────┐ ┌──────────┐ ┌──────────┐    │
│  │    Tinder    │ │  Hinge   │ │  Match   │    │
│  │   Scraper    │ │ Scraper  │ │ Scraper  │    │
│  └──────────────┘ └──────────┘ └──────────┘    │
└───────┬──────────────────────────────────────────┘
        │
┌───────▼──────────────────────────────────────────┐
│    Dating App APIs (Tinder, Hinge, Match)        │
│  (Requires actual implementation & auth)         │
└──────────────────────────────────────────────────┘
```

## Data Flow

### 1. Initialization Phase

```
User Input (Frontend)
    ↓
FilterPanel Component
    ↓
POST /init {min_age, max_distance, interests, use_clip, ...}
    ↓
DatingAppOrchestrator.__init__
    └─ FilterEngine(FilterConfig)
    └─ CLIPMatcher()
    └─ TinderScraper(), HingeScraper(), MatchScraper()
    ↓
Response: {status: "initialized", config: {...}}
```

### 2. Authentication Phase

```
User Provides Credentials (Frontend)
    ↓
POST /authenticate {tinder: {facebook_token}, hinge: {...}, match: {...}}
    ↓
For each scraper:
    scraper.authenticate(credentials[app])
        ↓
        [Tinder]   -> GET https://api.gotinder.com/v2/auth/validate
        [Hinge]    -> GET https://hinge.co/api/users/me
        [Match]    -> POST https://www.match.com/auth/login
    ↓
Response: {results: {tinder: true, hinge: true, match: false}}
```

### 3. Data Sync Phase

```
POST /sync
    ↓
orchestrator.sync_all_apps()
    ↓
For each scraper:
    1. scraper.get_likes_sent()
       -> Profiles YOU liked
       -> Store as OUTGOING
    
    2. scraper.get_likes_received()
       -> Profiles who liked YOU
       -> Store as INCOMING
    
    3. scraper.get_matches()
       -> Profiles who like YOU and YOU liked
       -> Store as MUTUAL
    ↓
consolidate_to_self.all_profiles {}
    ↓
Response: {total_profiles: 150, total_mutual: 12, total_incoming: 34}
```

### 4. Filtering Phase

```
POST /filter-and-rank {your_interests: [...], embed_photos: false}
    ↓
for profile in all_profiles:
    
    # Apply strict filters (ALL must pass)
    ├─ Age check: min_age <= profile.age <= max_age
    ├─ Distance check: profile.distance_km <= max_distance
    ├─ Interest check: overlap >= min_interest_overlap
    ├─ Lifestyle check: not (must_not_smoke AND profile.smokes)
    └─ ... other checks ...
    
    if ALL pass:
        ├─ Calculate match_percentage
        │  = base_score (50)
        │    + interest_overlap_score (0-50)
        │    + distance_bonus (0-10)
        │
        └─ Add to filtered_profiles[]
    ↓
Sort by match_percentage DESC
    ↓
Response:
{
    mutual_matches: [...],      # MUTUAL status, sorted by score
    incoming_likes: [...],      # INCOMING status, sorted by score
    potential_matches: [...]    # ALL filtered, sorted by score
}
```

### 5. CLIP Matching Phase (Optional)

```
POST /search/by-description {description: "athletic blonde woman"}
    ↓
clip_matcher.embed_text(description)
    └─ CLIP encodes text → 512-dim vector
    ↓
for profile in candidates:
    for photo_url in profile.photo_urls:
        if not profile.photo_embedding[i]:
            # Embed photo on first run (slow)
            photo_embedding = clip_matcher.embed_image(photo_url)
            # Cache for future use
    
    # Average all photo embeddings
    avg_embedding = mean(profile.photo_embeddings)
    
    # Compute similarity
    similarity = cosine_similarity(text_embedding, avg_embedding)
    
    if similarity >= threshold (0.7):
        results.append((profile, similarity))
    ↓
Sort by similarity DESC
    ↓
Response: {matches: [{profile: {...}, similarity_score: 0.82}, ...]}
```

## Component Responsibilities

### Frontend (React)

**App.tsx**
- Main app shell
- Tab navigation
- Header & stats display
- API lifecycle (init, auth, sync)

**MutualMatches.tsx**
- Display MUTUAL status profiles
- Sorting (score, distance, recent)
- Profile grid layout

**NewLikes.tsx**
- Display INCOMING likes
- Filter by app source
- Highlight new badges

**FilterPanel.tsx**
- Configuration form
- Age range, distance, interests
- Lifestyle checkboxes
- CLIP toggle

**Dashboard.tsx**
- Quick stats cards
- Apply filters & ranking
- CLIP search interface
- How-it-works guide

**ProfileCard.tsx**
- Individual profile display
- Photo gallery
- Match score badge
- Interests tags
- Call-to-action button

### Backend (Python)

**models/profile.py**
- Unified Profile dataclass
- MatchStatus enum (MUTUAL, INCOMING, OUTGOING, REJECTED)
- AppSource enum (TINDER, HINGE, MATCH)
- Helper methods (to_dict, full_location, etc.)

**filtering/filter_engine.py**
- FilterConfig dataclass
- FilterEngine class with strict filter checks
- Match score calculation
- Factory functions for quick setup

**filtering/clip_matcher.py**
- CLIPMatcher class
- Image/text embedding with CLIP
- Cosine similarity computation
- Batch embedding for performance
- Text-based profile search

**scrapers/base_scraper.py**
- BaseScraper abstract class
- TinderScraper stub
- HingeScraper stub
- MatchScraper stub
- Caching utilities
- Auth abstraction

**orchestrator.py**
- DatingAppOrchestrator main class
- Multi-app coordination
- Profile deduplication
- Sync orchestration
- Filter application
- Result aggregation & ranking

**api.py**
- Flask REST API
- CORS enabled
- 10+ endpoints for frontend
- Error handling & logging
- JSON serialization

## Key Design Principles

### 1. Separation of Concerns
- **Scrapers**: Data fetching only
- **Filtering**: Business logic
- **API**: HTTP interface only
- **Frontend**: UI/UX only

### 2. Single Responsibility
- Profile: unified schema only
- FilterEngine: filtering logic only
- CLIPMatcher: image matching only
- Orchestrator: coordination only

### 3. DRY (Don't Repeat Yourself)
- Profile.to_dict() used everywhere
- BaseScraper handles caching
- Filter checks encapsulated

### 4. YAGNI (You Aren't Gonna Need It)
- No unused fields in Profile
- No premature optimization
- Simple, readable code

## Performance Considerations

### API Response Times
- `/matches/mutual` - O(n) where n = total profiles
- `/filter-and-rank` - O(n * m) where m = number of checks
- `/search/by-description` - O(n * d) where d = embedding dimension (512)

### Memory Usage
- All profiles in memory: ~1KB per profile
- CLIP model: ~4GB on disk, ~2GB loaded
- Photo embeddings: ~2KB per embedding (512 floats)

### Optimization Strategies
1. Cache photo embeddings after first embedding
2. Batch CLIP requests for multiple photos
3. Paginate large result sets
4. Use GPU for CLIP if available
5. Implement lazy loading in frontend

## Extensibility

### Adding New Filters
1. Add field to FilterConfig
2. Add check method to FilterEngine
3. Include in _passes_all_filters()

### Adding New Dating Apps
1. Create YourAppScraper(BaseScraper)
2. Implement 3 methods: authenticate(), get_matches(), get_likes_received()
3. Implement get_likes_sent()
4. Add YourAppSource to AppSource enum
5. Register in DatingAppOrchestrator.scrapers

### Adding New Matching Algorithms
1. Subclass CLIPMatcher or FilterEngine
2. Override similarity/score methods
3. Use in filter_and_rank()

## Security Considerations

1. **Auth Tokens**: Never log or expose
2. **User Data**: Handle with care
3. **API Rate Limiting**: Implement in scrapers
4. **CORS**: Only allow trusted origins
5. **Input Validation**: Validate all API inputs
6. **Account Security**: Use strong passwords, 2FA
