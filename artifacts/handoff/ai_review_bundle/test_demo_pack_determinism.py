import json
from pathlib import Path


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _build_pack_to(pack_root: Path, matches_dir: Path) -> None:
    """Build demo pack stores deterministically into `pack_root`.

    This is intentionally implemented without shelling out to scripts so the
    determinism check is fully automated and platform-independent.
    """

    from backend.demo_pack.builder import (
        build_evidence_panels,
        build_moments,
        build_patterns,
        load_demo_match_file,
        synthesize_events,
    )
    from backend.demo_pack.io import write_stores

    match_paths = sorted(matches_dir.glob("*.json"))
    assert len(match_paths) == 6, f"Expected 6 matches, got {len(match_paths)}"

    events_by_match = {}
    moments_by_match = {}
    all_moments = []

    for mp in match_paths:
        match = load_demo_match_file(mp)
        match_id = match.get("match_id") or mp.stem
        events = synthesize_events(match_id, match)
        events_by_match[match_id] = events
        moments = build_moments(match_id, events)
        moments_by_match[match_id] = moments
        all_moments.extend(moments)

    team_ids = sorted({t for mid in events_by_match.keys() for t in mid.split("-")[:2]})
    patterns = build_patterns(team_ids=team_ids, all_moments=all_moments)
    panels = build_evidence_panels(events_by_match, moments_by_match)

    write_stores(pack_root, events_by_match, moments_by_match, patterns, panels)


def _write_demo_matches(matches_dir: Path, frames: int = 120) -> None:
    from scripts.generate_demo_matches import _load_base_snapshot, make_demo_match

    base = _load_base_snapshot(Path("data/raw/real_data.json"))
    match_ids = [
        "TL-C9-G2",
        "TL-C9-G3",
        "TL-100-G1",
        "TL-100-G2",
        "C9-100-G1",
        "C9-100-G2",
    ]

    matches_dir.mkdir(parents=True, exist_ok=True)
    for idx, mid in enumerate(match_ids):
        match = make_demo_match(base, mid, idx, frames)
        (matches_dir / f"{mid}.json").write_text(
            json.dumps(match, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def test_demo_pack_double_build_is_identical(tmp_path: Path):
    """Unassailable determinism: build the same pack twice and compare outputs.

    Pass criteria:
    - `events_store.json` identical (IDs and ordering)
    - `moments_store.json` identical (timestamps/types/refs)
    - `patterns_store.json` identical (pattern ids and instance refs)
    - `evidence_refs.json` identical (panel keys and counts)
    """

    matches_dir = tmp_path / "demo_matches"
    _write_demo_matches(matches_dir, frames=120)

    pack_a = tmp_path / "pack_a"
    pack_b = tmp_path / "pack_b"
    _build_pack_to(pack_a, matches_dir)
    _build_pack_to(pack_b, matches_dir)

    files = [
        ("events_store.json", pack_a / "processed" / "events_store.json", pack_b / "processed" / "events_store.json"),
        ("moments_store.json", pack_a / "processed" / "moments_store.json", pack_b / "processed" / "moments_store.json"),
        ("patterns_store.json", pack_a / "processed" / "patterns_store.json", pack_b / "processed" / "patterns_store.json"),
        ("evidence_refs.json", pack_a / "processed" / "evidence_refs.json", pack_b / "processed" / "evidence_refs.json"),
    ]

    for name, a_path, b_path in files:
        a = _read_json(a_path)
        b = _read_json(b_path)
        assert a == b, f"{name} differs between two builds"
