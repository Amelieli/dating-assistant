#!/bin/bash
# Start the Dating Orchestrator Frontend

cd "$(dirname "$0")/frontend"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

# Start dev server
export VITE_API_URL=http://localhost:5001
npm run dev
