from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.demo_pack.schemas import DemoEvent, DemoMoment, DemoPattern, EvidencePanel


@dataclass(frozen=True)
class DemoStores:
    events_by_match: dict[str, list[DemoEvent]]
    moments_by_match: dict[str, list[DemoMoment]]
    patterns: list[DemoPattern]
    panels_by_evidence_id: dict[str, EvidencePanel]
    metadata: dict[str, Any]
    observation_masking: dict[str, Any] | None
    benchmarks: dict[str, Any] | None


class DemoPackCorrupted(RuntimeError):
    def __init__(self, message: str, *, fix: str = "Rebuild the demo pack"):
        super().__init__(message)
        self.fix = fix


_CACHED: DemoStores | None = None


def _read_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise DemoPackCorrupted(f"Missing required demo pack file: {path}") from e
    except json.JSONDecodeError as e:
        raise DemoPackCorrupted(f"Demo pack JSON is corrupted: {path}") from e


def _try_read_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        raise DemoPackCorrupted(f"Demo pack JSON is corrupted: {path}") from e


def load_demo_stores(pack_root: str | Path | None = None) -> DemoStores:
    """Load precomputed demo stores from disk.

    This is intentionally "zero compute" at runtime: it only loads frozen JSON.
    """

    global _CACHED
    if _CACHED is not None:
        return _CACHED

    if pack_root is None:
        env_root = os.environ.get("DEMO_PACK_ROOT")
        if not env_root:
            raise DemoPackCorrupted(
                "DEMO_PACK_ROOT is not set",
                fix='Set DEMO_PACK_ROOT to the extracted demo pack directory (e.g., "artifacts/demo_pack")',
            )
        pack_root = env_root
    pack_root = Path(pack_root)

    processed = pack_root / "processed"
    events_raw = _read_json(processed / "events_store.json")
    moments_raw = _read_json(processed / "moments_store.json")
    patterns_raw = _read_json(processed / "patterns_store.json")
    evidence_raw = _read_json(processed / "evidence_refs.json")

    metadata = _try_read_json(pack_root / "metadata.json") or {}
    observation_masking = _try_read_json(processed / "observation_masking.json")
    benchmarks = _try_read_json(processed / "benchmarks.json")

    events_by_match = {
        mid: [DemoEvent.model_validate(e) for e in evs]
        for mid, evs in events_raw.get("matches", {}).items()
    }
    moments_by_match = {
        mid: [DemoMoment.model_validate(m) for m in moms]
        for mid, moms in moments_raw.get("matches", {}).items()
    }
    patterns = [DemoPattern.model_validate(p) for p in patterns_raw.get("patterns", [])]
    panels_by_evidence_id = {
        eid: EvidencePanel.model_validate(p)
        for eid, p in evidence_raw.get("panels", {}).items()
    }

    _CACHED = DemoStores(
        events_by_match=events_by_match,
        moments_by_match=moments_by_match,
        patterns=patterns,
        panels_by_evidence_id=panels_by_evidence_id,
        metadata=metadata,
        observation_masking=observation_masking,
        benchmarks=benchmarks,
    )
    return _CACHED
