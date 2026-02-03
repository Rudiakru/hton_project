import json
import subprocess
import sys
from pathlib import Path


def _run_build(tmp_path: Path, *, source: str, matches_dir: Path | None = None) -> Path:
    out_root = tmp_path / f"demo_pack_{source}"
    tar_path = tmp_path / f"demo_pack_{source}.tar.gz"

    cmd = [
        sys.executable,
        "scripts/build_demo_pack.py",
        "--source",
        source,
        "--out",
        str(out_root),
        "--tar",
        str(tar_path),
    ]
    if matches_dir is not None:
        cmd.extend(["--matches-dir", str(matches_dir)])

    subprocess.run(cmd, check=True)
    assert out_root.exists()
    assert (out_root / "processed" / "events_store.json").exists()
    return out_root


def test_build_writes_observation_masking_and_benchmarks(tmp_path):
    out_root = _run_build(tmp_path, source="synthetic", matches_dir=Path("data/demo_matches"))

    masking = json.loads((out_root / "processed" / "observation_masking.json").read_text(encoding="utf-8"))
    assert masking["status"] == "ok"
    assert isinstance(masking["events_before"], int) and masking["events_before"] > 0
    assert isinstance(masking["events_after"], int) and 0 <= masking["events_after"] <= masking["events_before"]
    assert isinstance(masking["reduction_pct"], int) and 0 <= masking["reduction_pct"] <= 100

    benchmarks = json.loads((out_root / "processed" / "benchmarks.json").read_text(encoding="utf-8"))
    assert benchmarks["version"] == 1
    assert isinstance(benchmarks["pack_build_ms"], int) and benchmarks["pack_build_ms"] >= 0
    assert isinstance(benchmarks["endpoint_latencies_ms"], dict)
    # Non-flaky: only check presence and non-negative ranges
    assert "/api/demo/health" in benchmarks["endpoint_latencies_ms"]
    assert all(v >= 0 for v in benchmarks["endpoint_latencies_ms"].values())
    assert isinstance(benchmarks["determinism_sha256_combined"], str) and len(benchmarks["determinism_sha256_combined"]) == 64

    meta = json.loads((out_root / "metadata.json").read_text(encoding="utf-8"))
    assert meta["version"] == 1
    assert meta["source"] in {"synthetic", "custom"}


def test_real_source_pack_optional(tmp_path):
    real_dir = Path("data/demo_matches_real")
    if not real_dir.exists() or len(list(real_dir.glob("*.json"))) != 6:
        # Repo may not ship real match exports by default.
        return

    out_root = _run_build(tmp_path, source="real")
    meta = json.loads((out_root / "metadata.json").read_text(encoding="utf-8"))
    assert meta["source"] == "real"
    assert meta["real_matches"] == 6
