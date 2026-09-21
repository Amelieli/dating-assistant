#  Dating Apps Orchestrator Agent

A smart agent that unifies Tinder, Hinge, and Match with AI-powered filtering, mutual match detection, and intelligent profile recommendations.

## Features

 **Mutual Match Detection** - Shows only profiles that liked you AND you liked back
 **New Likes Display** - See all incoming likes across all 3 apps in one place
 **Smart Filtering** - Age, location, interests with strict enforcement
 **CLIP Image Matching** - Find visually similar profiles to your preferences
 **Unified Dashboard** - Single UI for all dating app data

## Architecture

```
├── backend/
│   ├── orchestrator.py      # Main agent orchestrating all 3 apps
│   ├── scrapers/
│   │   ├── tinder.py
│   │   ├── hinge.py
│   │   └── match.py
│   ├── filtering/
│   │   ├── filter_engine.py # Strict filtering logic
│   │   └── clip_matcher.py  # CLIP-based image similarity
│   ├── models/
│   │   └── profile.py       # Unified profile schema
│   ├── api.py               # Flask API for frontend
│   └── requirements.txt
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── MutualMatches.tsx
│   │   │   ├── NewLikes.tsx
│   │   │   ├── FilterPanel.tsx
│   │   │   └── ProfileCard.tsx
│   │   └── hooks/
│   │       └── useOrchestrator.ts
│   └── vite.config.ts
└── docker-compose.yml       # Local dev setup
```

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
python api.py

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

## Configuration

See `config.example.yaml` for credentials and filter settings.
