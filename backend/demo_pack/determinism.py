from __future__ import annotations

import re
from dataclasses import dataclass


_EVIDENCE_ID_RE = re.compile(r"^[A-Z0-9-]+:\d{6}$")


def format_game_time(ts_seconds: int) -> str:
    m, s = divmod(max(0, int(ts_seconds)), 60)
    return f"{m:02d}:{s:02d}"


def make_evidence_id(match_id: str, global_seq: int) -> str:
    evidence_id = f"{match_id}:{global_seq:06d}"
    if not _EVIDENCE_ID_RE.match(evidence_id):
        # Defensive: ensures match_id is compatible with the locked regex
        raise ValueError(f"Generated evidence_id has invalid format: {evidence_id}")
    return evidence_id


@dataclass(frozen=True)
class SortKey:
    """Deterministic sort key (stable across runs and Python versions).

    Locked requirement from the cutline spec: events MUST be sorted deterministically
    BEFORE assigning `global_seq` / `evidence_id`.

    Tie-breakers are ordered from most-semantic to least-semantic:
    1) `ts` (timestamp seconds)
    2) `event_type`
    3) `stable_payload_hash` (canonical JSON of payload, sort_keys=True)
    4) `raw_index` (original frame index; last-resort tiebreaker)

    NOTE: If new event types introduce additional fields (team_id, player_id, x/y),
    they should be included in the payload so `stable_payload_hash` captures them.
    """

    ts: int
    event_type: str
    stable_payload_hash: str
    raw_index: int


def stable_str_hash(obj: object) -> str:
    """Deterministic hash for sorting.

    Uses a canonical string representation so that dict ordering differences
    don't affect the result.
    """

    import json

    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
