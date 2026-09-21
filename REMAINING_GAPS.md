# Dating Agent - Remaining Implementation Gaps

## Executive Summary

12 of 20 tools are **COMPLETE**. You need 8 more tools to have a fully functional system.

**Critical Path to MVP**: Hinge only = 3 more tools (2-3 weeks)
**Full System**: All platforms = 8 more tools (10-12 weeks)

---

## The Remaining 8 Tools (Priority Order)

### TIER 1: Essential for Functionality (CRITICAL - Need These First)

#### 1. hinge.auth_handler (PRIORITY: CRITICAL)
**Status**: NOT BUILT
**Difficulty**: MEDIUM
**Time Estimate**: 1 week
**Dependencies**: token_vault, otp_handler, config_manager, session_manager

**What It Does**:
- Authenticates users with Hinge via phone OTP
- Manages Hinge OAuth tokens
- Refreshes tokens before expiration
- Stores session state
- Recovers from auth failures

**Technical Requirements**:
- Phone number verification via OTP (using otp_handler)
- OAuth 2.0 token handling
- Session cookie management
- Token refresh mechanism
- Error handling for 401 responses

**Key Methods Needed**:
```python
- authenticate_with_phone(phone_number) -> str (otp_id)
- verify_phone_otp(otp_id, code) -> bool
- get_access_token(user_id) -> str
- refresh_access_token(user_id) -> bool
- is_authenticated(user_id) -> bool
- logout(user_id) -> bool
```

**Research Required**:
- Review HingeSDK documentation (ReedGraff/HingeSDK)
- Hinge API endpoints for auth
- OAuth flow details
- Token expiration and refresh timing

---

#### 2. hinge.profile_fetcher (PRIORITY: CRITICAL)
**Status**: NOT BUILT
**Difficulty**: MEDIUM
**Time Estimate**: 1-2 weeks
**Dependencies**: hinge.auth_handler, profile_normalizer, rate_limiter, error_handler

**What It Does**:
- Fetches recommended profiles from Hinge
- Retrieves user's matches
- Gets profile details (bios, photos, prompts)
- Handles pagination
- Retries on errors

**Technical Requirements**:
- HTTP client (httpx or urllib)
- Pagination loop for recommendations
- Photo URL extraction
- Prompt parsing (Hinge-specific)
- Error recovery

**Key Methods Needed**:
```python
- fetch_recommendations(user_id, limit=100) -> List[Dict]
- fetch_matches(user_id) -> List[Dict]
- fetch_profile_details(user_id, profile_id) -> Dict
- fetch_all_profiles(user_id) -> List[Dict]
- handle_pagination(response) -> List[Dict]
```

**Research Required**:
- Hinge API endpoints for /profiles, /recommendations, /matches
- Response schema for profiles
- Rate limits and best practices
- Photo resolution options
- Error codes and handling

---

#### 3. profile_aggregator (PRIORITY: CRITICAL)
**Status**: NOT BUILT
**Difficulty**: MEDIUM
**Time Estimate**: 1 week
**Dependencies**: All auth handlers, all fetchers, profile_store, metrics_collector

**What It Does**:
- Coordinates fetching from all enabled platforms
- Manages concurrent requests
- Deduplicates profiles
- Normalizes and stores profiles
- Reports progress and errors

**Technical Requirements**:
- Concurrent/async request handling
- Platform detection and routing
- Progress tracking
- Error aggregation
- Stats compilation

**Key Methods Needed**:
```python
- aggregate_all_profiles(user_ids_by_platform) -> Dict
- sync_platform(platform, user_id) -> Dict
- run_full_sync() -> Dict
- get_sync_status() -> Dict
- cancel_sync() -> bool
```

**Architecture**:
```python
for platform in enabled_platforms:
    authenticate(platform)
    for user_id in users[platform]:
        profiles = fetch_profiles(platform, user_id)
        for profile in profiles:
            normalized = normalize(profile, platform)
            deduplicated = dedup_check(normalized)
            store.add_profile(platform, user_id, normalized)
    metrics.log_sync(platform, stats)
```

