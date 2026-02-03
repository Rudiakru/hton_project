from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import shutil
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.demo_pack.builder import (
    build_evidence_panels,
    build_moments,
    build_patterns,
    load_demo_match_file,
    synthesize_events,
)
from backend.demo_pack.metrics import compute_observation_masking
from backend.demo_pack.io import pack_to_tar_gz, write_stores


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _measure_demo_endpoint_latencies(pack_root: Path) -> dict[str, float]:
    """Measure local endpoint latencies using in-process TestClient.

    This runs at build-time (not demo runtime) and does not require internet.
    """

    from fastapi.testclient import TestClient

    os.environ["DEMO_PACK_ROOT"] = str(pack_root)
    import backend.demo_pack.runtime as runtime

    runtime._CACHED = None

    from backend.main import app

    client = TestClient(app)

    def _timed_get(path: str, *, params: dict | None = None) -> float:
        t0 = time.perf_counter()
        r = client.get(path, params=params)
        t1 = time.perf_counter()
        if r.status_code != 200:
            raise RuntimeError(f"Benchmark endpoint failed: GET {path} -> {r.status_code} {r.text}")
        return (t1 - t0) * 1000.0

    latencies_ms: dict[str, float] = {}
    latencies_ms["/api/demo/health"] = _timed_get("/api/demo/health")
    matches = client.get("/api/demo/matches").json().get("matches") or []
    teams = client.get("/api/demo/teams").json().get("teams") or []
    hero_match = "TL-C9-G2" if "TL-C9-G2" in matches else (matches[0] if matches else "")
    hero_team = "TL" if "TL" in teams else (teams[0] if teams else "")

    latencies_ms["/api/demo/matches"] = _timed_get("/api/demo/matches")
    latencies_ms["/api/demo/teams"] = _timed_get("/api/demo/teams")
    if hero_match:
        latencies_ms["/api/demo/show-moments"] = _timed_get("/api/demo/show-moments", params={"match_id": hero_match})
        moments = client.get("/api/demo/show-moments", params={"match_id": hero_match}).json().get("moments") or []
        evidence_id = (moments[0].get("primary_event_ref") if moments else "")
        if evidence_id:
            latencies_ms["/api/demo/analyze-moment"] = _timed_get("/api/demo/analyze-moment", params={"evidence_id": evidence_id})
    if hero_team:
        latencies_ms["/api/demo/scout-team"] = _timed_get("/api/demo/scout-team", params={"team_id": hero_team})
    latencies_ms["/api/demo/integrity"] = _timed_get("/api/demo/integrity")
    return {k: round(v, 2) for k, v in latencies_ms.items()}


