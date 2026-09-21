# Installation Guide - Dating Apps Orchestrator

Your backend is already running! Now let's get the frontend going.

## Prerequisites

### Python (Already Done!)
- [x] Python 3.10+ installed
- [x] Backend dependencies installed
- [x] Backend running on http://localhost:5001

### Node.js (NEEDED)
You need to install Node.js to run the frontend.

## Install Node.js

### Option 1: Using Homebrew (Recommended for Mac)

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js
brew install node
```

### Option 2: Download Installer
Go to https://nodejs.org/ and download the LTS version.

### Verify Installation

```bash
node --version  # Should show v18+
npm --version   # Should show 9+
```

## Setup Frontend

Once Node.js is installed:

```bash
# Navigate to frontend
cd ~/dating-agent/frontend

# Install dependencies (this will take 2-3 minutes)
npm install

# Start dev server
npm run dev
```

The frontend should open automatically at http://localhost:5173 or http://localhost:5174

## Backend Status

Your backend is already running!

```
API Server: http://localhost:5001
Health Check: curl http://localhost:5001/health
```

If you need to restart the backend:

```bash
cd ~/dating-agent
bash start_backend.sh
```

## Convenient Startup

After setup, you can use these scripts:

### Terminal 1 - Backend
```bash
cd ~/dating-agent
bash start_backend.sh
```

### Terminal 2 - Frontend
```bash
cd ~/dating-agent
bash start_frontend.sh
```

## Troubleshooting

### Node.js command not found after install
Try closing and reopening your terminal, or:
```bash
source ~/.zshrc
node --version
```

### Port 5173 already in use
Vite will automatically use the next available port (5174, 5175, etc).

### Still getting errors?
Run these individually:

```bash
# Backend in separate terminal
cd ~/dating-agent/backend
source venv/bin/activate
python api.py

# Frontend in another terminal
cd ~/dating-agent/frontend
npm install
npm run dev
```

## What's Next?

1. Install Node.js (see above)
2. Run: `cd ~/dating-agent/frontend && npm install`
3. Run: `npm run dev`
4. Open http://localhost:5173 in your browser
5. See the beautiful dashboard!

Good luck!
