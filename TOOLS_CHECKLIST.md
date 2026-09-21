# Dating Agent Tools Checklist

## CRITICAL - Authentication Layer

- [ ] **multi_auth_manager** - Orchestrates auth across all 3 platforms
  - Manages multiple auth states simultaneously
  - Routes auth requests to platform-specific handlers
  - Stores tokens encrypted
  
- [ ] **hinge.auth_handler** - Hinge-specific authentication
  - Phone number verification via OTP
  - OAuth token management
  - Session persistence
  - Automatic token refresh
  
- [ ] **tinder.auth_handler** - Tinder-specific authentication  
  - Phone OTP verification
  - OAuth (Facebook/Google) integration
  - Token refresh with rotation
  - Device fingerprinting support (anti-detection)
  - Proxy chain support
  
- [ ] **league.auth_handler** - The League session management
  - Email/password login
  - Cookie-based session persistence
  - Browser fingerprint spoofing
  - Headless browser integration
  
- [ ] **token_vault** - Encrypted token storage
  - Stores auth tokens securely (encrypted at rest)
  - Automatic rotation
  - Recovery mechanisms
  - Audit logging

---

## CRITICAL - Profile Fetching Layer

- [ ] **hinge.profile_fetcher** - Hinge SDK wrapper
  - Wraps official Hinge SDK
  - Handles pagination
  - Error recovery and retries
  - Type validation
  
- [ ] **tinder.profile_fetcher** - Tinder reverse-engineered client
  - Uses reverse-engineered Tinder API
  - Handles recs endpoints
  - Manages swipe history
  - Handles match list fetching
  - Proxy rotation
  - Anti-detection headers
  
- [ ] **league.profile_fetcher** - The League scraper/API client
  - Web scraper using Playwright/Selenium
  - Or reverse-engineered API calls
  - Handles dynamic content loading
  - Manages pagination
  - Screenshot fallback for images
  
- [ ] **profile_aggregator** - Unified fetching coordinator
  - Orchestrates fetching from all 3 sources
  - Manages concurrent requests
  - Handles partial failures gracefully
  - Tracks fetch status and metadata
  
---

## HIGH - Data Processing Layer

- [ ] **profile_normalizer** - Converts to common schema
  - Hinge profile -> normalized profile
  - Tinder profile -> normalized profile
  - League profile -> normalized profile
  - Standardizes field names and types
  - Validates required fields
  
- [ ] **photo_processor** - Handles profile photos
  - Downloads photos from URLs
  - Resizes/optimizes images
  - Detects duplicates across platforms
  - Stores locally or in cloud
  - Generates thumbnails
  - Error handling for broken links
  
- [ ] **text_processor** - Standardizes text content
  - Normalize bios across platforms
  - Parse prompts/answers (Hinge-specific)
  - Extract hashtags and mentions
  - Language detection
  - Profanity filtering (optional)
  - Emoji normalization
  
- [ ] **deduplicator** - Cross-app profile matching
  - Fuzzy name matching
  - Photo fingerprinting (detect same person)
  - Bio similarity matching
  - Location proximity matching
  - Creates merged profiles
  - Conflict resolution for duplicate fields
  
---

## HIGH - Storage Layer

- [ ] **profile_store** - Database adapter
  - SQLite or PostgreSQL backend
  - Schema for normalized profiles
  - Indexes for performance
  - Query interface
  - Batch insert/update
  - Duplicate detection queries
  
- [ ] **session_manager** - Persistent session storage
  - Stores auth sessions per user
  - Auto-loads on startup
  - Expiration handling
  - Concurrent session support
  
- [ ] **metrics_store** - Performance/usage tracking
  - Logs API calls per platform
  - Tracks rate limits hit
  - Records error counts
  - Monitors ban detection triggers
  
---

## HIGH - Rate Limiting & Safety

- [ ] **rate_limiter** - Global request throttling
  - Per-platform rate limits (different for each app)
  - Adaptive backoff on rate limit detection
  - Ban detection with auto-pause
  - Cool-down management
  - Request queue with priority
  
- [ ] **proxy_manager** - (Optional but recommended)
  - Rotation through proxy list
  - Proxy health checks
  - Fallback mechanisms
  - Per-request proxy assignment
  
- [ ] **ban_detector** - Detects when account is being throttled/banned
  - Monitors 401/403 responses
  - Tracks consecutive failures
  - Triggers cooldown periods
  - Alerts on permanent ban patterns
  