---

### TIER 2: Platform-Specific Handlers (HIGH COMPLEXITY)

#### 4. tinder.auth_handler (PRIORITY: HIGH - but risky)
**Status**: NOT BUILT
**Difficulty**: VERY HIGH
**Time Estimate**: 2-3 weeks
**Dependencies**: token_vault, config_manager, session_manager
**Legal Risk**: HIGH (TOS violation, reverse engineering)

**What It Does**:
- Authenticates with Tinder (reverse-engineered)
- Manages OAuth tokens (Facebook/Google)
- Handles phone OTP verification
- Implements anti-detection measures
- Detects and responds to bans

**Technical Challenges**:
- No official API - requires reverse engineering
- Tinder actively detects bots
- Frequent API changes break clients
- Device fingerprinting needed
- User-Agent spoofing required
- Request signing/validation

**Key Methods Needed**:
```python
- authenticate_with_phone(phone_number) -> str (otp_id)
- authenticate_with_oauth(provider, oauth_token) -> bool
- verify_otp(otp_id, code) -> bool
- get_access_token(user_id) -> str
- refresh_access_token(user_id) -> bool
- is_banned(user_id) -> bool
- set_user_agent(user_agent) -> None
- set_device_id(device_id) -> None
```

**Research Required**:
- Study existing Tinder API clients (pindo, tinder-api)
- Reverse engineer current API endpoints
- Document request/response formats
- Find current auth mechanisms
- Monitor for API changes
- Implement request signing if needed

**Warning**: Tinder actively fights scrapers. This tool requires:
- Regular maintenance as APIs change
- Proxy rotation
- User-Agent cycling
- Device ID spoofing
- Detecting and handling bans

---

#### 5. tinder.profile_fetcher (PRIORITY: HIGH - but risky)
**Status**: NOT BUILT
**Difficulty**: VERY HIGH
**Time Estimate**: 2-3 weeks
**Dependencies**: tinder.auth_handler, profile_normalizer, rate_limiter

**What It Does**:
- Fetches recommended profiles from Tinder
- Retrieves match list
- Gets profile details
- Handles pagination
- Anti-detection evasion

**Technical Challenges**:
- Reverse-engineered API endpoints
- Complex response parsing
- Anti-bot rate limits
- IP-based blocking
- Frequent API schema changes

**Key Methods Needed**:
```python
- fetch_recommendations(user_id, limit=100) -> List[Dict]
- fetch_matches(user_id) -> List[Dict]
- fetch_profile_details(user_id, profile_id) -> Dict
- fetch_messages(user_id, match_id) -> List[Dict]
```

---

#### 6. league.auth_handler (PRIORITY: MEDIUM - but risky)
**Status**: NOT BUILT
**Difficulty**: VERY HIGH
**Time Estimate**: 2-3 weeks
**Dependencies**: token_vault, config_manager, browser automation
**Legal Risk**: VERY HIGH (no API, explicit scraping prohibition)

**What It Does**:
- Authenticates with The League (web-based)
- Manages session cookies
- Handles browser automation
- Implements anti-detection
- Recovers from blocks

**Technical Challenges**:
- No API available - web scraping only
- Requires headless browser (Playwright)
- JavaScript execution needed
- Anti-bot CloudFlare protection
- Account blocks on detection
- HTML parsing complexity

**Key Methods Needed**:
```python
- authenticate_with_email(email, password) -> bool
- open_browser_session() -> Browser
- get_session_cookies() -> Dict
- is_logged_in() -> bool
- handle_2fa() -> bool
```

**Requirements**:
- Playwright library (not in current env)
- Browser instance management
- Cookie jar handling
- Screenshot capability (for debugging)

**Warning**: The League actively blocks scrapers. Very high risk of:
- Account bans
- IP blocks
- Legal action (explicit TOS against scraping)

---

