from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_demo_matches(out_dir: Path, frames: int) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

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
    out_dir.mkdir(parents=True, exist_ok=True)
    for idx, mid in enumerate(match_ids):
        match = make_demo_match(base, mid, idx, frames)
        (out_dir / f"{mid}.json").write_text(
            json.dumps(match, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def _build_pack_to(pack_root: Path, matches_dir: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from backend.demo_pack.builder import (
        build_evidence_panels,
        build_moments,
        build_patterns,
        load_demo_match_file,
        synthesize_events,
    )
    from backend.demo_pack.io import write_stores

    match_paths = sorted(matches_dir.glob("*.json"))
    if len(match_paths) != 6:
        raise SystemExit(f"Expected 6 matches in {matches_dir}, got {len(match_paths)}")

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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", type=int, default=120)
    ap.add_argument("--work-dir", default="artifacts/determinism_check")
    args = ap.parse_args()

    work = Path(args.work_dir)
    if work.exists():
        shutil.rmtree(work)
    (work / "matches").mkdir(parents=True, exist_ok=True)

    _write_demo_matches(work / "matches", frames=args.frames)

    pack_a = work / "pack_a"
    pack_b = work / "pack_b"
    _build_pack_to(pack_a, work / "matches")
    _build_pack_to(pack_b, work / "matches")

    compare = [
        ("events_store.json", pack_a / "processed" / "events_store.json", pack_b / "processed" / "events_store.json"),
        ("moments_store.json", pack_a / "processed" / "moments_store.json", pack_b / "processed" / "moments_store.json"),
        ("patterns_store.json", pack_a / "processed" / "patterns_store.json", pack_b / "processed" / "patterns_store.json"),
        ("evidence_refs.json", pack_a / "processed" / "evidence_refs.json", pack_b / "processed" / "evidence_refs.json"),
    ]
    for name, a_path, b_path in compare:
        a = _read_json(a_path)
        b = _read_json(b_path)
        if a != b:
            raise SystemExit(f"Determinism check failed: {name} differs between two builds")

    print("✓ Determinism verified (double-build outputs are identical)")
    print(f"Work dir: {work}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
