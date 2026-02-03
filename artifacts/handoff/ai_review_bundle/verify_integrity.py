from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


_EVIDENCE_RE = re.compile(r"^[A-Z0-9-]+:\d{6}$")


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def verify(pack_root: Path) -> dict:
    # This verifier must run from an extracted demo pack without importing repo code.
    matches_dir = pack_root / "matches"
    processed_dir = pack_root / "processed"
    events_store = processed_dir / "events_store.json"
    moments_store = processed_dir / "moments_store.json"
    patterns_store = processed_dir / "patterns_store.json"
    evidence_refs = processed_dir / "evidence_refs.json"

    errors: list[str] = []
    required = [matches_dir, events_store, moments_store, patterns_store, evidence_refs]
    for p in required:
        if not p.exists():
            errors.append(f"Missing required path: {p}")

    if errors:
        return {
            "version": 1,
            "pack_root": str(pack_root),
            "integrity_ok": False,
            "broken_refs": len(errors),
            "errors": errors,
        }

    events_raw = _read_json(events_store)
    moments_raw = _read_json(moments_store)
    patterns_raw = _read_json(patterns_store)
    evidence_raw = _read_json(evidence_refs)

    events_by_match = events_raw.get("matches", {})
    moments_by_match = moments_raw.get("matches", {})
    patterns = patterns_raw.get("patterns", [])
    panels = evidence_raw.get("panels", {})

    if len(events_by_match) != 6:
        errors.append(f"Expected 6 matches in events_store, got {len(events_by_match)}")

    # evidence ids unique + match-scoped + format
    all_eids = []
    for match_id, events in events_by_match.items():
        for e in events:
            if e.get("match_id") != match_id:
                errors.append(f"Event match_id mismatch for {e.get('evidence_id')}")
            evidence_id = e.get("evidence_id")
            if not isinstance(evidence_id, str) or not _EVIDENCE_RE.match(evidence_id):
                errors.append(f"Invalid evidence_id format: {evidence_id}")
            else:
                all_eids.append(evidence_id)
    if len(all_eids) != len(set(all_eids)):
        errors.append("Evidence IDs are not globally unique")

    # moments 3-5 per match and refs exist
    for match_id, moments in moments_by_match.items():
        if not (3 <= len(moments) <= 5):
            errors.append(f"Match {match_id} has {len(moments)} moments (expected 3-5)")
        event_ids = {e.get("evidence_id") for e in events_by_match.get(match_id, [])}
        for m in moments:
            if not m.get("passes_validity_filter") or not m.get("validity_reasons"):
                errors.append(f"Moment {m.get('moment_id')} did not pass validity filter")
            if m.get("primary_event_ref") not in event_ids:
                errors.append(
                    f"Moment {m.get('moment_id')} primary ref missing: {m.get('primary_event_ref')}"
                )
            for r in m.get("related_event_refs", []):
                if r not in event_ids:
                    errors.append(f"Moment {m.get('moment_id')} related ref missing: {r}")

    # patterns baseline is demo-only
    for p in patterns:
        if p.get("sample_size") != 6:
            errors.append(f"Pattern {p.get('pattern_id')} sample_size must be 6")
        if p.get("confidence_level") not in {"high", "medium", "low"}:
            errors.append(f"Invalid confidence_level for {p.get('pattern_id')}")
        freq = p.get("frequency")
        if not isinstance(freq, (int, float)) or not (0.0 <= float(freq) <= 1.0):
            errors.append(f"Invalid frequency for {p.get('pattern_id')}")
        instances = p.get("instances") or []
        if not instances:
            errors.append(f"Pattern {p.get('pattern_id')} must have instances")
        for inst in instances:
            for eid in inst.get("evidence_refs", []):
                if eid not in panels:
                    errors.append(f"Pattern {p.get('pattern_id')} instance refs missing panel: {eid}")

    # panels exist for all events; context is match-scoped
    for match_id, events in events_by_match.items():
        for e in events:
            evidence_id = e.get("evidence_id")
            panel = panels.get(evidence_id)
            if panel is None:
                errors.append(f"Missing evidence panel for {evidence_id}")
                continue
            if panel.get("match_id") != match_id:
                errors.append(f"Panel match_id mismatch for {evidence_id}")
            for ctx in panel.get("context_window", []):
                if ctx.get("match_id") != match_id:
                    errors.append(f"Context window leaked match for {evidence_id}")
            for rm in panel.get("related_moments", []):
                if rm.get("match_id") != match_id:
                    errors.append(f"Related moments leaked match for {evidence_id}")

    total_events = sum(len(v) for v in events_by_match.values())
    total_moments = sum(len(v) for v in moments_by_match.values())
    total_patterns = len(patterns)

    return {
        "version": 1,
        "pack_root": str(pack_root),
        "integrity_ok": len(errors) == 0,
        "total_events": total_events,
        "total_moments": total_moments,
        "total_patterns": total_patterns,
        "broken_refs": len(errors),
        "errors": errors,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack-root", default=".")
    ap.add_argument("--out-json", default=None)
    args = ap.parse_args()
    pack_root = Path(args.pack_root).resolve()
    report = verify(pack_root)
    if args.out_json:
        out_path = Path(args.out_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    if not report.get("integrity_ok"):
        msg = report.get("errors") or ["Integrity failed"]
        raise SystemExit("\n".join(["Demo pack integrity failed:"] + [f"- {m}" for m in msg]))

    print("OK: All integrity checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
