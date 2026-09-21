"""
Manual reCAPTCHA Solver

Opens a browser window for user to solve reCAPTCHA,
then extracts the token for API use.

This is the safest method - no external services, no automation detection.
"""

import time
import webbrowser
from typing import Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ManualRecaptchaSolver:
    """
    Manual reCAPTCHA solver using browser.
    
    Opens a simple HTML page where user can solve reCAPTCHA,
    then copies the token for use in authentication.
    """
    
    RECAPTCHA_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Solve reCAPTCHA</title>
    <script src="https://www.google.com/recaptcha/api.js" async defer></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-top: 0;
        }
        .instructions {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #2196F3;
        }
        .token-display {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            font-family: monospace;
            word-break: break-all;
            display: none;
        }
        .token-display.visible {
            display: block;
        }
        button {
            background: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
        }
        button:hover {
            background: #45a049;
        }
        .status {
            margin-top: 20px;
            padding: 10px;
            border-radius: 5px;
        }
        .status.success {
            background: #dff0d8;
            color: #3c763d;
        }
        .status.waiting {
            background: #fcf8e3;
            color: #8a6d3b;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Solve reCAPTCHA for {platform}</h1>
        
        <div class="instructions">
            <strong>Instructions:</strong>
            <ol>
                <li>Solve the reCAPTCHA below</li>
                <li>The token will appear automatically</li>
                <li>Copy the token and return to the terminal</li>
            </ol>
        </div>
        
        <div class="g-recaptcha" 
             data-sitekey="{site_key}"
             data-callback="onRecaptchaSuccess"></div>
        
        <div id="status" class="status waiting">
            Waiting for reCAPTCHA...
        </div>
        
        <div id="tokenDisplay" class="token-display">
            <strong>Token:</strong><br>
            <span id="tokenValue"></span>
        </div>
        
        <button onclick="copyToken()" id="copyBtn" style="display:none;">
            Copy Token
        </button>
    </div>
    
    <script>
        let recaptchaToken = null;
        
        function onRecaptchaSuccess(token) {
            recaptchaToken = token;
            
            // Show token
            document.getElementById('tokenValue').textContent = token;
            document.getElementById('tokenDisplay').classList.add('visible');
            document.getElementById('copyBtn').style.display = 'inline-block';
            
            // Update status
            const status = document.getElementById('status');
            status.className = 'status success';
            status.textContent = 'reCAPTCHA solved! Copy the token and return to terminal.';
            
            // Save to file for programmatic access
            saveTokenToFile(token);
        }
        
        function copyToken() {
            const tokenText = document.getElementById('tokenValue').textContent;
            navigator.clipboard.writeText(tokenText).then(() => {
                alert('Token copied to clipboard!');
            });
        }
        
        function saveTokenToFile(token) {
            // Use localStorage as fallback
            localStorage.setItem('recaptcha_token', token);
            console.log('Token saved to localStorage');
        }
    </script>
</body>
</html>
"""
    
    def __init__(self, site_key: str, platform: str = "Dating App"):
        self.site_key = site_key
        self.platform = platform
        self.token = None
    
    def solve(self) -> Optional[str]:
        """
        Open browser for user to solve reCAPTCHA manually.
        
        Returns:
            reCAPTCHA token, or None if user cancelled
        """
        logger.info(f"Opening browser for {self.platform} reCAPTCHA...")
        
        # Create HTML file
        html_content = self.RECAPTCHA_HTML_TEMPLATE.format(
            platform=self.platform,
            site_key=self.site_key
        )
        
        html_file = Path("recaptcha_solver.html")
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        # Open in browser
        file_url = f"file://{html_file.absolute()}"
        webbrowser.open(file_url)
        
        print("\n" + "=" * 70)
        print(f"RECAPTCHA SOLVER - {self.platform}")
        print("=" * 70)
        print("\nA browser window has been opened.")
        print("Please:")
        print("  1. Solve the reCAPTCHA")
        print("  2. Copy the token that appears")
        print("  3. Paste it below")
        print("\n" + "=" * 70)
        
        # Wait for user to paste token
        try:
            token = input("\nPaste the reCAPTCHA token here (or press Enter to skip): ").strip()
            
            if token:
                logger.info("Token received!")
                self.token = token
                return token
            else:
                logger.warning("No token provided, skipping reCAPTCHA")
                return None
        
        except KeyboardInterrupt:
            logger.warning("reCAPTCHA solving cancelled")
            return None
        
        finally:
            # Cleanup HTML file
            try:
                html_file.unlink()
            except:
                pass
    
    def get_token(self) -> Optional[str]:
        """Get the solved token."""
        return self.token


def solve_recaptcha_interactive(site_key: str, platform: str = "Dating App") -> Optional[str]:
    """
    Convenience function to solve reCAPTCHA interactively.
    
    Args:
        site_key: reCAPTCHA site key
        platform: Platform name for display
    
    Returns:
        reCAPTCHA token or None
    """
    solver = ManualRecaptchaSolver(site_key, platform)
    return solver.solve()
