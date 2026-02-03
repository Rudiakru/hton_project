import json

from fastapi.testclient import TestClient


def test_health_endpoint_ok():
    from backend.main import app

    client = TestClient(app)
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_parse_match_accepts_single_json_file():
    from backend import main

    main.parsing_cache.clear()
    client = TestClient(main.app)

    frame = {
        "data": {
            "seriesState": {
                "id": "S_JSON",
                "games": [{"teams": []}],
            }
        }
    }

    content = json.dumps(frame).encode("utf-8")
    response = client.post(
        "/api/parse-match",
        files={"file": ("match.json", content, "application/json")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["series_id"] == "S_JSON"
    assert payload["analytics"]["series_id"] == "S_JSON"


def test_parse_match_accepts_jsonl_file_and_uses_last_frame_series_id():
    from backend import main

    main.parsing_cache.clear()
    client = TestClient(main.app)

    frame_1 = {"data": {"seriesState": {"id": "S1", "games": [{"teams": []}]}}}
    frame_2 = {"data": {"seriesState": {"id": "S2", "games": [{"teams": []}]}}}

    content = (json.dumps(frame_1) + "\n" + json.dumps(frame_2) + "\n").encode("utf-8")
    response = client.post(
        "/api/parse-match",
        files={"file": ("match.jsonl", content, "application/x-ndjson")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["series_id"] == "S2"


def test_analyze_batch_does_not_crash_when_match_has_no_games():
    """Regression: batch aggregation used to divide by zero when cohesion history was empty."""

    from backend import main

    main.parsing_cache.clear()
    client = TestClient(main.app)

    no_games_frame = {"data": {"seriesState": {"id": "EMPTY", "games": []}}}
    content = json.dumps(no_games_frame).encode("utf-8")

    response = client.post(
        "/api/analyze-batch",
        files=[("files", ("empty.json", content, "application/json"))],
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["count"] == 1
    assert "aggregate" in payload
    assert payload["aggregate"]["avg_cohesion"] == 0.0
