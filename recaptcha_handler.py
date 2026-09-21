"""
reCAPTCHA Handler for Hinge Authentication

Hinge uses Firebase reCAPTCHA for phone verification.
This module provides a way to solve reCAPTCHA challenges.
"""

import subprocess
import webbrowser
from pathlib import Path
from typing import Optional


class ReCaptchaHandler:
    """Handles reCAPTCHA solving for Hinge authentication."""
    
    def __init__(self, port: int = 5000):
        self.port = port
        self.token = None
    
    def get_token(self, site_key: str) -> str:
        """
        Get reCAPTCHA token by launching browser.
        
        This opens a simple HTML page where the user solves the reCAPTCHA.
        The token is then captured and returned.
        
        Args:
            site_key: Firebase reCAPTCHA site key
            
        Returns:
            reCAPTCHA token string
        """
        print(f"\n{'='*60}")
        print("RECAPTCHA VERIFICATION REQUIRED")
        print(f"{'='*60}")
        print("\nA browser window will open.")
        print("Please solve the reCAPTCHA challenge.")
        print("After completion, the token will be captured automatically.\n")
        
        # Create simple HTML page for reCAPTCHA
        html_content = self._generate_recaptcha_html(site_key)
        html_file = Path("recaptcha_temp.html")
        
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        # Open in browser
        webbrowser.open(f"file://{html_file.absolute()}")
        
        # For now, ask user to manually enter token
        print("After solving reCAPTCHA, the token will be displayed.")
        token = input("\nEnter the reCAPTCHA token: ").strip()
        
        # Clean up
        try:
            html_file.unlink()
        except:
            pass
        
        return token
    
    def _generate_recaptcha_html(self, site_key: str) -> str:
        """Generate HTML page with reCAPTCHA widget."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>reCAPTCHA Verification</title>
    <script src="https://www.google.com/recaptcha/api.js" async defer></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            text-align: center;
        }}
        h1 {{
            color: #333;
            margin-bottom: 20px;
        }}
        .instructions {{
            color: #666;
            margin-bottom: 30px;
            line-height: 1.6;
        }}
        #token {{
            width: 100%;
            padding: 10px;
            margin-top: 20px;
            border: 2px solid #667eea;
            border-radius: 5px;
            font-family: monospace;
            background: #f5f5f5;
        }}
        .success {{
            color: #28a745;
            font-weight: bold;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Hinge reCAPTCHA Verification</h1>
        <p class="instructions">
            Please complete the reCAPTCHA challenge below.<br>
            After completion, copy the token and paste it into the terminal.
        </p>
        
        <div class="g-recaptcha" 
             data-sitekey="{site_key}"
             data-callback="onCaptchaSuccess"></div>
        
        <div id="result"></div>
        <input type="text" id="token" readonly placeholder="Token will appear here...">
    </div>
    
    <script>
        function onCaptchaSuccess(token) {{
            document.getElementById('token').value = token;
            document.getElementById('result').innerHTML = 
                '<p class="success">Success! Copy the token above and paste it into the terminal.</p>';
            
            // Try to copy to clipboard
            document.getElementById('token').select();
            try {{
                document.execCommand('copy');
                console.log('Token copied to clipboard');
            }} catch(err) {{
                console.log('Could not copy token');
            }}
        }}
    </script>
</body>
</html>
"""
    
    def get_token_manual(self, site_key: str) -> str:
        """
        Get token by asking user to manually solve via web browser.
        
        Simpler fallback method.
        """
        url = f"https://www.google.com/recaptcha/api/fallback?k={site_key}"
        print(f"\nPlease visit this URL and solve the reCAPTCHA:")
        print(f"{url}\n")
        print("After solving, you'll receive a token.")
        
        token = input("Enter the token: ").strip()
        return token


def recaptcha_handler(port: int = 5000):
    """Factory function."""
    return ReCaptchaHandler(port=port)


if __name__ == "__main__":
    handler = ReCaptchaHandler()
    
    # Test with dummy site key
    test_key = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"  # Google test key
    print("Testing reCAPTCHA handler...")
    print(f"Using test site key: {test_key}")
    
    # This would open browser in real use
    # token = handler.get_token(test_key)
    # print(f"Got token: {token[:50]}...")
