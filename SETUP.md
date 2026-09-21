# Dating Apps Orchestrator - Setup Guide

Getting your unified dating dashboard running locally.

## Prerequisites

- Python 3.10+
- Node.js 18+
- pip & npm
- (Optional) CUDA GPU for faster CLIP processing

## Quick Start (Without Docker)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run API server
python api.py
```

The backend will start on `http://localhost:5000`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The frontend will open at `http://localhost:3000`

## Authentication with Dating Apps

### Tinder

1. Option A - Facebook Token:
   - Log in to Tinder on web
   - Open DevTools (F12)
   - Go to Application > Cookies > tinder.com
   - Find `sid` cookie value (this is your Facebook token)
   - Pass to API in credentials: `{"facebook_token": "..."}`

2. Option B - Phone Number:
   - Use SMS-based auth
   - Pass phone number to API
   - Enter OTP when prompted

### Hinge

1. Open Hinge on web
2. Open DevTools (F12)
3. Go to Network tab
4. Perform any action (like viewing a profile)
5. Find API request headers with `Authorization: Bearer ...`
6. Copy the token
7. Pass to API: `{"session_token": "..."}`

### Match

1. Simple username/password auth
2. Pass credentials directly: `{"username": "...", "password": "..."}`

**Note:** All auth methods are passed via the `/authenticate` endpoint.

## API Workflow

### 1. Initialize Orchestrator

```bash
curl -X POST http://localhost:5000/init \
  -H "Content-Type: application/json" \
  -d '{
    "min_age": 25,
    "max_age": 40,
    "max_distance_km": 50,
    "must_not_smoke": true,
    "required_interests": ["hiking", "travel"],
    "use_clip": true
  }'
```

### 2. Authenticate Apps

```bash
curl -X POST http://localhost:5000/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "tinder": {"facebook_token": "..."},
    "hinge": {"session_token": "..."},
    "match": {"username": "...", "password": "..."}
  }'
```

### 3. Sync Data

```bash
curl -X POST http://localhost:5000/sync
```

### 4. Get Results

```bash
# Mutual matches
curl http://localhost:5000/matches/mutual

# Incoming likes
curl http://localhost:5000/matches/incoming

# Apply filters & ranking
curl -X POST http://localhost:5000/filter-and-rank \
  -H "Content-Type: application/json" \
  -d '{
    "your_interests": ["hiking", "travel"],
    "embed_photos": false
  }'

# CLIP-based search
curl -X POST http://localhost:5000/search/by-description \
  -H "Content-Type: application/json" \
  -d '{
    "description": "athletic blonde woman who loves hiking",
    "top_k": 10
  }'
```

## Implementing Actual Scrapers

The provided scrapers are stubs. You need to implement the actual API calls for each app.

### Tinder API Endpoints

```python
# Example: Get your matches
GET https://api.gotinder.com/user
Authorization: Bearer {X-Auth-Token}

GET https://api.gotinder.com/matches
Authorization: Bearer {X-Auth-Token}

GET https://api.gotinder.com/likes
Authorization: Bearer {X-Auth-Token}
```

### Hinge API

```python
# Usually REST API with session cookies/bearer tokens
GET https://hinge.co/api/users/me/matches
Authorization: Bearer {session_token}
```

### Match API

```python
# Usually OAuth or session-based
GET https://api.match.com/users/me/matches
Authorization: Bearer {access_token}
```

## CLIP Image Matching

### How It Works

1. CLIP encodes images into a 512-dimensional embedding space
2. Text descriptions are also encoded into the same space
3. Cosine similarity between embeddings indicates visual similarity
4. Higher similarity = more visually similar

### Performance Tips

- Use GPU (`device: "cuda"`) for 10x speedup
- Process photos in batches
- Cache embeddings after first run
- Adjust `similarity_threshold` (0-1) based on results

## Project Structure

```
dating-agent/
├── backend/
│   ├── models/
│   │   └── profile.py          # Unified Profile schema
│   ├── filtering/
│   │   ├── filter_engine.py    # Strict filtering logic
│   │   └── clip_matcher.py     # CLIP-based matching
│   ├── scrapers/
│   │   └── base_scraper.py     # App scrapers (stubs)
│   ├── orchestrator.py         # Main orchestrator agent
│   ├── api.py                  # Flask API
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx             # Main app component
│   │   ├── components/
│   │   │   ├── MutualMatches.tsx
│   │   │   ├── NewLikes.tsx
│   │   │   ├── FilterPanel.tsx
│   │   │   ├── ProfileCard.tsx
│   │   │   └── Dashboard.tsx
│   │   ├── App.css
│   │   └── main.tsx
│   ├── package.json
│   ├── index.html
│   ├── vite.config.ts
│   └── tailwind.config.js
│
└── config.example.yaml
```

## Troubleshooting

### CLIP not available
- Install: `pip install openai-clip torch torchvision`
- Requires significant disk space (~4GB)
- First run is slow while it downloads the model

### Photos not loading
- Ensure URLs are publicly accessible
- Some apps might block cross-origin requests
- Check browser console for CORS errors

### Sync returns no data
- Check authentication tokens are fresh
- Login to each app in browser to refresh tokens
- Some apps might have rate limits or session timeouts

### Performance is slow
- Use GPU for CLIP processing
- Reduce number of profiles to embed
- Cache results locally

## Next Steps

1. Implement actual scrapers for each dating app
2. Add real authentication handling
3. Deploy to cloud (Heroku, Railway, etc.)
4. Add notifications for new likes
5. Build mobile app version

## Contributing

This is an open project. PRs welcome for:
- Actual scraper implementations
- Better CLIP usage patterns
- Advanced filtering algorithms
- Mobile app
- Additional dating apps (Bumble, Facebook Dating, etc.)
