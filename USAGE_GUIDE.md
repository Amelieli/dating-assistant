# How to Use the Hinge MVP

## Quick Start (5 minutes)

### Option 1: Interactive Script (Recommended)

```bash
python quick_start_hinge.py
```

This will:
1. Ask for your phone number
2. Send OTP to that number
3. Ask you to enter the code
4. Automatically fetch, store, and deduplicate profiles
5. Generate a report

### Option 2: Manual (Understand Every Step)

```python
from dating_agent.profile_aggregator import profile_aggregator

# Initialize aggregator
agg = profile_aggregator()

# Get auth handler
auth = agg.hinge_auth

# Request OTP
req = auth.request_phone_verification("+1-555-123-4567")
print(f"OTP sent: {req['message']}")

# Enter the code manually
otp_id = req['otp_id']
code = input("Enter SMS code: ")

# Verify
verify = auth.verify_phone_otp(otp_id, code)
user_id = verify['user_id']
print(f"Authenticated as {user_id}")

# Fetch and store profiles
result = agg.run_full_sync(user_id, limit=100)
print(f"Profiles fetched: {result['platforms']['hinge']['profiles_fetched']}")

# Export report
agg.export_sync_report("my_report.json")
```

### Option 3: Test Without Real Auth (No Phone Required)

```python
from dating_agent.profile_store import profile_store
from dating_agent.deduplicator import deduplicator

# Create mock profile
store = profile_store()
mock = {
    'id': 'test_001',
    'name': 'Alice Smith',
    'age': 28,
    'bio': 'Test profile',
    'photo_urls': []
}

# Store it
profile_id = store.add_profile('hinge', 'test_user', mock)
print(f"Stored: {profile_id}")

# Query it
profiles = store.get_all_profiles()
print(f"Total profiles: {len(profiles)}")

# Check deduplication
dedup = deduplicator()
duplicates = dedup.find_all_duplicates(profiles)
print(f"Duplicates found: {len(duplicates)}")
```

---

## After Running the Sync

### 1. Check the Database

```python
from dating_agent.profile_store import profile_store

store = profile_store()

# Get all profiles
profiles = store.get_all_profiles()
print(f"Total profiles: {len(profiles)}")

# Search for specific profile
alice = store.search_profiles("Alice", field="name")

# Get statistics
stats = store.get_stats()
print(f"Total: {stats['total_profiles']}")
print(f"Duplicates: {stats['duplicate_pairs']}")
```

### 2. Check the Reports

```bash
# View the sync report
cat aggregation_report.json | jq .

# View auth log
cat hinge_auth_log.json | jq .

# View fetch log
cat hinge_fetch_log.json | jq .

# View error log
cat dating_agent_errors.log | jq .
```

### 3. Access Downloaded Photos

```bash
# List all downloaded photos
ls dating_agent_photos/

# View photo metadata
cat dating_agent_photos/photo_log.json | jq .

# Count photos
ls dating_agent_photos/*.jpg | wc -l
```

---

## Configuration

### View Current Settings

```python
from dating_agent.config_manager import ConfigManager

config = ConfigManager()

# Get Hinge rate limit
rate_limit = config.get("hinge.rate_limit_per_second")
print(f"Hinge rate limit: {rate_limit} req/sec")

# Get all Hinge config
hinge_config = config.get_platform_config("hinge")
print(f"Hinge config: {hinge_config}")
```

### Adjust Settings

```python
from dating_agent.config_manager import ConfigManager

config = ConfigManager()

# Slower rate limiting (safer)
config.set("hinge.rate_limit_per_second", 0.5)

# Faster rate limiting (risky)
config.set("hinge.rate_limit_per_second", 2.0)

# Longer timeout
config.set("hinge.timeout", 60)

# More retries
config.set("hinge.retry_attempts", 5)
```

---

## Monitoring & Debugging

### Check Authentication Status

```python
from dating_agent.profile_aggregator import profile_aggregator

agg = profile_aggregator()

# See authenticated users
status = agg.get_hinge_auth_status()
print(f"Authenticated users: {status['authenticated_users']}")
print(f"Recent actions: {status['recent_auth_actions']}")
```

### Check Sync Status

```python
# Get aggregator status
status = agg.get_sync_status()
print(f"Total syncs: {status['total_syncs_logged']}")
print(f"Recent syncs: {status['recent_syncs']}")
```

### Check Errors

```python
from dating_agent.error_handler import ErrorHandler

eh = ErrorHandler()

# Get error stats
stats = eh.get_error_stats()
print(f"Total errors: {stats['total_errors']}")
print(f"By category: {stats['by_category']}")

# Get specific errors
auth_errors = eh.get_errors_by_category("authentication")
print(f"Auth errors: {len(auth_errors)}")

# Export error report
eh.export_error_report("errors.json")
```

### Check Performance Metrics

```python
from dating_agent.metrics_collector import MetricsCollector

mc = MetricsCollector()

# Get summary
summary = mc.get_summary()
print(f"Total requests: {summary['total_requests']}")

# Get platform health
health = mc.get_platform_health("hinge")
print(f"Hinge success rate: {health['success_rate']}%")

# Get trends
trends = mc.get_trends("success_rate", window_hours=24)
print(f"Last 24h trends: {trends['by_platform']}")

# Export metrics
mc.export_metrics("metrics.json")
```

---

## Common Tasks

### Task 1: Fetch More Profiles

