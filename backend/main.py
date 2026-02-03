from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from pathlib import Path
from typing import List
from backend.parsers.grid_parser import extract_player_positions
from backend.engines.risk_calculator import calculate_risk_score, classify_risk_stage
from backend.engines.spatial_analyzer import calculate_cohesion_score, detect_teamfight, analyze_isolation
from backend.engines.heatmap_generator import generate_death_heatmap, generate_victory_heatmap
from backend.engines.pattern_detector import detect_patterns
from backend.engines.insight_generator import generate_coaching_insights
from backend.engines.validator import validate_model_accuracy

from fastapi.responses import StreamingResponse
import io
import csv

from backend.demo_pack.runtime import DemoPackCorrupted, load_demo_stores

app = FastAPI(title="Macro Health Monitor API")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory cache
parsing_cache = {}

# Reusable parsing logic
async def process_match_data(content: bytes, filename: str = None):
    # Check cache if filename provided
    if filename and filename in parsing_cache:
        return parsing_cache[filename]
        
    # Accept either:
    # - JSONL (one JSON object per line)
    # - JSON (single object or list of objects)
    try:
        decoded = content.decode("utf-8")
    except UnicodeDecodeError:
        decoded = content.decode("utf-8", errors="replace")

    frames = []
    try:
        parsed = json.loads(decoded)
        if isinstance(parsed, list):
            frames = [f for f in parsed if isinstance(f, dict)]
        elif isinstance(parsed, dict):
            frames = [parsed]
    except json.JSONDecodeError:
        # Fall back to JSONL parsing
        lines = decoded.splitlines()
        for line in lines:
            if not line.strip():
                continue
            frames.append(json.loads(line))
    timeline_data = []
    cohesion_history = []
    pattern_history = []
    teamfight_events = []
    
    # We limit to 100 frames for performance in the demo
    frames = frames[:100]
    last_series_id = "N/A"
    
    for idx, frame in enumerate(frames):
        series_state = frame.get("data", {}).get("seriesState", {})
        last_series_id = series_state.get("id", last_series_id)
        games = series_state.get("games", [])
        if not games:
            continue
        
        game = games[0]
        game_time_seconds = idx * 10 # Dummy: 10s per frame
        game_time = f"{game_time_seconds // 60:02d}:{game_time_seconds % 60:02d}"
        
        teams_pos = extract_player_positions(game)
        
        # Teamfight detection
        if detect_teamfight(teams_pos):
            if not teamfight_events or teamfight_events[-1]["end_time_seconds"] < game_time_seconds - 20:
                teamfight_events.append({
                    "start_time": game_time,
                    "start_time_seconds": game_time_seconds,
                    "end_time_seconds": game_time_seconds,
                    "won": idx % 2 == 0 # Mock winner logic
                })
            else:
                teamfight_events[-1]["end_time_seconds"] = game_time_seconds
        
        blue_team_pos = teams_pos[0] if len(teams_pos) > 0 else []
        
        # Pattern detection
        patterns = detect_patterns(blue_team_pos, game_time_seconds)
        for p in patterns:
            pattern_history.append({
                "game_time": game_time,
                "pattern": p
            })
            
        # Mock Gold-Diff development
        gold_diff = (idx * 50) - 2000 if idx < 50 else (idx * -30) + 2000
        
        # Risk calculation
        game_state = {
            "gold_diff": gold_diff,
            "team_objectives": {"towers": 2, "dragons": 1}, 
            "enemy_objectives": {"towers": 1},
            "team_vision": 15.5,
            "enemy_vision": 12.0
        }
        risk_score = calculate_risk_score(game_state)
        
        timeline_data.append({
            "game_time": game_time,
            "gold_diff": gold_diff,
            "risk_score": risk_score
        })
        
        # Spatial analysis
        cohesion_blue = calculate_cohesion_score(blue_team_pos)
        cohesion_history.append({
            "game_time": game_time,
            "cohesion_score": cohesion_blue
        })

    # Final state for heatmaps and alerts (last frame)
    last_frame = frames[-1] if frames else {}
    last_series_state = last_frame.get("data", {}).get("seriesState", {})
    last_series_id = last_series_state.get("id", last_series_id)

    last_games = last_series_state.get("games") or []
    last_game = last_games[0] if last_games else {}
    last_teams_pos = extract_player_positions(last_game)
    
    final_risk = timeline_data[-1]["risk_score"] if timeline_data else 50
    stage = classify_risk_stage(final_risk)
    
    # Isolation Alerts
    isolation_alerts_red = analyze_isolation(last_teams_pos[1], last_teams_pos[0]) if len(last_teams_pos) > 1 else []
    
    # Insights generation
    insights = generate_coaching_insights({
        "cohesion_history": cohesion_history,
        "risk_score": final_risk,
        "pattern_history": pattern_history
    })

    result = {
        "series_id": last_series_id,
        "timeline": timeline_data,
        "risk_score": final_risk,
        "stage": stage,
        "cohesion_history": cohesion_history,
        "pattern_history": pattern_history,
        "teamfights": teamfight_events,
        "insights": insights,
        "is_teamfight": detect_teamfight(last_teams_pos) if len(last_teams_pos) > 1 else False,
        "isolation_alerts": isolation_alerts_red,
        "causal_chain": [
            {"cause": "Bad Spacing", "impact": -15},
            {"cause": "Gold Deficit", "impact": -5},
            {"cause": "Vision Loss", "impact": -8}
        ],
        "heatmaps": {
            "deaths": generate_death_heatmap([[12000, 12000], [12500, 12500], [8000, 9000]]),
            "victories": generate_victory_heatmap([[4000, 4000], [4500, 4500]]),
            "hotspots": ["Bot River", "Baron Pit"]
        }
    }

    # Store in cache
    if filename:
        parsing_cache[filename] = result

    return result

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/api/demo/health")
async def demo_health_check():
    try:
        stores = load_demo_stores()
    except DemoPackCorrupted as e:
        raise HTTPException(
            status_code=500,
            detail=f"Demo pack corrupted. {e}. Fix: {e.fix}.",
        )
    return {
        "status": "healthy",
        "mode": "demo",
        "matches": len(stores.events_by_match),
        "banner": "DEMO MODE — frozen dataset (6 matches)",
        "baseline_note": "Baseline computed within demo dataset only",
        "dataset": stores.metadata or {"source": "unknown"},
    }


