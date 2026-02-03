import json
from pathlib import Path

import pytest

from backend.demo_pack.builder import build_evidence_panels, build_moments, build_patterns, synthesize_events
from backend.demo_pack.io import load_stores, write_stores


@pytest.fixture()
def demo_match_path() -> Path:
    return Path("data/raw/real_data.json")


def _make_match_wrapper(base: dict, match_id: str) -> dict:
    """Wrap the existing snapshot into the expected match structure."""
    return {
        "match_id": match_id,
        "data": base,
    }


def test_deterministic_evidence_ids_same_input(demo_match_path, tmp_path):
    base = json.loads(demo_match_path.read_text(encoding="utf-8"))
    match = _make_match_wrapper(base, "TL-C9-G2")

    ev1 = synthesize_events("TL-C9-G2", match)
    ev2 = synthesize_events("TL-C9-G2", match)

    assert [e.evidence_id for e in ev1] == [e.evidence_id for e in ev2]
    assert [e.global_seq for e in ev1] == list(range(1, len(ev1) + 1))


def test_save_load_preserves_ids_and_refs(demo_match_path, tmp_path):
    base = json.loads(demo_match_path.read_text(encoding="utf-8"))
    match_id = "TL-C9-G2"
    match = _make_match_wrapper(base, match_id)

    events = synthesize_events(match_id, match)
    moments = build_moments(match_id, events)
    patterns = build_patterns(team_ids=["TL", "C9"], all_moments=moments)
    panels = build_evidence_panels({match_id: events}, {match_id: moments})

    pack_root = tmp_path / "pack"
    write_stores(pack_root, {match_id: events}, {match_id: moments}, patterns, panels)
    ev_by_match, mo_by_match, pat2, panels2 = load_stores(pack_root)

    assert [e.evidence_id for e in ev_by_match[match_id]] == [e.evidence_id for e in events]
    assert [m.primary_event_ref for m in mo_by_match[match_id]] == [m.primary_event_ref for m in moments]
    assert set(panels2.keys()) == {e.evidence_id for e in events}
    assert len(pat2) == len(patterns)


def test_all_moment_refs_exist(demo_match_path):
    base = json.loads(demo_match_path.read_text(encoding="utf-8"))
    match_id = "TL-C9-G2"
    match = _make_match_wrapper(base, match_id)

    events = synthesize_events(match_id, match)
    moments = build_moments(match_id, events)
    event_ids = {e.evidence_id for e in events}

    assert 3 <= len(moments) <= 5
    for m in moments:
        assert m.primary_event_ref in event_ids
        for r in m.related_event_refs:
            assert r in event_ids
