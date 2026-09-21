"""
Flask API for the Dating App Orchestrator.
Exposes endpoints for the React frontend.
"""
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from orchestrator import DatingAppOrchestrator
from filtering.filter_engine import FilterConfig
from models.profile import Profile, MatchStatus, AppSource
from ranking import RankingConfig, rank_profiles, get_top_matches
import logging
import json
from typing import Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Initialize orchestrator (will be configured via API)
orchestrator: Optional[DatingAppOrchestrator] = None


@app.route("/", methods=["GET"])
def index():
    """Serve the UI."""
    return render_template('index.html')


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "dating-orchestrator"})


@app.route("/init", methods=["POST"])
def init_orchestrator():
    """
    Initialize the orchestrator with filter config.
    
    Request body:
    {
        "min_age": 25,
        "max_age": 40,
        "max_distance_km": 50,
        "must_not_smoke": true,
        "must_not_use_drugs": true,
        "required_interests": ["hiking", "travel"],
        "use_clip": true
    }
    """
    global orchestrator
    
    try:
        config_data = request.json
        
        # Extract filter config
        filter_config = FilterConfig(
            min_age=config_data.get("min_age", 18),
            max_age=config_data.get("max_age", 100),
            max_distance_km=config_data.get("max_distance_km", 50),
            must_not_smoke=config_data.get("must_not_smoke", True),
            must_not_use_drugs=config_data.get("must_not_use_drugs", True),
            required_interests=config_data.get("required_interests"),
            min_interest_overlap=config_data.get("min_interest_overlap", 1),
            acceptable_religions=config_data.get("acceptable_religions"),
            acceptable_politics=config_data.get("acceptable_politics"),
        )
        
        use_clip = config_data.get("use_clip", True)
        orchestrator = DatingAppOrchestrator(filter_config, use_clip=use_clip)
        
        return jsonify({
            "status": "initialized",
            "config": config_data
        })
    except Exception as e:
        logger.error(f"Init failed: {e}")
        return jsonify({"error": str(e)}), 400


@app.route("/hydrate", methods=["POST"])
def hydrate_profiles():
    """
    Hydrate the orchestrator with pre-fetched profile data.
    
    Request body:
    {
        "profiles": [
            {
                "app_id": "...",
                "app_source": "tinder",
                "name": "...",
                "age": 25,
                ...
            }
        ]
    }
    """
    global orchestrator
    
    # Auto-initialize if needed
    if not orchestrator:
        filter_config = FilterConfig(
            min_age=18,
            max_age=100,
            max_distance_km=100,
            must_not_smoke=False,
            must_not_use_drugs=False,
        )
        orchestrator = DatingAppOrchestrator(filter_config, use_clip=False)
    
    try:
        data = request.json
        profiles_data = data.get("profiles", [])
        
        added_count = 0
        for p in profiles_data:
            try:
                # Convert to Profile object
                app_source = AppSource(p.get("app_source", "tinder"))
                match_status = MatchStatus(p.get("match_status", "incoming"))
                
                profile = Profile(
                    app_id=p.get("app_id", ""),
                    app_source=app_source,
                    name=p.get("name", "Unknown"),
                    age=p.get("age", 30),
                    city=p.get("city", ""),
                    state=p.get("state", ""),
                    country=p.get("country", "US"),
                    bio=p.get("bio", ""),
                    interests=p.get("interests", []),
                    occupation=p.get("occupation", ""),
                    education=p.get("education", ""),
                    photo_urls=p.get("photo_urls", []),
                    match_status=match_status,
                    verified=p.get("verified", False),
                    distance_km=p.get("distance_km"),
                    ethnicity=p.get("ethnicity"),
                    height_cm=p.get("height_cm"),
                    smokes=p.get("smokes"),
                    drinks=p.get("drinks"),
                )
                
                # Add to orchestrator storage
                key = (profile.app_id, profile.app_source)
                orchestrator.all_profiles[key] = profile
                
                if match_status == MatchStatus.INCOMING:
                    orchestrator.incoming_likes[key] = profile
                elif match_status == MatchStatus.MUTUAL:
                    orchestrator.your_likes[key] = profile
                
                added_count += 1
            except Exception as e:
                logger.warning(f"Failed to add profile: {e}")
                continue
        
        return jsonify({
            "status": "hydrated",
            "profiles_added": added_count,
            "total_profiles": len(orchestrator.all_profiles),
        })
    except Exception as e:
        logger.error(f"Hydrate failed: {e}")
        return jsonify({"error": str(e)}), 400


@app.route("/authenticate", methods=["POST"])
def authenticate():
    """
    Authenticate with all dating apps.
    
    Request body:
    {
        "tinder": {"facebook_token": "..."},
        "hinge": {"session_token": "..."},
        "match": {"username": "...", "password": "..."}
    }
    """
    if not orchestrator:
        return jsonify({"error": "Orchestrator not initialized. Call /init first"}), 400
    
    try:
        credentials = request.json
        results = orchestrator.authenticate_all_apps(credentials)
        
        return jsonify({
            "status": "authenticated",
            "results": {k.value: v for k, v in results.items()}
        })
    except Exception as e:
        logger.error(f"Auth failed: {e}")
        return jsonify({"error": str(e)}), 400