#### 7. league.profile_fetcher (PRIORITY: MEDIUM - but risky)
**Status**: NOT BUILT
**Difficulty**: VERY HIGH
**Time Estimate**: 2-3 weeks
**Dependencies**: league.auth_handler, browser automation
**Legal Risk**: VERY HIGH

**What It Does**:
- Scrapes The League profiles from web interface
- Extracts profile data from HTML
- Handles dynamic content loading
- Downloads photos
- Navigates pagination

**Technical Challenges**:
- HTML parsing complexity (no API)
- Dynamic JavaScript content
- Anti-scraping measures
- CloudFlare protection
- Frequent HTML changes break parser

**Key Methods Needed**:
```python
- fetch_recommendations() -> List[Dict]
- fetch_profile_details(profile_url) -> Dict
- extract_profile_data(html) -> Dict
- download_profile_photos(profile_id) -> List[str]
```

---

### TIER 3: Orchestration (Must have for multi-platform)

#### 8. multi_auth_manager (PRIORITY: MEDIUM - for multi-platform)
**Status**: NOT BUILT
**Difficulty**: MEDIUM
**Time Estimate**: 1 week
**Dependencies**: hinge.auth_handler, tinder.auth_handler, league.auth_handler

**What It Does**:
- Manages authentication for all 3 platforms simultaneously
- Routes requests to correct auth handler
- Manages token rotation
- Coordinates session state
- Handles cross-platform user mapping

**Key Methods Needed**:
```python
- authenticate(platform, user_id, credentials) -> bool
- refresh_all_tokens() -> Dict[str, bool]
- get_auth_status() -> Dict
- is_any_platform_authenticated() -> bool
- logout_all() -> Dict
- handle_auth_error(platform, error) -> bool
```

---

## Implementation Roadmap

### Phase 1: Hinge MVP (2-3 weeks)
**Goal**: Functional Hinge profile aggregation

1. Build **hinge.auth_handler**
   - [ ] Phone OTP verification
   - [ ] OAuth token management
   - [ ] Session persistence
   - [ ] Token refresh

2. Build **hinge.profile_fetcher**
   - [ ] API client for /recommendations
   - [ ] Profile detail fetching
   - [ ] Pagination handling
   - [ ] Photo URL extraction

3. Build **profile_aggregator**
   - [ ] Fetch coordination
   - [ ] Normalization pipeline
   - [ ] Storage integration
   - [ ] Error handling

**Deliverable**: Working system that fetches Hinge profiles into unified database

### Phase 2: Tinder Integration (4-5 weeks)
**Goal**: Add Tinder profiles to aggregator

1. Build **tinder.auth_handler**
   - [ ] Reverse engineer auth API
   - [ ] Phone OTP + OAuth support
   - [ ] Anti-detection measures
   - [ ] Ban detection

2. Build **tinder.profile_fetcher**
   - [ ] Fetch recommendations
   - [ ] Profile detail fetching
   - [ ] Handle pagination
   - [ ] Anti-detection evasion

3. Integrate with **multi_auth_manager**

**Deliverable**: Can fetch profiles from both Hinge and Tinder

### Phase 3: League Integration (4-5 weeks)
**Goal**: Add League profiles (highest risk)

1. Build **league.auth_handler**
   - [ ] Browser automation (Playwright)
   - [ ] Email/password login
   - [ ] 2FA handling
   - [ ] Session management

2. Build **league.profile_fetcher**
   - [ ] Profile HTML parsing
   - [ ] Dynamic content handling
   - [ ] Photo downloading
   - [ ] Pagination

3. Integrate with **multi_auth_manager**

**Deliverable**: Complete multi-platform aggregator (high legal risk)

---

## Critical Knowledge Gaps to Fill

### For Hinge Integration:
- [ ] Review HingeSDK source code (ReedGraff/HingeSDK)
- [ ] Document Hinge API endpoints
- [ ] Test phone OTP flow
- [ ] Understand OAuth token lifecycle
- [ ] Profile data schema