---

## MEDIUM - Utilities

- [ ] **otp_handler** - SMS/Email OTP verification
  - Can integrate with Twilio, etc.
  - Handles OTP parsing
  - Timeout management
  - Retry logic
  
- [ ] **config_manager** - Centralized configuration
  - Rate limits per platform
  - API keys and secrets
  - Proxy lists
  - Feature flags
  - Environment-specific settings
  
- [ ] **error_handler** - Centralized error recovery
  - Categorizes errors (auth, rate limit, network, parsing)
  - Implements recovery strategies
  - Logs detailed error context
  - Alerts on critical errors
  
- [ ] **metrics_collector** - Performance monitoring
  - Tracks execution times
  - API call counts
  - Success/failure rates
  - Resource usage
  - Generates reports

---

## NICE TO HAVE - Advanced Features

- [ ] **pagination_handler** - Unified pagination across platforms
  - Handles different pagination styles
  - Resumes from checkpoints
  - Prevents duplicate fetches
  
- [ ] **browser_automation** - Headless browser integration
  - Uses Playwright for anti-bot bypass
  - JavaScript execution support
  - Screenshot capture
  - Cookie management
  
- [ ] **match_engine** - Advanced deduplication
  - ML-based name matching
  - Photo similarity neural net
  - Handles variations (nicknames, etc.)
  
- [ ] **notification_system** - Alerts on events
  - Ban detection alerts
  - Sync completion notifications
  - Error notifications
  - Rate limit warnings

---

## Implementation Priority

### Phase 1 (Weeks 1-2): Foundation
1. token_vault
2. multi_auth_manager
3. profile_store
4. config_manager

### Phase 2 (Weeks 3-4): Core Auth
5. hinge.auth_handler
6. tinder.auth_handler
7. league.auth_handler

### Phase 3 (Weeks 5-6): Fetching
8. hinge.profile_fetcher
9. tinder.profile_fetcher
10. league.profile_fetcher
11. profile_aggregator

### Phase 4 (Weeks 7-8): Processing
12. profile_normalizer
13. photo_processor
14. text_processor
15. deduplicator

### Phase 5 (Weeks 9-10): Safety & Polish
16. rate_limiter
17. ban_detector
18. metrics_collector
19. error_handler
20. otp_handler

---

## Risk Assessment by Tool

| Tool | Complexity | Risk Level | Notes |
|------|-----------|-----------|-------|
| multi_auth_manager | High | Medium | Many edge cases |
| hinge.auth_handler | Medium | Low | Official SDK available |
| tinder.auth_handler | Very High | High | Changes frequently, anti-detection needed |
| league.auth_handler | Very High | High | No official API, browser needed |
| profile_normalizer | Medium | Low | Well-defined schema |
| deduplicator | High | Medium | Fuzzy matching is tricky |
| rate_limiter | High | Medium | Must be aggressive enough |
| ban_detector | Medium | Medium | Hard to predict |

---

## Dependency Graph

```
config_manager
    |
    +-- multi_auth_manager
    |       |-- hinge.auth_handler
    |       |-- tinder.auth_handler
    |       +-- league.auth_handler
    |           |
    |           +-- token_vault
    |
    +-- rate_limiter
    |       +-- ban_detector
    |
    +-- profile_aggregator
    |       |-- hinge.profile_fetcher
    |       |-- tinder.profile_fetcher
    |       |-- league.profile_fetcher
    |       |
    |       +-- profile_normalizer
    |           |-- text_processor
    |           +-- photo_processor
    |               |
    |               +-- profile_store
    |                   |
    |                   +-- deduplicator
    |
    +-- error_handler
    +-- metrics_collector
    +-- otp_handler
```

---

## Total Effort Estimate

- **Total Tools**: 20
- **Critical Tools**: 5
- **Estimated Development Time**: 8-12 weeks (1 person, full-time)
- **Most Time-Consuming**: tinder.auth_handler, league.auth_handler, deduplicator
- **Most Risk**: Keeping Tinder/League clients working as APIs change

---

## Build Recommendations

1. **Start with Hinge** - It has an official SDK, lowest risk
2. **Only add Tinder if** you accept the legal/TOS risk
3. **Skip League initially** - Most difficult, least accessible API
4. **Build in phases** - Don't try to build all 20 at once
5. **Test incrementally** - Each tool should have unit tests
6. **Monitor actively** - Set up alerts for when APIs break

