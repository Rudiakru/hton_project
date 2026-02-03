# Validation (honest, demo-dataset only)

This project’s demo mode is deliberately conservative:

- **Offline / deterministic** demo pack (6 matches).
- **No runtime LLM calls**.
- **No heavy compute at runtime** (insights are precomputed into the pack).

Because the demo pack is small (and may be synthetic-derived depending on what’s available locally), validation here is **not a claim of competitive accuracy across the league**. It’s a sanity check that:

1. the surfaced insights look *plausible* and coach-readable,
2. the evidence drilldown supports the claim,
3. the system doesn’t hallucinate references.

## What we validated

### Hold-out matches reviewed (2)

We manually reviewed the full “Start Demo → Next → Integrity” flow and then inspected the surfaced “critical moments” for two matches:

- `TL-C9-G2`
- `C9-100-G2`

For each match, the demo pack surfaced **5 moments** (within the cutline requirement of 3–5).

### Labeling rubric (minimal, defensible)

For each surfaced moment, we labeled:

- **Coach usefulness (Yes/Maybe/No):** Would a coach plausibly pause here to discuss a decision?
- **Evidence adequacy (Pass/Fail):** Does the evidence panel show a match-scoped context window and related info without broken links?

## Results (demo-safe)

### Moment coverage (2 matches)

In both hold-out matches, the surfaced moments were deterministic “decision points” spaced through the early-to-mid game timeline.

Example moment windows from the pack:

- `TL-C9-G2`: `0–30s`, `60–120s`, `150–210s`, `240–300s`, `330–390s`
- `C9-100-G2`: `0–30s`, `60–120s`, `150–210s`, `240–300s`, `330–390s`

**Coach usefulness (qualitative):**

- **Maybe** for most moments in the synthetic-derived pack: they function well as structured “review anchors” (formation snapshots / pacing checkpoints), but they are not as rich as real “kill/objective/teamfight” event moments.

**Evidence adequacy:**

- **Pass**: evidence panels open consistently and show a match-scoped ±60s context window.
- Integrity proof stays clean: `broken_refs == 0`.

## Limitations (explicit)

- The demo dataset is **only 6 matches**, and may be **synthetic-derived** if real exports aren’t present.
- This validation is a check of **consistency + evidence integrity**, not a benchmark of esports truth.
- For larger, real datasets, we expect “critical moments” to include more semantically meaningful triggers (teamfights/objectives), but that is outside this locked demo pack scope.
