from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_base_snapshot(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _deterministic_shift(val: float, match_idx: int, frame_idx: int) -> float:
    # Small deterministic shift to avoid identical frames across matches.
    return float(val) + (match_idx * 7) + ((frame_idx % 10) - 5) * 0.3


def make_demo_match(base: dict, match_id: str, match_idx: int, frames: int) -> dict:
    series_state = base.get("data", {}).get("seriesState", {})
    games = series_state.get("games", [])
    game0 = games[0] if games else {"teams": []}

    out_frames = []
    for frame_idx in range(frames):
        ts = frame_idx * 10
        game = json.loads(json.dumps(game0))  # deep copy via JSON for determinism
        for team in game.get("teams", []):
            for p in team.get("players", []):
                pos = p.get("position")
                if not isinstance(pos, dict):
                    continue
                if pos.get("x") is None or pos.get("y") is None:
                    continue
                pos["x"] = _deterministic_shift(float(pos["x"]), match_idx, frame_idx)
                pos["y"] = _deterministic_shift(float(pos["y"]), match_idx, frame_idx)
        out_frames.append({"ts": ts, "game": game})

    return {
        "match_id": match_id,
        "frames": out_frames,
        "meta": {
            "source": "derived_from_real_data_snapshot",
            "frames": frames,
            "dt_seconds": 10,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="data/raw/real_data.json")
    ap.add_argument("--out-dir", default="data/demo_matches")
    ap.add_argument("--frames", type=int, default=360)
    args = ap.parse_args()

    base = _load_base_snapshot(Path(args.base))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    match_ids = [
        "TL-C9-G2",
        "TL-C9-G3",
        "TL-100-G1",
        "TL-100-G2",
        "C9-100-G1",
        "C9-100-G2",
    ]
    for idx, mid in enumerate(match_ids):
        match = make_demo_match(base, mid, idx, args.frames)
        with (out_dir / f"{mid}.json").open("w", encoding="utf-8") as f:
            json.dump(match, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(match_ids)} demo matches to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