@app.route("/sync", methods=["POST"])
def sync_data():
    """Sync data from all 3 dating apps."""
    if not orchestrator:
        return jsonify({"error": "Orchestrator not initialized"}), 400
    
    try:
        logger.info("Starting sync...")
        stats = orchestrator.sync_all_apps()
        
        return jsonify({
            "status": "synced",
            "stats": stats
        })
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/matches/mutual", methods=["GET"])
def get_mutual_matches():
    """Get mutual matches (both parties liked each other)."""
    if not orchestrator:
        return jsonify({"error": "Orchestrator not initialized"}), 400
    
    try:
        matches = orchestrator.get_mutual_matches()
        return jsonify({
            "count": len(matches),
            "matches": [m.to_dict() for m in matches]
        })
    except Exception as e:
        logger.error(f"Get mutual matches failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/matches/incoming", methods=["GET"])
def get_incoming_likes():
    """Get profiles who sent you a like."""
    if not orchestrator:
        return jsonify({"error": "Orchestrator not initialized"}), 400
    
    try:
        likes = orchestrator.get_incoming_likes()
        return jsonify({
            "count": len(likes),
            "likes": [l.to_dict() for l in likes]
        })
    except Exception as e:
        logger.error(f"Get incoming likes failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/filter-and-rank", methods=["POST"])
def filter_and_rank():
    """
    Apply strict filters and compute match scores.
    
    Request body:
    {
        "your_interests": ["hiking", "travel", "photography"],
        "embed_photos": false
    }
    """
    if not orchestrator:
        return jsonify({"error": "Orchestrator not initialized"}), 400
    
    try:
        data = request.json
        your_interests = data.get("your_interests", [])
        embed_photos = data.get("embed_photos", False)
        
        results = orchestrator.filter_and_rank(your_interests, embed_photos=embed_photos)
        
        return jsonify({
            "status": "filtered",
            "mutual_matches": [p.to_dict() for p in results["mutual_matches"]],
            "incoming_likes": [p.to_dict() for p in results["incoming_likes"]],
            "potential_matches": [p.to_dict() for p in results["potential_matches"]],
        })
    except Exception as e:
        logger.error(f"Filter and rank failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/search/by-description", methods=["POST"])
def search_by_description():
    """
    Find profiles matching a text description using CLIP.
    
    Request body:
    {
        "description": "athletic blonde woman who loves hiking",
        "top_k": 10,
        "filter_first": true
    }
    """
    if not orchestrator or not orchestrator.clip_matcher:
        return jsonify({"error": "CLIP matching not available"}), 400
    
    try:
        data = request.json
        description = data.get("description", "")
        top_k = data.get("top_k", 10)
        
        results = orchestrator.find_similar_by_description(description, top_k=top_k)
        
        return jsonify({
            "status": "found",
            "count": len(results),
            "matches": [
                {
                    "profile": p.to_dict(),
                    "similarity_score": float(score)
                }
                for p, score in results
            ]
        })
    except Exception as e:
        logger.error(f"Search by description failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/stats", methods=["GET"])
def get_stats():
    """Get current statistics."""
    if not orchestrator:
        return jsonify({"error": "Orchestrator not initialized"}), 400
    
    try:
        all_profiles = list(orchestrator.all_profiles.values())
        mutual = [p for p in all_profiles if p.match_status == MatchStatus.MUTUAL]
        incoming = [p for p in all_profiles if p.match_status == MatchStatus.INCOMING]
        outgoing = [p for p in all_profiles if p.match_status == MatchStatus.OUTGOING]
        
        # Count by app
        by_app = {}
        for profile in all_profiles:
            app = profile.app_source.value
            if app not in by_app:
                by_app[app] = 0
            by_app[app] += 1
        
        return jsonify({
            "total_profiles": len(all_profiles),
            "mutual_matches": len(mutual),
            "incoming_likes": len(incoming),
            "outgoing_likes": len(outgoing),
            "by_app": by_app,
        })
    except Exception as e:
        logger.error(f"Get stats failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/refresh", methods=["POST"])
def refresh_new_data():
    """Refresh data and get what changed."""
    if not orchestrator:
        return jsonify({"error": "Orchestrator not initialized"}), 400
    
    try:
        changes = orchestrator.refresh_new_data()
        
        return jsonify({
            "status": "refreshed",
            "changes": changes
        })
    except Exception as e:
        logger.error(f"Refresh failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/profile/<app>/<profile_id>", methods=["GET"])