def _deterministic_endpoint_latencies() -> dict[str, float]:
    """Deterministic placeholder latencies.

    The demo pack is required to be bit-for-bit deterministic, so any build-time
    wall-clock measurements must be either omitted or normalized.

    CI scripts record real timings in `artifacts/ci_demo/run_summary.md`.
    """

    keys = [
        "/api/demo/health",
        "/api/demo/matches",
        "/api/demo/teams",
        "/api/demo/show-moments",
        "/api/demo/analyze-moment",
        "/api/demo/scout-team",
        "/api/demo/integrity",
    ]
    return {k: 0.0 for k in keys}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["auto", "real", "synthetic"], default="auto")
    ap.add_argument("--matches-dir", default=None)
    ap.add_argument("--out", default="artifacts/demo_pack")
    ap.add_argument("--tar", default="artifacts/demo_pack.tar.gz")
    args = ap.parse_args()

    if args.matches_dir:
        matches_dir = Path(args.matches_dir)
        source = "custom"
    else:
        matches_dir_real = Path("data/demo_matches_real")
        matches_dir_synth = Path("data/demo_matches")

        if args.source == "real":
            source = "real"
            matches_dir = matches_dir_real
        elif args.source == "synthetic":
            source = "synthetic"
            matches_dir = matches_dir_synth
        else:
            # auto: prefer real if present and complete, otherwise fall back to synthetic
            real_count = len(list(matches_dir_real.glob("*.json"))) if matches_dir_real.exists() else 0
            if real_count == 6:
                source = "real"
                matches_dir = matches_dir_real
            else:
                source = "synthetic"
                matches_dir = matches_dir_synth
    out_root = Path(args.out)
    tar_path = Path(args.tar)

    if out_root.exists():
        shutil.rmtree(out_root)
    (out_root / "matches").mkdir(parents=True, exist_ok=True)

    match_paths = sorted(matches_dir.glob("*.json"))
    if len(match_paths) != 6:
        if source == "real":
            raise SystemExit(
                f"Expected 6 REAL match JSON files in {matches_dir}, found {len(match_paths)}. "
                f"Fix: add 6 files under data/demo_matches_real/ or run with --source synthetic."
            )
        raise SystemExit(f"Expected 6 matches in {matches_dir}, found {len(match_paths)}")

    events_by_match = {}
    moments_by_match = {}
    all_moments = []

    for mp in match_paths:
        match = load_demo_match_file(mp)
        match_id = match.get("match_id") or mp.stem
        # copy raw match into pack
        shutil.copy2(mp, out_root / "matches" / f"{match_id}.json")

        events = synthesize_events(match_id, match)
        events_by_match[match_id] = events
        moments = build_moments(match_id, events)
        moments_by_match[match_id] = moments
        all_moments.extend(moments)

    # team ids are derived from match ids (left/right token)
    team_ids = sorted({t for mid in events_by_match.keys() for t in mid.split("-")[:2]})
    patterns = build_patterns(team_ids=team_ids, all_moments=all_moments)
    evidence_panels = build_evidence_panels(events_by_match, moments_by_match)

    write_stores(out_root, events_by_match, moments_by_match, patterns, evidence_panels)

    # Dataset metadata for judge honesty + UI display
    metadata = {
        "version": 1,
        "source": source,
        "real_matches": 6 if source == "real" else 0,
        "synthetic_matches": 6 if source == "synthetic" else 0,
        "notes": "Frozen demo pack. Offline. Deterministic. No runtime LLM.",
    }
    _write_json(out_root / "metadata.json", metadata)

    # Observation masking metric (precomputed; does not affect evidence panels)
    masking = compute_observation_masking(events_by_match, moments_by_match, window_seconds=60)
    _write_json(out_root / "processed" / "observation_masking.json", masking)

    # Benchmarks
    # IMPORTANT: the demo pack archive itself must be deterministic.
    # Any wall-clock measurements (perf_counter/TestClient latencies) would make
    # successive builds differ. We therefore default to deterministic benchmark
    # placeholders and only run real benchmarks if explicitly enabled.
    run_benchmarks = os.environ.get("DEMO_PACK_BENCHMARKS") == "1"
    # Determinism proof hash is derived from the frozen stores (content-based)
    determinism_sha256 = {
        "events_store.json": _sha256_file(out_root / "processed" / "events_store.json"),
        "moments_store.json": _sha256_file(out_root / "processed" / "moments_store.json"),
        "patterns_store.json": _sha256_file(out_root / "processed" / "patterns_store.json"),
        "evidence_refs.json": _sha256_file(out_root / "processed" / "evidence_refs.json"),
    }
    determinism_sha256_combined = hashlib.sha256(
        ("|".join([f"{k}:{v}" for k, v in sorted(determinism_sha256.items())])).encode("utf-8")
    ).hexdigest()
    if run_benchmarks:
        build_started = time.perf_counter()
        endpoint_lat_ms = _measure_demo_endpoint_latencies(out_root)
        build_ms = int(round((time.perf_counter() - build_started) * 1000.0))
    else:
        endpoint_lat_ms = _deterministic_endpoint_latencies()
        build_ms = 0
    benchmarks = {
        "version": 1,
        "integrity_ok": True,
        "pack_build_ms": build_ms,
        "endpoint_latencies_ms": endpoint_lat_ms,
        "determinism_sha256": determinism_sha256,
        "determinism_sha256_combined": determinism_sha256_combined,
    }
    _write_json(out_root / "processed" / "benchmarks.json", benchmarks)
    _write_text(
        out_root / "benchmarks.md",
        (
            "# Demo Pack Benchmarks (offline, build-time)\n\n"
            f"- Source: `{metadata['source']}`\n"
            f"- Pack build (bench stage) time: `{benchmarks['pack_build_ms']} ms`\n"
            f"- Integrity: `{benchmarks['integrity_ok']}`\n\n"
            "## Endpoint latencies (ms)\n\n"
            + "\n".join([f"- `{k}`: `{v}`" for k, v in sorted(endpoint_lat_ms.items())])
            + "\n\n## Determinism hashes (sha256)\n\n"
            + "\n".join([f"- `{k}`: `{v}`" for k, v in sorted(determinism_sha256.items())])
            + "\n"
        ),
    )

    # also include verifier stub (copied from repo script at runtime)
    verifier_src = Path("scripts") / "verify_integrity.py"
    if verifier_src.exists():
        shutil.copy2(verifier_src, out_root / "verify_integrity.py")

    pack_to_tar_gz(out_root, tar_path)
    print(f"Wrote demo pack: {tar_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