### For Tinder Integration:
- [ ] Study existing reverse-engineered clients
- [ ] Document current API endpoints (as of early 2025)
- [ ] Understand request signing/validation
- [ ] Find current auth flow
- [ ] Test with throwaway account
- [ ] Monitor for API changes

### For League Integration:
- [ ] Analyze League website structure
- [ ] Understand JavaScript rendering
- [ ] Document anti-scraping measures
- [ ] Test Playwright integration
- [ ] Parse profile HTML structure
- [ ] Plan fallback strategies

---

## Security & Legal Considerations

### Hinge
- Medium risk (official SDK exists)
- TOS likely prohibits automated scraping
- Risk: Account ban
- Mitigation: Only use for own accounts

### Tinder
- High risk (reverse-engineered)
- Explicit TOS violation
- Active bot detection system
- Risk: Account ban + IP ban
- Risk: Potential CFAA violation for anti-bot bypass
- Mitigation: Use disposable accounts, proxies, rate limiting

### The League
- Very high risk (web scraping)
- Explicit TOS prohibition
- Career-focused users may report scraping
- Risk: Account ban + legal action
- Risk: CFAA violation
- Mitigation: Get written consent first

---

## Tools Not Built Yet - Quick Reference

| Tool | Difficulty | Time | Risk | Why Not Built |
|------|-----------|------|------|---------------|
| hinge.auth_handler | MEDIUM | 1 week | LOW | Need HingeSDK research |
| hinge.profile_fetcher | MEDIUM | 1-2 weeks | LOW | Need API documentation |
| profile_aggregator | MEDIUM | 1 week | NONE | Waiting on fetchers |
| tinder.auth_handler | VERY HIGH | 2-3 weeks | HIGH | Reverse engineering needed |
| tinder.profile_fetcher | VERY HIGH | 2-3 weeks | HIGH | Reverse engineering needed |
| league.auth_handler | VERY HIGH | 2-3 weeks | VERY HIGH | Needs Playwright, complex |
| league.profile_fetcher | VERY HIGH | 2-3 weeks | VERY HIGH | HTML scraping, fragile |
| multi_auth_manager | MEDIUM | 1 week | NONE | Waiting on auth handlers |

---

## Summary: What You Need to Do

1. **Decide your scope**:
   - Hinge only (3 more tools, 2-3 weeks, low risk)
   - Hinge + Tinder (6 more tools, 6-7 weeks, high risk)
   - All three (8 more tools, 10-12 weeks, very high risk)

2. **Start with Hinge** (lowest risk, fastest to MVP):
   - Research HingeSDK
   - Build auth handler (use phone OTP flow)
   - Build profile fetcher (parse API responses)
   - Build aggregator (coordinate fetching)

3. **Consider Tinder carefully**:
   - High complexity (reverse engineering)
   - High maintenance (API changes)
   - High legal/TOS risk
   - Need for proxies and anti-detection

4. **Avoid League unless necessary**:
   - Highest complexity (browser automation needed)
   - Highest legal risk (explicit scraping prohibition)
   - Requires Playwright (not in environment)
   - Most fragile (HTML parsing breaks on changes)

---

## Environment Requirements for Remaining Tools

### For Hinge & Tinder Integration:
```python
# Already available in environment
- httpx or urllib (HTTP client)
- json (parsing)
- re (regex)
- time (rate limiting)
- sqlite3 (already used)
```

### For League Integration (NOT AVAILABLE):
```python
# MISSING - Would need to be installed
- playwright (browser automation)
# Can use as fallback:
- selenium (also not available)
```

**Note**: League integration is blocked until Playwright can be installed.

---

## Conclusion

**You have 60% of the system built** (12 of 20 tools).

**To have a working MVP**: Need 3 more tools (Hinge integration)
**To have a complete system**: Need 8 more tools (all platforms)

**Recommended Next Step**: Build hinge.auth_handler → This is the foundation for everything else.