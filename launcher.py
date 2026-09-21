#!/usr/bin/env python3
"""
Dating Agent Launcher

Sets up the Python path and runs quick start scripts.
Usage:
    python3 launcher.py hinge
    python3 launcher.py tinder
"""

import sys
import os
from pathlib import Path

# Add the tools directory to Python path
tools_dir = Path.home() / ".code_puppy" / "plugins" / "universal_constructor"
sys.path.insert(0, str(tools_dir))

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 launcher.py [hinge|tinder]")
        print("")
        print("Or run directly:")
        print("  ./run_hinge.sh")
        print("  ./run_tinder.sh")
        sys.exit(1)
    
    choice = sys.argv[1].lower()
    
    if choice == 'hinge':
        print("Starting Hinge Profile Aggregator...\n")
        # Import and run the hinge quick start
        import subprocess
        result = subprocess.run([
            sys.executable, 
            "quick_start_hinge.py"
        ], env={**os.environ, 'PYTHONPATH': str(tools_dir)})
        sys.exit(result.returncode)
    
    elif choice == 'tinder':
        print("Starting Tinder Profile Aggregator...\n")
        # Import and run the tinder quick start
        import subprocess
        result = subprocess.run([
            sys.executable,
            "quick_start_tinder.py"
        ], env={**os.environ, 'PYTHONPATH': str(tools_dir)})
        sys.exit(result.returncode)
    
    else:
        print(f"Unknown choice: {choice}")
        print("Use 'hinge' or 'tinder'")
        sys.exit(1)

if __name__ == "__main__":
    main()