@app.get("/api/demo/matches")
async def demo_list_matches():
    try:
        stores = load_demo_stores()
    except DemoPackCorrupted as e:
        raise HTTPException(status_code=500, detail=f"Demo pack corrupted. {e}. Fix: {e.fix}.")
    return {"matches": sorted(stores.events_by_match.keys())}


@app.get("/api/demo/teams")
async def demo_list_teams():
    try:
        stores = load_demo_stores()
    except DemoPackCorrupted as e:
        raise HTTPException(status_code=500, detail=f"Demo pack corrupted. {e}. Fix: {e.fix}.")
    team_ids = sorted({t for mid in stores.events_by_match.keys() for t in mid.split("-")[:2]})
    return {"teams": team_ids}


@app.get("/api/demo/show-moments")
async def demo_show_moments(match_id: str):
    try:
        stores = load_demo_stores()
    except DemoPackCorrupted as e:
        raise HTTPException(status_code=500, detail=f"Demo pack corrupted. {e}. Fix: {e.fix}.")
    moments = stores.moments_by_match.get(match_id)
    if moments is None:
        raise HTTPException(status_code=404, detail=f"Unknown match_id: {match_id}")
    return {
        "match_id": match_id,
        "moments": [m.model_dump() for m in moments],
    }


@app.get("/api/demo/analyze-moment")
async def demo_analyze_moment(evidence_id: str):
    try:
        stores = load_demo_stores()
    except DemoPackCorrupted as e:
        raise HTTPException(status_code=500, detail=f"Demo pack corrupted. {e}. Fix: {e.fix}.")
    panel = stores.panels_by_evidence_id.get(evidence_id)
    if panel is None:
        # Never echo raw evidence ids into UI-facing errors (coach/judge facing output).
        raise HTTPException(
            status_code=404,
            detail="Unknown evidence reference. Fix: rebuild the demo pack or refresh the page.",
        )
    return {"panel": panel.model_dump()}


@app.get("/api/demo/scout-team")
async def demo_scout_team(team_id: str):
    try:
        stores = load_demo_stores()
    except DemoPackCorrupted as e:
        raise HTTPException(status_code=500, detail=f"Demo pack corrupted. {e}. Fix: {e.fix}.")
    patterns = [p for p in stores.patterns if p.team_id == team_id]
    return {
        "team_id": team_id,
        "sample_size": 6,
        "baseline_note": "Baseline computed within demo dataset only",
        "patterns": [p.model_dump() for p in patterns],
    }


@app.get("/api/demo/observation-masking")
async def demo_observation_masking():
    try:
        stores = load_demo_stores()
    except DemoPackCorrupted as e:
        raise HTTPException(status_code=500, detail=f"Demo pack corrupted. {e}. Fix: {e.fix}.")
    if stores.observation_masking is None:
        return {"status": "missing", "note": "No observation masking metrics in this pack."}
    return stores.observation_masking


@app.get("/api/demo/benchmarks")
async def demo_benchmarks():
    try:
        stores = load_demo_stores()
    except DemoPackCorrupted as e:
        raise HTTPException(status_code=500, detail=f"Demo pack corrupted. {e}. Fix: {e.fix}.")
    if stores.benchmarks is None:
        return {"status": "missing", "note": "No benchmarks in this pack."}
    return stores.benchmarks


