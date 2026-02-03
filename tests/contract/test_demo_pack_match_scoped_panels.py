from pathlib import Path


def test_evidence_panels_are_strictly_match_scoped(tmp_path: Path):
    """Fails if any evidence panel contains context events from a different match."""

    from backend.demo_pack.io import load_stores
    from scripts.generate_demo_matches import _load_base_snapshot, make_demo_match
    import json

    matches_dir = tmp_path / "demo_matches"
    matches_dir.mkdir(parents=True, exist_ok=True)

    base = _load_base_snapshot(Path("data/raw/real_data.json"))
    match_ids = [
        "TL-C9-G2",
        "TL-C9-G3",
        "TL-100-G1",
        "TL-100-G2",
        "C9-100-G1",
        "C9-100-G2",
    ]
    for idx, mid in enumerate(match_ids):
        match = make_demo_match(base, mid, idx, frames=60)
        (matches_dir / f"{mid}.json").write_text(json.dumps(match, indent=2), encoding="utf-8")

    # Build pack stores into tmp_path/pack
    from tests.contract.test_demo_pack_determinism import _build_pack_to

    pack_root = tmp_path / "pack"
    _build_pack_to(pack_root, matches_dir)

    _events_by_match, _moments_by_match, _patterns, panels = load_stores(pack_root)
    for evidence_id, panel in panels.items():
        assert panel.match_id == panel.event.match_id
        for e in panel.context_window:
            assert (
                e.match_id == panel.match_id
            ), f"Cross-match contamination in panel {evidence_id}: {e.match_id} != {panel.match_id}"
        for m in panel.related_moments:
            assert (
                m.match_id == panel.match_id
            ), f"Cross-match contamination in related moments {evidence_id}: {m.match_id} != {panel.match_id}"