```python
agg = profile_aggregator()
auth = agg.hinge_auth

# Authenticate first
req = auth.request_phone_verification("+1-555-123-4567")
verify = auth.verify_phone_otp(req['otp_id'], "123456")
user_id = verify['user_id']

# Fetch more
result = agg.run_full_sync(
    hinge_user_id=user_id,
    limit=500,  # Get 500 instead of 100
    find_duplicates=True,
    download_photos=True
)
```

### Task 2: Find Duplicates Without Fetching

```python
from dating_agent.profile_store import profile_store
from dating_agent.deduplicator import Deduplicator

store = profile_store()
dedup = Deduplicator()

# Get existing profiles
profiles = store.get_all_profiles()

# Find duplicates
duplicates = dedup.find_all_duplicates(profiles, min_score=0.8)

# Display results
for dup in duplicates:
    print(f"Match: {dup['profile1_name']} <-> {dup['profile2_name']}")
    print(f"Score: {dup['match_score']}")
    print()

# Store in database
for dup in duplicates:
    store.mark_duplicate(
        dup['profile1_id'],
        dup['profile2_id'],
        dup['match_score'],
        "Duplicate detected"
    )
```

### Task 3: Export All Data

```python
import json
from dating_agent.profile_store import profile_store

store = profile_store()

# Get all profiles
profiles = store.get_all_profiles()

# Export to JSON
with open("all_profiles.json", 'w') as f:
    json.dump(profiles, f, indent=2)

# Convert to CSV (manual)
import csv
with open("all_profiles.csv", 'w', newline='') as f:
    if profiles:
        writer = csv.DictWriter(f, fieldnames=profiles[0].keys())
        writer.writeheader()
        writer.writerows(profiles)
```

### Task 4: Search Profiles

```python
from dating_agent.profile_store import profile_store

store = profile_store()

# Search by name
results = store.search_profiles("alice", field="name")
print(f"Found {len(results)} profiles with 'alice' in name")

# Get profiles by location
ny_profiles = store.search_profiles("New York", field="location")
print(f"Found {len(ny_profiles)} profiles in New York")

# Get profiles by bio
outdoor = store.search_profiles("hiking", field="bio")
print(f"Found {len(outdoor)} profiles mentioning hiking")
```

### Task 5: Multiple Accounts

```python
agg = profile_aggregator()
auth = agg.hinge_auth

# Authenticate first user
req1 = auth.request_phone_verification("+1-555-111-1111")
v1 = auth.verify_phone_otp(req1['otp_id'], "123456")
user1 = v1['user_id']

# Authenticate second user
req2 = auth.request_phone_verification("+1-555-222-2222")
v2 = auth.verify_phone_otp(req2['otp_id'], "123456")
user2 = v2['user_id']

# Sync both users
r1 = agg.run_full_sync(user1, limit=100)
r2 = agg.run_full_sync(user2, limit=100)

# Check combined database
store = agg.store
stats = store.get_stats()
print(f"Total profiles across users: {stats['total_profiles']}")
```

---

## Troubleshooting

### Issue: "OTP timeout"
```
Error: OTP expired after 300 seconds
```
**Solution**: OTP codes expire after 5 minutes. Request a new one:
```python
req = auth.request_phone_verification(phone)
```

### Issue: "Rate limited"
```
Error: Rate limit hit - waiting 60 seconds
```
**Solution**: System automatically backs off. Wait. Or adjust in config:
```python
config.set("hinge.rate_limit_per_second", 1.0)  # More conservative
```

### Issue: "User not authenticated"
```
Error: User {user_id} is not authenticated
```
**Solution**: Run authentication first before fetching

### Issue: "No photos downloaded"
```
Connection timeout downloading photos
```
**Solution**: Network issue. System will retry. Check internet connection.

### Issue: "Database locked"
```
sqlite3.OperationalError: database is locked
```
**Solution**: Another process is using the database. Close it.

---

## Performance Tuning

### Faster Syncs (More Aggressive)

```python
agg = profile_aggregator()
config = agg.config

# Increase rate limit (risky - may trigger bans)
config.set("hinge.rate_limit_per_second", 2.0)

# Run sync
result = agg.run_full_sync(user_id, limit=500)
```

### Slower Syncs (Safer)

```python
config.set("hinge.rate_limit_per_second", 0.5)

# Run sync (takes longer but safer)
result = agg.run_full_sync(user_id, limit=100)
```

### Disable Photo Downloads (Faster)

```python
# Skip photo downloads - 10x faster
result = agg.run_full_sync(user_id, download_photos=False)
```

### Skip Deduplication (Faster)

```python
# Skip duplicate detection
result = agg.run_full_sync(user_id, find_duplicates=False)
```

---

## Next Steps

1. **Run the quick start**: `python quick_start_hinge.py`
2. **Check the database**: `ls *.db *.json`
3. **Query some profiles**: Use the examples above
4. **Build Tinder integration**: See next section
5. **Add League integration**: (Optional, harder)

---

## For More Help

- **HINGE_MVP_GUIDE.md** - Detailed walkthrough
- **QUICK_REFERENCE.txt** - Quick lookup
- **README_IMPLEMENTATION_STATUS.md** - Full technical details
- Check `dating_agent_errors.log` for detailed error messages
- Each tool has a `__main__` block you can run directly

---

**You're ready to use it now! Run `python quick_start_hinge.py` to get started.**