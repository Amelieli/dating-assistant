# How to Get the Real Firebase API Key for Hinge

## The Problem

The Firebase API key hardcoded in `hinge_auth_real.py` is outdated:
```python
FIREBASE_API_KEY = "AIzaSyDyZ4g7OnN3RjL4VqKV0mVjLyy-tlqDk20"  # OUTDATED
```

This causes the error:
```
ERROR: API key not valid. Please pass a valid API key.
```

## Solution: Extract the Real Key

### Option 1: From Hinge Mobile App (Easiest)

#### Android:
1. Download Hinge APK
2. Decompile with jadx or apktool
3. Search for "AIzaSy" in the code
4. Look for Firebase configuration

#### iOS:
1. Extract Hinge IPA
2. Look in plist files or binary
3. Search for Firebase config

### Option 2: From Hinge Web (Browser Inspection)

1. **Open Hinge Web**
   - Go to https://hinge.co/login
   - Open browser DevTools (F12)

2. **Go to Network Tab**
   - Filter by "XHR" or "Fetch"
   - Look for requests to `identitytoolkit.googleapis.com`

3. **Trigger Phone Login**
   - Enter your phone number
   - Watch network requests

4. **Find the Key**
   - Look for requests with `?key=AIzaSy...`
   - Copy the full key after `key=`

Example request you're looking for:
```
https://identitytoolkit.googleapis.com/v1/recaptchaParams?key=AIzaSy...
https://www.googleapis.com/identitytoolkit/v3/relyingparty/sendVerificationCode?key=AIzaSy...
```

5. **Copy the Key**
   - The key starts with `AIzaSy`
   - Should be 39 characters long
   - Example: `AIzaSyABCDEF1234567890abcdefghijklmnop`

### Option 3: From Network Traffic (Advanced)

1. **Setup Proxy**
   ```bash
   # Install mitmproxy
   pip install mitmproxy
   
   # Run proxy
   mitmweb
   ```

2. **Configure Phone**
   - Set phone to use proxy (localhost:8080)
   - Install mitmproxy certificate

3. **Login to Hinge**
   - Open Hinge app
   - Start login process
   - Watch mitmweb traffic

4. **Find Firebase Requests**
   - Look for `googleapis.com` requests
   - Find the `key=` parameter

## Update the Code

Once you have the real key:

1. **Edit `hinge_auth_real.py`**
   ```python
   # Line ~27
   FIREBASE_API_KEY = "AIzaSyYOUR_REAL_KEY_HERE"
   ```

2. **Also update `dating_agent/auth_handlers.py`**
   - The wrapped version also needs the key
   - Or it inherits from `hinge_auth_real.py`

3. **Test It**
   ```bash
   python3 quick_start_hinge.py
   ```

## Workaround: Use Demo Mode

If you can't get the real key, use demo mode:

```bash
python3 quick_start_hinge_demo.py
```

This creates mock profiles to test the system without authentication.

## Alternative: Manual Auth Flow

Instead of SMS, you can manually authenticate:

1. **Login to Hinge in Browser**
   - Go to https://hinge.co
   - Login normally

2. **Extract Session Token**
   - Open DevTools > Application > Cookies
   - Copy the session cookie value

3. **Use Token Directly**
   ```python
   from dating_agent.auth_handlers import HingeAuth
   
   auth = HingeAuth()
   auth.credentials = {
       'hinge_token': 'YOUR_SESSION_TOKEN_HERE',
       'user_id': 'YOUR_USER_ID'  # From cookie or API response
   }
   
   # Now you can fetch profiles without SMS auth
   ```

## Why This Happens

- **Firebase keys change**: Hinge updates their Firebase config periodically
- **Reverse-engineered**: We're using undocumented APIs
- **Rate limiting**: Firebase may block suspicious keys
- **Regional**: Different keys for different regions

## Security Note

**Never share your Firebase API key publicly!**
- It can be used to send SMS to any phone number
- Could rack up Firebase charges
- May violate Hinge's TOS

## Need Help?

If you're stuck:

1. **Use demo mode** first to test the system:
   ```bash
   python3 quick_start_hinge_demo.py
   ```

2. **Check if Hinge changed their auth flow**:
   - They may have switched from Firebase
   - May require different authentication

3. **Use browser automation** instead:
   - Selenium to login via web
   - Extract session token
   - Use token for API calls

## Updated Quick Start

With the real key, the flow works like this:

```python
from dating_agent.profile_aggregator import profile_aggregator

agg = profile_aggregator()

# Step 1: Request OTP (with real Firebase key)
result = agg.hinge_auth.request_phone_verification(
    "+1-555-123-4567",
    solve_captcha=True
)
# Real SMS sent to your phone!

# Step 2: Verify OTP
code = input("Enter SMS code: ")
verify = agg.hinge_auth.verify_phone_otp(result['otp_id'], code)

# Step 3: Sync profiles
sync = agg.run_full_sync(
    hinge_user_id=verify['user_id'],
    limit=50
)

print(f"Success! Fetched {sync['platforms']['hinge']['profiles_fetched']} profiles")
```

---

**TL;DR**: 
1. Use demo mode: `python3 quick_start_hinge_demo.py`
2. Or extract real Firebase key from Hinge web/app
3. Update `hinge_auth_real.py` line 27
4. Then `python3 quick_start_hinge.py` will work!
