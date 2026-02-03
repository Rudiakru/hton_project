import json
import os
from pathlib import Path

from fastapi.testclient import TestClient


def _build_temp_demo_pack(tmp_path: Path) -> Path:
    """Build a small but spec-compliant demo pack in a temp dir for API tests."""

    from backend.demo_pack.builder import build_evidence_panels, build_moments, build_patterns, synthesize_events
    from backend.demo_pack.io import write_stores

    base = json.loads(Path("data/raw/real_data.json").read_text(encoding="utf-8"))

    match_ids = [
        "TL-C9-G2",
        "TL-C9-G3",
        "TL-100-G1",
        "TL-100-G2",
        "C9-100-G1",
        "C9-100-G2",
    ]

    events_by_match = {}
    moments_by_match = {}
    all_moments = []
    for mid in match_ids:
        match = {"match_id": mid, "data": base}
        events = synthesize_events(mid, match)
        moments = build_moments(mid, events)
        events_by_match[mid] = events
        moments_by_match[mid] = moments
        all_moments.extend(moments)

    team_ids = sorted({t for mid in match_ids for t in mid.split("-")[:2]})
    patterns = build_patterns(team_ids=team_ids, all_moments=all_moments)
    panels = build_evidence_panels(events_by_match, moments_by_match)

    pack_root = tmp_path / "demo_pack"
    (pack_root / "matches").mkdir(parents=True, exist_ok=True)
    write_stores(pack_root, events_by_match, moments_by_match, patterns, panels)
    return pack_root


def test_demo_endpoints_happy_path(tmp_path, monkeypatch):
    pack_root = _build_temp_demo_pack(tmp_path)
    monkeypatch.setenv("DEMO_PACK_ROOT", str(pack_root))

    # Reset runtime cache between tests
    import backend.demo_pack.runtime as runtime

    runtime._CACHED = None

    from backend.main import app

    client = TestClient(app)

    health = client.get("/api/demo/health")
    assert health.status_code == 200
    assert health.json()["mode"] == "demo"
    assert health.json()["matches"] == 6

    matches = client.get("/api/demo/matches").json()["matches"]
    assert len(matches) == 6

    teams = client.get("/api/demo/teams").json()["teams"]
    assert set(teams) >= {"TL", "C9"}

    match_id = matches[0]
    moments = client.get("/api/demo/show-moments", params={"match_id": match_id}).json()["moments"]
    assert 3 <= len(moments) <= 5

    # Match-scoped evidence IDs (guards against cross-match contamination).
    for m in moments:
        assert isinstance(m.get("primary_event_ref"), str)
        assert m["primary_event_ref"].startswith(f"{match_id}:")
        for ref in m.get("related_event_refs") or []:
            assert isinstance(ref, str)
            assert ref.startswith(f"{match_id}:")

    evidence_id = moments[0]["primary_event_ref"]
    panel = client.get("/api/demo/analyze-moment", params={"evidence_id": evidence_id}).json()["panel"]
    assert panel["evidence_id"] == evidence_id
    assert panel["match_id"] == match_id
    assert all(e["match_id"] == match_id for e in panel.get("context_window", []))

    scout = client.get("/api/demo/scout-team", params={"team_id": teams[0]}).json()
    assert scout["sample_size"] == 6
    assert len(scout["patterns"]) >= 3

    integrity = client.get("/api/demo/integrity").json()
    assert integrity["broken_refs"] == 0

    # Optional judge-facing artifacts (may be missing in temp pack)
    mask = client.get("/api/demo/observation-masking").json()
    assert mask.get("status") in {"ok", "missing"}
    bench = client.get("/api/demo/benchmarks").json()
    assert bench.get("status") in {"missing"} or bench.get("version") == 1


def test_demo_flow_is_flake_free_10x(tmp_path, monkeypatch):
    """API-level rehearsal of the critical demo path.

    This doesn't replace a browser E2E test, but it is an automated guard that:
    - data loads from the frozen pack
    - moments are always 3–5
    - evidence panels open by evidence_id
    - scouting report opens and its evidence drills down
    - integrity remains broken_refs == 0
    """

    pack_root = _build_temp_demo_pack(tmp_path)
    monkeypatch.setenv("DEMO_PACK_ROOT", str(pack_root))

    import backend.demo_pack.runtime as runtime

    runtime._CACHED = None

    from backend.main import app

    client = TestClient(app)

    matches = client.get("/api/demo/matches").json()["matches"]
    teams = client.get("/api/demo/teams").json()["teams"]
    hero_match = "TL-C9-G2" if "TL-C9-G2" in matches else matches[0]
    hero_team = "TL" if "TL" in teams else teams[0]

    for _ in range(10):
        # Step 1: show moments
        moments = client.get("/api/demo/show-moments", params={"match_id": hero_match}).json()["moments"]
        assert 3 <= len(moments) <= 5

        # Step 2: analyze first moment
        evidence_id = moments[0]["primary_event_ref"]
        panel = client.get("/api/demo/analyze-moment", params={"evidence_id": evidence_id}).json()["panel"]
        assert panel["evidence_id"] == evidence_id
        assert panel["match_id"] == hero_match

        # Step 3: scouting report
        scout = client.get("/api/demo/scout-team", params={"team_id": hero_team}).json()
        assert scout["sample_size"] == 6
        assert len(scout["patterns"]) >= 3

        # Step 4: drill down first pattern evidence
        pattern0 = scout["patterns"][0]
        assert pattern0.get("instances")
        p_evidence_id = pattern0["instances"][0]["evidence_refs"][0]
        p_panel = client.get("/api/demo/analyze-moment", params={"evidence_id": p_evidence_id}).json()["panel"]
        assert p_panel["evidence_id"] == p_evidence_id

        # Step 5: integrity
        integrity = client.get("/api/demo/integrity").json()
        assert integrity["broken_refs"] == 0
