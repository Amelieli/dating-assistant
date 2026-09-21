#!/bin/bash
# Start the Dating Orchestrator Backend

cd "$(dirname "$0")/backend"

# Activate virtual environment
source venv/bin/activate

# Run Flask app
python api.py
