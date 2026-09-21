"""
Authentication handlers for dating apps.
Wraps the real authentication implementations.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Add parent directory to path to import the real auth modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from hinge_auth_real import HingeAuthReal
from tinder_auth_real import TinderAuthReal
from dating_agent.recaptcha_solver import solve_recaptcha_interactive

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HingeAuth(HingeAuthReal):
    """Hinge authentication handler - extends the real implementation."""
    
    def __init__(self, creds_file: str = "hinge_creds.json"):
        super().__init__(creds_file)
        self._pending_phone = None
        self._pending_otp_id = None
        self._pending_session_info = None
        self._recaptcha_token = None
    
    def request_phone_verification(self, phone: str, solve_captcha: bool = True) -> Dict[str, Any]:
        """
        Request phone verification (step 1 of 2).
        Sends OTP code to phone number.
        
        Args:
            phone: Phone number in format +1-555-123-4567
            solve_captcha: If True, opens browser for user to solve reCAPTCHA
        
        Returns:
            Dict with 'status', 'message', and 'otp_id'
        """
        import uuid
        import requests
        
        try:
            logger.info(f"Hinge: Requesting verification for {phone}")
            
            # Store phone for later verification
            self._pending_phone = phone
            self._pending_otp_id = str(uuid.uuid4())
            
            # Step 1: Register installation
            install_id = str(uuid.uuid4()).lower()
            logger.info("Hinge: Registering installation...")
            
            resp = requests.post(
                f"{self.API_BASE}/identity/install",
                headers={
                    "X-App-Version": self.HINGE_APP_VERSION,
                    "X-Device-Platform": self.HINGE_DEVICE_PLATFORM,
                },
                json={"installId": install_id},
                timeout=10
            )
            
            if not resp.ok:
                logger.warning(f"Hinge: Install registration returned {resp.status_code}")
            
            # Step 2: Get reCAPTCHA site key
            logger.info("Hinge: Getting reCAPTCHA parameters...")
            resp = requests.get(
                self.RECAPTCHA_API,
                params={"alt": "json", "key": self.FIREBASE_API_KEY},
                timeout=10
            )
            
            if resp.ok:
                recaptcha_params = resp.json()
                site_key = recaptcha_params.get("recaptchaSiteKey")
                logger.info(f"Hinge: Got reCAPTCHA site key")
                
                # Step 3: Solve reCAPTCHA (if enabled)
                if solve_captcha and site_key:
                    logger.info("Hinge: Solving reCAPTCHA...")
                    self._recaptcha_token = solve_recaptcha_interactive(site_key, "Hinge")
                    
                    if not self._recaptcha_token:
                        logger.warning("Hinge: No reCAPTCHA token provided, using mock")
                        self._recaptcha_token = "mock_token"
                else:
                    logger.info("Hinge: Using mock reCAPTCHA token")
                    self._recaptcha_token = "mock_token"
            else:
                logger.warning(f"Hinge: reCAPTCHA fetch failed ({resp.status_code})")
                self._recaptcha_token = "mock_token"
            
            # Step 4: Send OTP
            logger.info(f"Hinge: Sending OTP to {phone}...")
            resp = requests.post(
                self.SEND_OTP_API,
                json={
                    "phoneNumber": phone,
                    "recaptchaToken": self._recaptcha_token,
                },
                params={"key": self.FIREBASE_API_KEY},
                timeout=10
            )
            
            if resp.ok:
                sms_data = resp.json()
                self._pending_session_info = sms_data.get("sessionInfo")
                logger.info("Hinge: OTP sent successfully!")
                
                return {
                    'status': 'success',
                    'message': f'OTP sent to {phone}',
                    'otp_id': self._pending_otp_id
                }
            else:
                logger.error(f"Hinge: OTP send failed ({resp.status_code}): {resp.text}")
                return {
                    'status': 'error',
                    'message': f'Failed to send OTP: {resp.status_code}',
                    'otp_id': self._pending_otp_id  # Return ID anyway for testing
                }
        
        except Exception as e:
            logger.error(f"Hinge: Request verification failed - {e}")
            return {
                'status': 'error',
                'message': str(e),
                'otp_id': None
            }
    
    def verify_phone_otp(self, otp_id: str, code: str) -> Dict[str, Any]:
        """
        Verify OTP code (step 2 of 2).
        Completes authentication and returns user ID.
        
        Returns:
            Dict with 'status', 'user_id', and 'session_id'
        """
        import requests
        
        try:
            if otp_id != self._pending_otp_id:
                return {
                    'status': 'error',
                    'message': 'Invalid OTP ID',
                    'user_id': None,
                    'session_id': None
                }
            
            if not self._pending_phone:
                return {
                    'status': 'error',
                    'message': 'No pending phone verification',
                    'user_id': None,
                    'session_id': None
                }
            
            logger.info(f"Hinge: Verifying OTP code...")
            
            # Step 1: Verify OTP with Firebase
            resp = requests.post(
                self.VERIFY_OTP_API,
                json={
                    "sessionInfo": self._pending_session_info or "mock_session",
                    "code": code,
                },
                params={"key": self.FIREBASE_API_KEY},
                timeout=10
            )
            
            if not resp.ok:
                logger.error(f"Hinge: OTP verification failed ({resp.status_code}): {resp.text}")
                return {
                    'status': 'error',
                    'message': f'Invalid OTP code or expired session',
                    'user_id': None,
                    'session_id': None
                }
            
            # Get Firebase token
            sms_jwt = resp.json().get("idToken")
            logger.info("Hinge: OTP verified with Firebase")
            
            # Step 2: Exchange for Hinge token
            install_id = str(self._pending_otp_id)  # Reuse for install ID
            
            resp = requests.post(
                f"{self.API_BASE}/auth/sms",
                headers={
                    "X-App-Version": self.HINGE_APP_VERSION,
                    "X-Device-Platform": self.HINGE_DEVICE_PLATFORM,
                },
                json={
                    "installId": install_id,
                    "token": sms_jwt,
                },
                timeout=10
            )
            
            if not resp.ok:
                logger.error(f"Hinge: Token exchange failed ({resp.status_code}): {resp.text}")
                return {
                    'status': 'error',
                    'message': f'Failed to exchange token with Hinge',
                    'user_id': None,
                    'session_id': None
                }
            
            # Success!
            token_data = resp.json()
            hinge_token = token_data.get("token")
            user_id = token_data.get("identityId")
            
            logger.info(f"Hinge: Authentication successful! User ID: {user_id}")
            
            # Save credentials
            credentials = {
                "phone_number": self._pending_phone,
                "hinge_token": hinge_token,
                "user_id": user_id,
                "install_id": install_id,
                "authenticated_at": __import__('datetime').datetime.now().isoformat(),
            }
            
            self._save_credentials(credentials)
            self.credentials = credentials
            
            return {
                'status': 'success',
                'user_id': user_id,
                'session_id': hinge_token,
            }
        
        except Exception as e:
            logger.error(f"Hinge: Verification error - {e}")
            return {
                'status': 'error',
                'message': str(e),
                'user_id': None,
                'session_id': None
            }


class TinderAuth(TinderAuthReal):
    """Tinder authentication handler - extends the real implementation."""
    
    def __init__(self, creds_file: str = "tinder_creds.json"):
        super().__init__(creds_file)
        self._pending_phone = None
        self._pending_otp_id = None
        self._recaptcha_token = None
    
    def request_phone_verification(self, phone: str, solve_captcha: bool = True) -> Dict[str, Any]:
        """
        Request phone verification (step 1 of 2).
        Sends OTP code to phone number.
        
        Args:
            phone: Phone number in format +1-555-123-4567
            solve_captcha: If True, opens browser for user to solve reCAPTCHA
        
        Returns:
            Dict with 'status', 'message', and 'otp_id'
        """
        import uuid
        
        try:
            logger.info(f"Tinder: Requesting verification for {phone}")
            
            # Store phone for later verification
            self._pending_phone = phone
            self._pending_otp_id = str(uuid.uuid4())
            
            # Tinder's auth flow is more complex and less documented
            # For now, we'll use the simplified flow from the real auth handler
            logger.warning("Tinder: Using simplified auth flow (real SMS not sent yet)")
            logger.info("Tinder: You'll need to manually trigger SMS via Tinder app or web")
            
            return {
                'status': 'success',
                'message': f'Ready to verify {phone} (trigger SMS manually)',
                'otp_id': self._pending_otp_id
            }
        except Exception as e:
            logger.error(f"Tinder: Request verification failed - {e}")
            return {
                'status': 'error',
                'message': str(e),
                'otp_id': None
            }
    
    def verify_phone_otp(self, otp_id: str, code: str) -> Dict[str, Any]:
        """
        Verify OTP code (step 2 of 2).
        Completes authentication and returns user ID.
        
        Returns:
            Dict with 'status', 'user_id', and 'device_id'
        """
        try:
            if otp_id != self._pending_otp_id:
                return {
                    'status': 'error',
                    'message': 'Invalid OTP ID',
                    'user_id': None,
                    'device_id': None
                }
            
            if not self._pending_phone:
                return {
                    'status': 'error',
                    'message': 'No pending phone verification',
                    'user_id': None,
                    'device_id': None
                }
            
            # Call the real authenticate method
            result = self.authenticate_with_phone(self._pending_phone)
            
            if result['status'] == 'success':
                return {
                    'status': 'success',
                    'user_id': result['user_id'],
                    'device_id': self.device_id,
                }
            else:
                return {
                    'status': 'error',
                    'message': result.get('message', 'Authentication failed'),
                    'user_id': None,
                    'device_id': None
                }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'user_id': None,
                'device_id': None
            }
