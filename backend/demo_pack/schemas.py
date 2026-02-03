from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class DemoEvent(BaseModel):
    match_id: str
    # seconds from match start
    ts: int
    # human readable (MM:SS)
    game_time: str
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)

    evidence_id: str
    global_seq: int


class DemoMoment(BaseModel):
    match_id: str
    moment_id: str
    title: str
    description: str
    start_ts: int
    end_ts: int

    passes_validity_filter: bool
    validity_reasons: list[str]

    primary_event_ref: str
    related_event_refs: list[str] = Field(default_factory=list)


ConfidenceLevel = Literal["high", "medium", "low"]


class PatternInstance(BaseModel):
    match_id: str
    evidence_refs: list[str]
    note: str | None = None


class DemoPattern(BaseModel):
    team_id: str
    pattern_id: str
    label: str
    description: str
    confidence_level: ConfidenceLevel
    frequency: float
    sample_size: int
    instances: list[PatternInstance]


class EvidencePanel(BaseModel):
    evidence_id: str
    match_id: str
    event: DemoEvent
    context_window: list[DemoEvent]
    feature_snapshot: dict[str, Any] = Field(default_factory=dict)
    related_moments: list[DemoMoment] = Field(default_factory=list)
