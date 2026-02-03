from __future__ import annotations

from dataclasses import dataclass

from backend.demo_pack.schemas import DemoEvent, DemoMoment


@dataclass(frozen=True)
class ObservationMaskingMetrics:
    events_before: int
    events_after: int
    reduction_pct: int


def compute_observation_masking(
    events_by_match: dict[str, list[DemoEvent]],
    moments_by_match: dict[str, list[DemoMoment]],
    *,
    window_seconds: int = 60,
) -> dict:
    """Compute a deterministic "observation masking" metric.

    This is a judge-facing metric only. It does NOT affect evidence panels.

    Policy (deterministic):
    - Keep all high-signal events (by type).
    - Keep any event within ±window_seconds of any precomputed moment window.
    - Everything else is considered maskable background.
    """

    high_signal_types = {"TEAMFIGHT", "PATTERN"}

    kept_ids: set[str] = set()
    total_events = 0

    for match_id, events in events_by_match.items():
        total_events += len(events)

        moments = moments_by_match.get(match_id, [])
        moment_windows = [(max(0, m.start_ts - window_seconds), m.end_ts + window_seconds) for m in moments]

        for e in events:
            if e.event_type in high_signal_types:
                kept_ids.add(e.evidence_id)
                continue

            for lo, hi in moment_windows:
                if lo <= e.ts <= hi:
                    kept_ids.add(e.evidence_id)
                    break

    events_after = len(kept_ids)
    if total_events <= 0:
        reduction_pct = 0
    else:
        reduction_pct = int(round((1.0 - (events_after / total_events)) * 100.0))
        reduction_pct = max(0, min(100, reduction_pct))

    metrics = ObservationMaskingMetrics(
        events_before=total_events,
        events_after=events_after,
        reduction_pct=reduction_pct,
    )

    return {
        "status": "ok",
        "policy": {
            "high_signal_event_types": sorted(high_signal_types),
            "moment_window_seconds": int(window_seconds),
        },
        "events_before": metrics.events_before,
        "events_after": metrics.events_after,
        "reduction_pct": metrics.reduction_pct,
    }
