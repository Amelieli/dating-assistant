# Quick Start Guide - Dating Orchestrator

Get up and running in 10 minutes!

## Prerequisites

- Python 3.10+ (`python --version`)
- Node.js 18+ (`node --version`)
- Git

## Installation (5 minutes)

### 1. Clone & Navigate

```bash
git clone <repo-url>
cd dating-agent
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install
```

## Running Locally (5 minutes)

### Terminal 1: Backend

```bash
cd backend
source venv/bin/activate  # If not already activated
python api.py
```

You should see:
```
WARNING in app.run("Running on http://0.0.0.0:5000")
```

### Terminal 2: Frontend

```bash
cd frontend
npm run dev
```

Browser should open to `http://localhost:3000`

## Using the App (5 minutes)

### Step 1: Initialize

On the initialization screen, set your preferences:
- Age: 25-40
- Distance: 50km
- Interests: hiking, travel, photography
- Toggle: No smoking, No drugs
- Toggle: Use CLIP photo matching

Click "Initialize Orchestrator"

### Step 2: Authenticate

Go to Settings tab and authenticate:

**For Tinder:**
1. Open Tinder in another browser tab
2. Open DevTools (F12)
3. Go to Application > Cookies > tinder.com
4. Find `sid` cookie
5. Paste in "Session Token" field

**For Hinge:**
1. Open Hinge in another browser tab
2. Open DevTools > Network
3. Click any action (like a profile)
4. Find request with `Authorization: Bearer ...`
5. Copy token and paste

**For Match:**
- Just enter username & password

### Step 3: Sync

Click the "Sync Apps" button (top-right)

Wait 30-60 seconds for data to sync from all 3 apps.

### Step 4: View Results

- **Dashboard**: Overview & quick actions
- **Mutual Matches**: Profiles you both liked (best matches on top)
- **Incoming Likes**: People who liked you
- **Filters**: Adjust preferences anytime
- **AI Search**: Type "athletic blonde woman" to find similar profiles

## Next Steps

1. **Get Auth Tokens**
   - Follow the authentication steps above
   - Keep them secure!

2. **Implement Real Scrapers** (Optional)
   - Follow `IMPLEMENTATION_GUIDE.md`
   - Replace stub methods in `backend/scrapers/`

3. **Deploy to Cloud** (Optional)
   - Use `docker-compose.yml` to containerize
   - Deploy to Heroku, Railway, Render, etc.

4. **Customize Filters** (Optional)
   - Edit filter preferences in UI
   - Add custom filter logic in `FilterEngine`

## Common Issues

### "ModuleNotFoundError: No module named 'clip'"
```bash
pip install openai-clip torch torchvision
```

### Port 5000 already in use
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Or use different port
# Edit api.py: app.run(port=5001)
```

### Frontend can't connect to backend
- Check backend is running on localhost:5000
- Check CORS is enabled in `backend/api.py`
- Check firewall isn't blocking localhost

### Photos not loading
- Some apps block cross-origin image requests
- Use a CORS proxy: https://cors-anywhere.herokuapp.com/
- Or skip `embed_photos: true` option

## Keyboard Shortcuts

- `Ctrl+C` to stop servers
- `Cmd+R` / `F5` to refresh frontend
- `Dev Tools` (F12) to debug

## File Structure

```
dating-agent/
├── backend/
│   ├── orchestrator.py      [Main logic]
│   ├── api.py              [Flask server]
│   ├── filtering/          [Smart filters]
│   ├── scrapers/           [Data fetchers]
│   ├── models/             [Data schemas]
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx        [Main UI]
│   │   └── components/    [Page components]
│   ├── package.json
│   └── vite.config.ts
├── SETUP.md               [Detailed setup]
├── ARCHITECTURE.md        [System design]
└── IMPLEMENTATION_GUIDE.md [Scraper guide]
```

## API Endpoints Quick Reference

```
GET  /health              - Health check
POST /init                - Initialize with filters
POST /authenticate        - Login to apps
POST /sync                - Fetch data from apps
GET  /stats               - Get current stats
GET  /matches/mutual      - Get mutual matches
GET  /matches/incoming    - Get incoming likes
POST /filter-and-rank     - Apply filters
POST /search/by-description - CLIP search
POST /refresh             - Check for new likes
GET  /export/mutual-matches - Export as JSON
```

## Pro Tips

1. **Don't spam APIs** - Apps rate limit. Add delays between requests.
2. **Use VPN/Proxy** - Apps might detect/ban scrapers. Rotate IPs.
3. **Keep tokens fresh** - Re-login every few hours.
4. **Cache aggressively** - Reuse embeddings for photos.
5. **Sort by match %** - Focus on compatible matches first.
6. **CLIP is optional** - Photos are slow, try without first.

## Troubleshooting

```bash
# Check backend logs
tail -f logs/orchestrator.log

# Check frontend network errors
# F12 > Console tab

# Restart everything
Ctrl+C on both terminals
# Then run again from step "Running Locally"

# Clean slate
rm -rf backend/venv frontend/node_modules .cache
# Then reinstall
```

## What's Not Implemented Yet

- **Actual scrapers** - Stub implementations only
- **Email notifications** - For new likes
- **Mobile app** - Web only
- **User authentication** - No login system
- **Database** - Everything in memory
- **Deployment guides** - Assumes local only

## Support

- See `SETUP.md` for detailed setup
- See `ARCHITECTURE.md` for design
- See `IMPLEMENTATION_GUIDE.md` for scraper code
- Check `backend/api.py` for endpoint docs

## Have Fun!

This tool puts YOU in control of your dating experience. No more terrible algos!

Good luck out there!