@app.get("/api/demo/integrity")
async def demo_integrity():
    try:
        stores = load_demo_stores()
    except DemoPackCorrupted as e:
        raise HTTPException(status_code=500, detail=f"Demo pack corrupted. {e}. Fix: {e.fix}.")
    broken_refs = 0
    total_events = sum(len(v) for v in stores.events_by_match.values())
    total_moments = sum(len(v) for v in stores.moments_by_match.values())

    for match_id, moments in stores.moments_by_match.items():
        event_ids = {e.evidence_id for e in stores.events_by_match.get(match_id, [])}
        for m in moments:
            if m.primary_event_ref not in event_ids:
                broken_refs += 1
            for r in m.related_event_refs:
                if r not in event_ids:
                    broken_refs += 1

    for p in stores.patterns:
        for inst in p.instances:
            for eid in inst.evidence_refs:
                if eid not in stores.panels_by_evidence_id:
                    broken_refs += 1

    # Evidence panels must exist for EVERY event (evidence references must never break)
    for match_id, events in stores.events_by_match.items():
        for e in events:
            if e.evidence_id not in stores.panels_by_evidence_id:
                broken_refs += 1

    match_count = len(stores.events_by_match)

    return {
        "mode": "demo",
        "match_count": match_count,
        "total_events": total_events,
        "total_moments": total_moments,
        "total_patterns": len(stores.patterns),
        "total_evidence_panels": len(stores.panels_by_evidence_id),
        "broken_refs": broken_refs,
    }


@app.get("/api/demo/validation")
async def demo_validation():
    """Return a tiny precomputed validation summary shipped in the demo pack.

    This must remain offline + zero-compute at runtime (just frozen JSON).
    """
    try:
        load_demo_stores()  # validates pack presence + corruption
    except DemoPackCorrupted as e:
        raise HTTPException(status_code=500, detail=f"Demo pack corrupted. {e}. Fix: {e.fix}.")

    pack_root = os.environ.get("DEMO_PACK_ROOT")
    if not pack_root:
        raise HTTPException(
            status_code=500,
            detail='DEMO_PACK_ROOT is not set. Fix: set DEMO_PACK_ROOT to the extracted demo pack directory.',
        )

    path = Path(pack_root) / "processed" / "validation_summary.json"
    if not path.exists():
        return {
            "status": "missing",
            "note": "No validation summary shipped in this demo pack.",
            "fix": "Rebuild the demo pack (scripts/build_demo_pack.py).",
        }
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Validation summary JSON is corrupted: {path}. {e}")

@app.post("/api/parse-match")
async def parse_match(file: UploadFile = File(...)):
    """
    Endpoint for parsing a single match upload (JSON or JSONL).
    """
    try:
        content = await file.read()
        analytics = await process_match_data(content, file.filename)
        return {"success": True, "analytics": analytics, "series_id": analytics["series_id"]}
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {"success": False, "error": str(e)}

@app.post("/api/analyze-batch")
async def analyze_batch(files: List[UploadFile] = File(...)):
    """
    Endpoint for batch processing multiple match files.
    """
    try:
        results = []
        for file in files:
            content = await file.read()
            analytics = await process_match_data(content, file.filename)
            results.append(analytics)
        
        if not results:
            return {"success": False, "error": "No files processed"}

        # Aggregate statistics across matches (robust against empty cohesion histories)
        per_match_cohesion = []
        for r in results:
            cohesion_history = r.get("cohesion_history", [])
            if cohesion_history:
                per_match_cohesion.append(
                    sum(c["cohesion_score"] for c in cohesion_history) / len(cohesion_history)
                )

        avg_cohesion_all = (sum(per_match_cohesion) / len(per_match_cohesion)) if per_match_cohesion else 0.0
        total_patterns = sum(len(r['pattern_history']) for r in results)
        total_teamfights = sum(len(r['teamfights']) for r in results)
        
        # Validation
        validation = validate_model_accuracy(results)
        
        return {
            "success": True,
            "count": len(results),
            "aggregate": {
                "avg_cohesion": round(avg_cohesion_all, 2),
                "total_patterns": total_patterns,
                "total_teamfights": total_teamfights,
                "risk_trend": "Improving (Based on last 5 matches)",
                "common_patterns": ["Baron Setup", "Split Push 1-4"],
                "model_accuracy": validation["accuracy"]
            },
            "matches": results,
            "validation": validation
        }
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {"success": False, "error": str(e)}

@app.get("/api/export-csv")
async def export_csv():
    """
    Exports aggregate insights as a CSV file.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Type", "Severity", "Title", "Observation", "Recommendation", "Impact"])
    
    # Static demo data or from cache
    writer.writerow(["COHESION", "HIGH", "Formation Breakdown", "Cohesion dropped to 32", "Practice 'Tethering' drills", "High risk of isolated pick-offs"])
    writer.writerow(["RISK", "CRITICAL", "High Criticality Exposure", "Global risk is 68%", "Concede non-essential objectives", "Next fight has <40% win probability"])
    
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=macro-analysis.csv"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