def get_profile(app: str, profile_id: str):
    """Get a specific profile."""
    if not orchestrator:
        return jsonify({"error": "Orchestrator not initialized"}), 400
    
    try:
        # Find profile by app and ID
        for app_source in AppSource:
            if app_source.value == app:
                key = (profile_id, app_source)
                if key in orchestrator.all_profiles:
                    profile = orchestrator.all_profiles[key]
                    return jsonify(profile.to_dict())
        
        return jsonify({"error": "Profile not found"}), 404
    except Exception as e:
        logger.error(f"Get profile failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/export/mutual-matches", methods=["GET"])
def export_mutual_matches():
    """Export all mutual matches as JSON."""
    if not orchestrator:
        return jsonify({"error": "Orchestrator not initialized"}), 400
    
    try:
        data = orchestrator.export_all_mutual_matches()
        
        # Create downloadable response
        response = jsonify(data)
        response.headers["Content-Disposition"] = "attachment; filename=mutual_matches.json"
        return response
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/hinge/request-otp", methods=["POST"])
def hinge_request_otp():
    """Request Hinge OTP via phone."""
    try:
        import sys
        sys.path.insert(0, '..')
        from dating_agent.profile_aggregator import profile_aggregator
        
        agg = profile_aggregator()
        data = request.json
        phone = data.get('phone')
        
        if not phone:
            return jsonify({"error": "Phone number required"}), 400
        
        result = agg.hinge_auth.request_phone_verification(phone, solve_captcha=False)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Hinge OTP request failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/hinge/verify-otp", methods=["POST"])
def hinge_verify_otp():
    """Verify Hinge OTP code."""
    try:
        import sys
        sys.path.insert(0, '..')
        from dating_agent.profile_aggregator import profile_aggregator
        
        agg = profile_aggregator()
        data = request.json
        otp_id = data.get('otp_id')
        code = data.get('code')
        
        if not otp_id or not code:
            return jsonify({"error": "OTP ID and code required"}), 400
        
        result = agg.hinge_auth.verify_phone_otp(otp_id, code)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Hinge OTP verify failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/hinge/sync", methods=["POST"])
def hinge_sync():
    """Sync profiles from Hinge."""
    try:
        import sys
        sys.path.insert(0, '..')
        from dating_agent.profile_aggregator import profile_aggregator
        import time
        
        agg = profile_aggregator()
        data = request.json
        user_id = data.get('user_id')
        limit = data.get('limit', 50)
        
        if not user_id:
            return jsonify({"error": "User ID required"}), 400
        
        start = time.time()
        result = agg.run_full_sync(
            hinge_user_id=user_id,
            limit=limit,
            find_duplicates=True
        )
        duration = time.time() - start
        
        return jsonify({
            "status": "success",
            "profiles_fetched": result['platforms'].get('hinge', {}).get('profiles_fetched', 0),
            "profiles_stored": result['platforms'].get('hinge', {}).get('profiles_stored', 0),
            "duration": round(duration, 1)
        })
    except Exception as e:
        logger.error(f"Hinge sync failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/top", methods=["GET", "POST"])
def get_top_ranked():
    """
    Get top ranked profiles based on scoring algorithm.
    
    GET: Use default ranking config
    POST: Customize ranking config
    
    POST body (all optional):
    {
        "n": 20,
        "min_age": 25,
        "max_age": 45,
        "max_distance_km": 50,
        "must_not_smoke": true,
        "must_be_verified": false,
        "preferred_ethnicities": ["asian", "white"]
    }
    """
    if not orchestrator:
        return jsonify({"error": "Orchestrator not initialized"}), 400
    
    try:
        # Get config from request or use defaults
        if request.method == "POST":
            data = request.json or {}
        else:
            data = {}
        
        n = data.get("n", 20)
        
        # Build ranking config
        config = RankingConfig(
            min_age=data.get("min_age", 25),
            max_age=data.get("max_age", 45),
            max_distance_km=data.get("max_distance_km", 50),
            must_not_smoke=data.get("must_not_smoke", True),
            must_not_use_drugs=data.get("must_not_use_drugs", True),
            must_be_verified=data.get("must_be_verified", False),
            preferred_ethnicities=data.get("preferred_ethnicities"),
        )
        
        # Get all profiles as dicts
        all_profiles = [p.to_dict() for p in orchestrator.all_profiles.values()]
        
        # Rank and get top N
        top_profiles = get_top_matches(all_profiles, n=n, config=config)
        
        return jsonify({
            "status": "ranked",
            "total_profiles": len(all_profiles),
            "top_n": n,
            "config": {
                "min_age": config.min_age,
                "max_age": config.max_age,
                "max_distance_km": config.max_distance_km,
                "must_not_smoke": config.must_not_smoke,
            },
            "profiles": top_profiles,
        })
    except Exception as e:
        logger.error(f"Ranking failed: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    logger.info("Starting Dating App Orchestrator API...")
    logger.info("Available at: http://localhost:5001")
    logger.info("Docs: http://localhost:5001/health")
    app.run(debug=True, host="0.0.0.0", port=5001)
