import json
from pathlib import Path

from fastapi.testclient import TestClient


def _build_temp_demo_pack(tmp_path: Path) -> Path:
    """Build a spec-compliant demo pack in a temp dir for failure-mode tests."""

    from backend.demo_pack.builder import (
        build_evidence_panels,
        build_moments,
        build_patterns,
        synthesize_events,
    )
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


def _reset_demo_runtime_cache() -> None:
    import backend.demo_pack.runtime as runtime

    runtime._CACHED = None


def test_demo_pack_corruption_returns_actionable_500(tmp_path, monkeypatch):
    pack_root = _build_temp_demo_pack(tmp_path)
    monkeypatch.setenv("DEMO_PACK_ROOT", str(pack_root))

    # Corrupt a required JSON file.
    events_store = pack_root / "processed" / "events_store.json"
    events_store.write_text("{ not valid json", encoding="utf-8")

    _reset_demo_runtime_cache()

    from backend.main import app

    client = TestClient(app)
    r = client.get("/api/demo/health")
    assert r.status_code == 500

    detail = r.json().get("detail")
    assert isinstance(detail, str)
    assert "Demo pack corrupted" in detail
    assert "Fix:" in detail
    assert "Rebuild" in detail


def test_integrity_surfaces_missing_evidence_panel(tmp_path, monkeypatch):
    pack_root = _build_temp_demo_pack(tmp_path)
    monkeypatch.setenv("DEMO_PACK_ROOT", str(pack_root))

    evidence_refs = pack_root / "processed" / "evidence_refs.json"
    raw = json.loads(evidence_refs.read_text(encoding="utf-8"))
    panels = raw.get("panels") or {}
    assert len(panels) > 0

    # Delete exactly one panel entry.
    victim_key = sorted(panels.keys())[0]
    del panels[victim_key]
    raw["panels"] = panels
    evidence_refs.write_text(json.dumps(raw, indent=2, sort_keys=True), encoding="utf-8")

    _reset_demo_runtime_cache()

    from backend.main import app

    client = TestClient(app)
    integrity = client.get("/api/demo/integrity")
    assert integrity.status_code == 200
    payload = integrity.json()
    assert payload["broken_refs"] > 0


def test_wrong_demo_pack_root_returns_actionable_500(tmp_path, monkeypatch):
    # Point DEMO_PACK_ROOT at a non-existent folder.
    monkeypatch.setenv("DEMO_PACK_ROOT", str(tmp_path / "missing_demo_pack"))

    _reset_demo_runtime_cache()

    from backend.main import app

    client = TestClient(app)
    r = client.get("/api/demo/health")
    assert r.status_code == 500

    detail = r.json().get("detail")
    assert isinstance(detail, str)
    assert "Demo pack corrupted" in detail
    assert "Fix:" in detail


def test_missing_demo_pack_root_returns_actionable_500(monkeypatch):
    # DEMO_PACK_ROOT must be explicitly set in demo mode.
    monkeypatch.delenv("DEMO_PACK_ROOT", raising=False)

    _reset_demo_runtime_cache()

    from backend.main import app

    client = TestClient(app)
    r = client.get("/api/demo/health")
    assert r.status_code == 500

    detail = r.json().get("detail")
    assert isinstance(detail, str)
    assert "Demo pack corrupted" in detail
    assert "DEMO_PACK_ROOT" in detail
    assert "Fix:" in detail
