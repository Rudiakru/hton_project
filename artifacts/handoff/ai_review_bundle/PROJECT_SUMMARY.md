# Project Summary — Macro Health Monitor (GRID Risk-Engine)

Date: 2026-02-03

This document contains:

1. A **short summary** (executive / judge-friendly)
2. A **big summary** (detailed, technical, “how it works + how it’s verified”)

---

## 1) Short summary (executive)

**Macro Health Monitor** is an offline-capable esports coaching console for League of Legends macro analysis.
It converts match telemetry into **critical moments**, **scouting patterns**, and **evidence-first explanations**.

What makes it judge-proof:

- **Offline demo**: the UI talks only to local backend endpoints under `/api/demo/*`, which load from a frozen demo dataset via `DEMO_PACK_ROOT`.
- **Deterministic build**: the demo pack (`artifacts/demo_pack.tar.gz`) is built deterministically (bit-for-bit stable hash across successive builds).
- **Integrity proof**: an **offline verifier script is embedded inside the demo pack** (`artifacts/demo_pack/verify_integrity.py`) and checks ID format, reference integrity, match scoping, and expected counts.
- **One-command CI runner**: `scripts/run_ci_demo.ps1` and `scripts/run_ci_demo.sh` build everything, run verification + tests, start services, run Playwright E2E, and produce artifacts/logs (and screenshots/video on failure).

Demo path (what judges do): **Start Demo → Next → Integrity (broken_refs = 0)**.

---

## 2) Big summary (detailed)

### 2.1 What the product is (problem → solution)

Coaches and analysts need actionable macro insights fast, with confidence they can justify conclusions.
This project provides:

- **Critical moments** (3–5 per match) with **validity reasons**
- **Scouting report patterns** with **confidence labels** derived from sample size (demo pack uses `n=6`, so confidence is expected to be LOW)
- **Evidence panels** that open internally by stable `evidence_id` (no external replay links)

The guiding idea is *explainable, evidence-first analytics*: every insight can be traced back to a concrete evidence record.

### 2.2 Key “judge-proof” claims (offline / deterministic / verified)

#### Offline

- Demo mode uses only local endpoints under `/api/demo/*`.
- Backend data loading is controlled via `DEMO_PACK_ROOT`.
- Frontend demo UI is gated by demo env flags (`REACT_APP_DEMO_MODE=true`, and the CI runner also sets `VITE_DEMO_MODE=true`).

#### Deterministic

The demo pack artifact is designed to be reproducible:

- Deterministic JSON serialization for stores (`sort_keys=True`)
- Deterministic tar.gz creation (`backend/demo_pack/io.py`):
  - stable directory + file ordering
  - fixed metadata (uid/gid/mode/mtime)
  - deterministic gzip header (`mtime=0`, no embedded filename)
- Time-dependent benchmarks are **disabled by default** inside the pack build (real benchmarks only if `DEMO_PACK_BENCHMARKS=1`).

**Why this matters**: the sha256 of `artifacts/demo_pack.tar.gz` should match across two successive builds on a clean machine.

#### Verified (integrity proof)

The extracted pack contains a verifier that must run without importing repo code:

```sh
tar -xzf artifacts/demo_pack.tar.gz -C artifacts
python artifacts/demo_pack/verify_integrity.py --pack-root artifacts/demo_pack
```

Expected output:

```text
OK: All integrity checks passed
```

The verifier checks, among other things:

- Evidence IDs are stable and correctly formatted: `match_id:000001` (format: `^[A-Z0-9-]+:\d{6}$`)
- Evidence IDs are globally unique
- Moments exist per match (3–5) and reference existing events
- Patterns reference existing evidence panels
- Evidence panels are match-scoped (no cross-match context leakage)

### 2.3 Repository structure (high level)

Top-level overview (key parts):

- `backend/`: FastAPI application and demo-pack building/runtime logic
- `core/`: shared utilities, schemas, and analytics helpers (legacy/shared layer)
- `frontend/`: React (Vite) UI for analysis + demo console
- `scripts/`: deterministic demo data generation, demo pack build, and CI runners
- `tests/`: pytest tests (unit/contract/integration)
- `artifacts/`: build outputs (demo pack, CI logs/artifacts)
- `docs/`: additional docs (project-specific)

### 2.4 Demo data pipeline (from raw snapshot → frozen pack)

The offline demo is backed by a frozen “demo pack” containing:

- `demo_pack/matches/*.json` (6 match JSONs)
- `demo_pack/processed/events_store.json`
- `demo_pack/processed/moments_store.json`
- `demo_pack/processed/patterns_store.json`
- `demo_pack/processed/evidence_refs.json`
- `demo_pack/metadata.json` (source + dataset notes)
- `demo_pack/processed/benchmarks.json` + `demo_pack/benchmarks.md` (deterministic by default)
- `demo_pack/verify_integrity.py` (offline verifier embedded inside the pack)

Key scripts:

- `scripts/generate_demo_matches.py`
  - produces 6 deterministic demo matches derived from `data/raw/real_data.json`
  - uses deterministic numeric shifts to avoid identical frames across matches
- `scripts/build_demo_pack.py`
  - builds moments, patterns, and evidence panels and writes the frozen stores
  - writes metadata and a determinism hash summary
  - packages `artifacts/demo_pack/` into `artifacts/demo_pack.tar.gz`

### 2.5 Backend demo API (contract)

The frontend demo UI is designed to call only these endpoints (all under `/api/demo/*`):

- `/api/demo/health`
- `/api/demo/matches` and `/api/demo/teams`
- `/api/demo/show-moments?match_id=...`
- `/api/demo/analyze-moment?evidence_id=...`
- `/api/demo/scout-team?team_id=...`
- `/api/demo/integrity` (must report `broken_refs == 0` for the shipped demo pack)

The integrity endpoint is the “live” view of the same trust checks performed by the offline verifier.

### 2.6 Frontend demo UX (the staged judge path)

The demo is intentionally “selector-first” (stable, non-flaky) and built around a single obvious route:

1. Click **Start Demo**
   - loads hero match moments
   - automatically opens the first evidence panel
2. Click **Next**
   - loads scouting report patterns
   - opens the first pattern’s evidence
3. Check **Integrity / Health**
   - verify `broken_refs: 0`

For reliability, the UI provides stable E2E selectors:

- `data-testid="start-demo"`
- `data-testid="next-step"`
- `data-testid="evidence-drawer"`
- `data-testid="scouting-report"`
- `data-testid="integrity-panel"`
- `data-testid="broken-refs"`

Evidence is shown in an internal drawer (devtools feel). It is intentionally non-blocking so the main demo controls stay clickable.

### 2.7 Design system (JetBrains devtools × Cloud9 esports)

Theme goal: projector-friendly, dark, crisp, minimal chrome, strong accent color.

- Dark base (`slate-950`), subtle translucent surfaces (`bg-white/5`), soft borders (`border-white/10`)
- Cloud9-leaning cyan/sky accents for CTAs and highlights
- Tech labels and IDs use **JetBrains Mono** (via `@fontsource/jetbrains-mono`, offline-friendly)

Reference: `THEME.md`.

### 2.8 End-to-end automation (one command)

Two “single command” CI-grade runners exist:

- Windows: `scripts/run_ci_demo.ps1`
- Linux/macOS: `scripts/run_ci_demo.sh`

They perform, end-to-end:

1. Install deps (Python + Node)
2. Build demo matches
3. Build demo pack
4. Determinism self-check (build pack twice; tarball hash must match)
5. Extract pack
6. Run offline verifier (from inside extracted pack)
7. Run `pytest`
8. Start backend in demo mode
9. Start frontend in demo mode
10. Run headless Playwright E2E test that clicks the real demo path
11. Shut everything down cleanly (even on failure)

Artifacts produced under `artifacts/ci_demo/` include:

- `backend.log`, `frontend.log`, `pytest.log`, `e2e.log`
- `integrity_report.json`
- `run_summary.md` (timings + pack sha256)
- On E2E failure: `e2e_screenshot_*.png` and `e2e_video.webm` (if produced)

Example PASS run summary exists at `artifacts/ci_demo/run_summary.md`.

### 2.9 Testing strategy (what’s covered)

- `pytest` covers unit + contract/integration checks for demo pack building and determinism.
- Playwright covers the critical user path in the real UI.

Notable determinism coverage:

- `tests/contract/test_demo_pack_determinism.py` (double-build stores are identical)
- `tests/unit/test_demo_pack_deterministic_tar.py` (tar.gz determinism)

### 2.10 Constraints (explicit “do not do” rules)

To stay judge-proof and offline-friendly:

- No runtime LLM calls
- No external replay links from evidence panels
- Demo outputs must be computed from the frozen pack; no internet required for the demo path

### 2.11 How to run (human-friendly quickstart)

#### CI-grade end-to-end run (recommended)

Windows:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_ci_demo.ps1
```

Linux/macOS:

```sh
bash scripts/run_ci_demo.sh
```

#### Manual demo run (for live rehearsal)

1) Build + extract pack:

```sh
python scripts/generate_demo_matches.py --frames 120
python scripts/build_demo_pack.py
tar -xzf artifacts/demo_pack.tar.gz -C artifacts
```

2) Start backend:

```powershell
$env:DEMO_PACK_ROOT="artifacts\\demo_pack"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

3) Start frontend:

```powershell
cd frontend
$env:REACT_APP_DEMO_MODE="true"
npm run dev
```

Then open `http://127.0.0.1:5173/` and use **Start Demo → Next**.

---

### 2.12 Pointers (where to look next)

- Pitch framing: `PITCH_CHEAT_SHEET.md`
- Visual rules: `THEME.md`
- CI runner details: `scripts/run_ci_demo.ps1`, `scripts/run_ci_demo.sh`
- Demo pack build pipeline: `scripts/build_demo_pack.py`, `backend/demo_pack/io.py`
- Frontend demo console: `frontend/src/components/DemoDashboard.jsx`
- E2E test: `frontend/e2e/demo-flow.spec.ts`

---

## 3) Long summary (full project narrative)

This section is intentionally “long-form”: it’s written so a judge (or a teammate) can skim headlines quickly, *or* read end-to-end and understand exactly what the system does, how it stays offline/deterministic, and how we prove it.

### 3.1 The core pitch (what we built, in plain terms)

**Macro Health Monitor** is a coach-facing console that turns match telemetry into:

1. **Critical moments** (3–5 per match)
2. **A scouting report** (repeatable tendencies)
3. **Evidence drilldown** (click-to-verify panels with match-scoped context)

The demo is designed for harsh stage conditions:

- **No internet** required
- **No runtime LLM calls**
- **No heavy compute at runtime** (all outputs are precomputed into a frozen artifact)
- **No fragile UI path** (one safe route: `Start Demo` → `Next` → `Integrity`)

The key product promise is not “perfect analytics”; it’s **trust + speed**:

- Coaches can get to a defensible talking point fast.
- Every claim is paired with internal evidence.
- The system is deterministic and verified, so the demo cannot “mysteriously change” between runs.

### 3.2 The problem we’re solving (why coaches care)

Coaching prep is slow because it requires *both* discovery and proof:

- Discovery: find the moments that matter and identify tendencies.
- Proof: pull context so the team can agree on what happened and why.

Traditional workflows depend on VOD scanning and manual note-taking. Even if a coach suspects a tendency (“they overcommit to river around X”), they still need to justify it with examples and context.

Our approach compresses that workflow into a deterministic, evidence-first sequence:

- Start with a top moment (instant “what happened”).
- Expand into a tendency (“what repeats”).
- Drill into evidence (instant “prove it”).
- Show integrity (instant “this pack is internally consistent”).

### 3.3 The judge-proof approach: precompute everything into a frozen demo pack

The biggest demo risk in hackathon settings is relying on live services, live APIs, or live models. We avoid that by shipping a **fully offline demo pack**:

- Stored in `artifacts/demo_pack.tar.gz`
- Extracts to `artifacts/demo_pack/`
- Loaded by the backend in demo mode using `DEMO_PACK_ROOT`

In demo mode:

- The backend reads only from the extracted pack.
- The frontend calls only `/api/demo/*` endpoints.
- The E2E runner starts both services locally and validates the real UI flow.

This makes the system “judge-proof” because the demo becomes a **reproducible replay** of a known-good dataset and known-good outputs.

### 3.4 What’s inside the demo pack (data model + guarantees)

The demo pack is a small, opinionated dataset with **exactly 6 matches**. It contains:

- `matches/*.json`: raw-ish match inputs used for the pack
- `processed/events_store.json`: per-match event lists
- `processed/moments_store.json`: 3–5 surfaced moments per match
- `processed/patterns_store.json`: scouting patterns across the demo dataset
- `processed/evidence_refs.json`: evidence panels keyed by `evidence_id`
- `metadata.json`: dataset notes/scope
- `verify_integrity.py`: offline verifier embedded inside the pack

#### 3.4.1 Store schemas (key fields)

The pack stores are intentionally simple JSON (no database, no migrations, no external dependencies). The goal is to make the demo pack:

- easy to inspect with a text editor
- easy to integrity-check without importing repo code
- easy to load in a single backend process with predictable performance

At a high level:

- `events_store.json` is the *source of truth* for the stable internal reference system (`evidence_id`)
- `moments_store.json` and `patterns_store.json` are “views” that point back into events via those references
- `evidence_refs.json` materializes the “click-to-verify” payload for each reference

Minimal examples (representative fields):

`processed/events_store.json` (per match):

```json
{
  "version": 1,
  "matches": {
    "TL-C9-G2": [
      {
        "match_id": "TL-C9-G2",
        "ts": 120,
        "game_time": "2:00",
        "event_type": "TEAMFIGHT",
        "payload": {"frame_idx": 12, "teams": 2, "detected": true},
        "global_seq": 2,
        "evidence_id": "TL-C9-G2:000002"
      }
    ]
  }
}
```

`processed/moments_store.json` (3–5 per match):

```json
{
  "version": 1,
  "matches": {
    "TL-C9-G2": [
      {
        "match_id": "TL-C9-G2",
        "moment_id": "TL-C9-G2:M01",
        "title": "Critical Moment",
        "description": "At 2:00, detected teamfight relevant to macro decision-making.",
        "start_ts": 90,
        "end_ts": 150,
        "passes_validity_filter": true,
        "validity_reasons": ["Selected from TEAMFIGHT candidates", "Deterministic spacing rule applied"],
        "primary_event_ref": "TL-C9-G2:000002",
        "related_event_refs": []
      }
    ]
  }
}
```

`processed/patterns_store.json` (demo-only tendencies):

```json
{
  "version": 1,
  "patterns": [
    {
      "team_id": "TL",
      "pattern_id": "TL:river_risk",
      "label": "River Risk",
      "description": "Team enters river with higher contest risk.",
      "confidence_level": "low",
      "frequency": 0.5,
      "sample_size": 6,
      "instances": [
        {"match_id": "TL-C9-G2", "evidence_refs": ["TL-C9-G2:000002"], "note": "Derived from moment TL-C9-G2:M01"}
      ]
    }
  ]
}
```

`processed/evidence_refs.json` (materialized “proof panel”):

```json
{
  "version": 1,
  "panels": {
    "TL-C9-G2:000002": {
      "evidence_id": "TL-C9-G2:000002",
      "match_id": "TL-C9-G2",
      "event": {"match_id": "TL-C9-G2", "ts": 120, "event_type": "TEAMFIGHT", "evidence_id": "TL-C9-G2:000002"},
      "context_window": [{"match_id": "TL-C9-G2", "ts": 60, "event_type": "SNAPSHOT"}],
      "feature_snapshot": {"event_type": "TEAMFIGHT", "ts": 120, "match_scoped": true},
      "related_moments": [{"match_id": "TL-C9-G2", "moment_id": "TL-C9-G2:M01"}]
    }
  }
}
```

These examples are intentionally plain: judges can understand the shapes quickly, and developers can debug by reading a single JSON file.

#### 3.4.2 The reference graph (how everything links)

You can think of the pack as a small DAG:

- `events_store.json` defines **all** `evidence_id`s (stable keys)
- `moments_store.json` references events via `primary_event_ref` (+ optional `related_event_refs`)
- `patterns_store.json` references events via `instances[*].evidence_refs[*]`
- `evidence_refs.json` must contain a panel for every referenced `evidence_id`

Integrity is basically “every pointer resolves” + “no match_id leaks.”

The most important invariant is the internal reference system:

- Every event gets a stable `evidence_id`.
- Moments and patterns refer to events via those stable IDs.
- Evidence panels are keyed by the same IDs.

#### Evidence IDs

Evidence IDs are stable and globally unique across the pack:

- Format: `{match_id}:{global_seq:06d}`
- Example: `TL-C9-G2:000002`

This is enforced by the offline verifier (`verify_integrity.py`) and by API/integration tests.

**How IDs are produced (deterministically):**

- We first synthesize a list of raw events.
- We then **sort** events deterministically (by timestamp, event type, a stable payload hash, and the raw frame index).
- Only after sorting do we assign `global_seq = 1..N` and compute `evidence_id = {match_id}:{global_seq:06d}`.

This “sort-before-seq” rule is locked by the cutline spec and implemented in `backend/demo_pack/builder.py:synthesize_events()`.

#### Moments (3–5 per match, always)

Each match surfaces 3–5 moments and each moment includes:

- A title + description
- A validity decision (`passes_validity_filter`) and `validity_reasons`
- A `primary_event_ref` (must exist in that match)
- Optional `related_event_refs` (also must exist in that match)

The verifier explicitly rejects packs where a match has fewer than 3 or more than 5 moments.

**How moments are selected (deterministically):**

In `backend/demo_pack/builder.py:build_moments()` we select moments with a conservative spacing rule:

- Candidates: events of type `TEAMFIGHT` and `PATTERN`
- Spacing: keep events at least `90s` apart (to avoid redundant adjacent windows)
- Cap: keep up to `5`
- Fallback: if fewer than `3`, select from `SNAPSHOT` events with the same spacing rule
- Final pad: if the dataset is tiny (or heuristics return too few), pad with earliest remaining events

This guarantees every match has *something demoable* while keeping the process deterministic.

#### Evidence panels (match-scoped by construction)

For every `evidence_id`, we precompute an internal evidence panel payload:

- Event details (`match_id`, `ts`, `game_time`, `event_type`)
- A **±60s context window** (events from the same match only)
- Related moments (same match only)

Concretely, in `backend/demo_pack/builder.py:build_evidence_panels()`:

- Context window is computed as: `ctx = [event for event in events if (ts-60) <= event.ts <= (ts+60)]`
- Related moments are: `related = [moment for moment in moments if moment.start_ts <= ts <= moment.end_ts]`
- A small `feature_snapshot` object is included (currently minimal and explicitly match-scoped)

**No cross-match contamination** is allowed. The verifier rejects any panel/context/moment that leaks a different `match_id`.

### 3.5 How determinism is achieved (and why it matters)

Determinism means: if you run the build twice on a clean machine, you get the same outputs.

We treat determinism as a feature, not an accident:

1. **Sort before sequencing**: events are deterministically sorted before assigning `global_seq` and `evidence_id`.
2. **Stable JSON output**: stores are written with sorted keys.
3. **Deterministic archive**: `demo_pack.tar.gz` is built with stable file order and fixed metadata.
4. **No time-dependent content by default**: benchmark placeholders are deterministic unless explicitly enabled.

Concretely:

- `backend/demo_pack/builder.py:synthesize_events()` sorts events via a stable sort key *before* numbering them.
- `backend/demo_pack/io.py:pack_to_tar_gz()` fixes tar entry metadata (`uid/gid/mode/mtime`) and gzip header `mtime=0`.
- `scripts/build_demo_pack.py` disables wall-clock benchmarks by default (`DEMO_PACK_BENCHMARKS=1` opt-in only).

#### 3.5.1 Deterministic archive details (tar + gzip)

Archive determinism is a common “gotcha”: even if the JSON contents match, `tar.gz` hashes can differ because of:

- file ordering in the archive
- file metadata (mtime/uid/gid/mode)
- gzip header embedding a timestamp or original filename

We make this judge-proof by constructing tar entries manually in a stable order and forcing:

- `mtime = 0`
- `uid = 0`, `gid = 0`, empty `uname/gname`
- stable directory creation inside the archive
- gzip header `mtime=0` and empty filename

Implementation: `backend/demo_pack/io.py:pack_to_tar_gz()`.

This matters for judges because it converts “trust me” into “hash it.”

### 3.6 Integrity verification: two layers (offline verifier + live endpoint)

We provide two complementary integrity mechanisms:

1) **Offline verifier (in-pack)**

After extracting the pack, run:

```sh
python artifacts/demo_pack/verify_integrity.py --pack-root artifacts/demo_pack
```

This script must work **without importing repo code**, so it can be treated as a self-contained proof artifact.

#### 3.6.1 What the offline verifier checks (in plain English)

The verifier in `scripts/verify_integrity.py` (copied into the pack at build time) checks:

- Pack structure exists (`matches/`, `processed/` stores)
- Exactly `6` matches present in `events_store.json`
- Every event’s `evidence_id` matches `^[A-Z0-9-]+:\d{6}$` and is globally unique
- Every moment:
  - exists under a match id
  - count is `3–5` per match
  - passed validity filtering and has non-empty `validity_reasons`
  - references an event (`primary_event_ref` and any `related_event_refs` must exist)
- Every pattern:
  - has `sample_size == 6`
  - has a valid confidence label (`high|medium|low`)
  - references evidence that has a corresponding panel in `evidence_refs.json`
- Every evidence panel:
  - exists for every event
  - is match-scoped (`panel.match_id`, all `context_window[*].match_id`, and all `related_moments[*].match_id` must equal the owning match)

The output summary is intentionally small (`broken_refs`, totals, list of errors) so it can be pasted into logs and judged quickly.

2) **Backend integrity endpoint**

When running the backend in demo mode, call:

- `GET /api/demo/integrity`

This endpoint returns a summary including `broken_refs` and should be `0` for the shipped demo pack.

In practice, our CI runner writes the verifier output to:

- `artifacts/ci_demo/integrity_report.json`

Example (from a passing run):

```json
{
  "broken_refs": 0,
  "integrity_ok": true,
  "total_events": 840,
  "total_moments": 30,
  "total_patterns": 9
}
```

### 3.7 The “one command” proof: CI-grade runner + artifacts

The strongest way to convince judges (and ourselves) is to remove humans from verification.

We ship two single-command CI runners:

- `scripts/run_ci_demo.ps1` (Windows)
- `scripts/run_ci_demo.sh` (Linux/macOS)

Each runner performs end-to-end verification:

1. Installs dependencies
2. Builds demo matches
3. Builds the demo pack
4. Proves determinism by building the pack twice and comparing tarball sha256
5. Extracts and runs the offline verifier from inside the extracted pack
6. Runs all `pytest`
7. Starts backend in demo mode
8. Starts frontend in demo mode
9. Runs Playwright headless E2E through the real UI
10. Tears everything down cleanly even on failure

It always leaves behind an artifact bundle under `artifacts/ci_demo/`:

- `run_summary.md` (timings + pack hash)
- `backend.log`, `frontend.log`, `pytest.log`, `e2e.log`
- `integrity_report.json`
- On E2E failure: screenshots/videos for debugging

This makes the project “audit-friendly”: the runner output is something you can hand to someone else and say, “Here is the proof trail.”

#### 3.7.1 What `artifacts/ci_demo/` looks like (and how to read it)

On a typical successful run, you’ll see:

```text
artifacts/ci_demo/
  run_summary.md
  integrity_report.json
  backend.log
  frontend.log
  pytest.log
  e2e.log
  frontend_build.log
  build_matches.log
  build_pack.log
  build_pack_2.log
  extract_pack.log
  offline_verify.log
  playwright/            # raw Playwright output (kept for debugging)
```

If E2E fails, the runner copies the most useful debugging artifacts to stable filenames:

- `e2e_screenshot_0.png`, `e2e_screenshot_1.png`, ...
- `e2e_video.webm` (if Playwright video recording is enabled)

This is deliberate: when something breaks on stage (or in CI), you want one folder you can zip and hand to a teammate.

### 3.8 The UI: built to feel like a professional devtool on stage

The frontend goal is: **one obvious route** + **high contrast** + **large tap targets** + **instant feedback**.

In demo mode the UI emphasizes judge-safe concepts:

- “Offline / Deterministic / Verified” badges
- Dataset scope callout (“Demo pack = 6 matches… baselines computed within pack”)
- Coach-language headings (“What happened / Why this matters / What to do next”)

To support reliable automation, we add stable selectors like:

- `data-testid="start-demo"`
- `data-testid="next-step"`
- `data-testid="evidence-drawer"`
- `data-testid="scouting-report"`
- `data-testid="integrity-panel"`
- `data-testid="broken-refs"`

And we keep the evidence drawer **non-blocking** (so it never breaks the demo route).

#### 3.8.1 Where the demo flow lives in the code

- Demo console: `frontend/src/components/DemoDashboard.jsx`
  - `Start Demo` (`data-testid="start-demo"`) triggers:
    - `GET /api/demo/show-moments`
    - then `GET /api/demo/analyze-moment` on the top moment
  - `Next` (`data-testid="next-step"`) triggers:
    - `GET /api/demo/scout-team`
    - then opens the first pattern instance evidence (if present)
- Evidence drawer: `frontend/src/components/EvidenceDrawer.jsx`
  - right-side panel with coach-facing header (`match vs match • Game N @ mm:ss`)
  - raw `evidence_id` is behind a collapsed “Technical details” disclosure
- Banner: `frontend/src/components/DemoBanner.jsx`
  - “Offline / Deterministic / Verified” badges and dataset scope note

#### “Don’t show raw IDs to judges”

Internally, we use `evidence_id` to guarantee stable references.
But judge-facing UI defaults to *match + time labels*; raw IDs live behind optional “Technical details” (useful for debugging and E2E reliability without confusing the audience).

### 3.9 What exactly the E2E test proves

The Playwright test (`frontend/e2e/demo-flow.spec.ts`) clicks the real route:

1. Open app
2. Click `Start Demo`
3. Assert evidence drawer opens and shows a coach-facing title
4. Click `Next`
5. Assert scouting report is visible
6. Optionally open the first pattern evidence instance
7. Scroll to integrity panel and assert `broken_refs` shows `0`

This test is deliberately conservative: it uses stable `data-testid` selectors and avoids fragile CSS selectors.

#### 3.9.1 How E2E is wired (base URL + deterministic expectations)

The CI runner starts backend + frontend locally and passes the frontend URL to Playwright via:

- `E2E_BASE_URL` (for example: `http://127.0.0.1:5173`)

The E2E test intentionally asserts “stage invariants” rather than internal implementation details:

- evidence drawer is visible
- scouting report is visible
- integrity panel shows `broken_refs == 0`

This keeps the test stable even if we restyle UI components.

### 3.10 Failure modes are designed to be actionable

We explicitly test and support “what happens when something is wrong,” because judges will inevitably encounter failure modes in other hackathon demos.

Examples:

- If the backend isn’t reachable, the UI shows a banner with the exact fix command (`DEMO_PACK_ROOT` + `uvicorn`).
- If the demo pack is corrupted (e.g., a missing evidence panel), the offline verifier fails with a clear remediation message.

The principle is: **no scary stack traces** and no ambiguous “something went wrong.” Every error should tell you what to do next.

#### 3.10.1 Adversarial failure injection (what we actually tried)

We don’t just hope errors look good; we intentionally break a known-good pack to confirm we get judge-readable failures.

Example injection:

- Copy the extracted pack
- Delete one evidence panel entry from `processed/evidence_refs.json`
- Re-run `verify_integrity.py`

Expected result: verifier fails with a message like:

```text
Demo pack integrity failed:
- Missing evidence panel for TL-C9-G2:000002
```

This is the exact “failure-mode surfacing” requirement from `IMPLEMENTATION_CUTLINE_V2.md`.

### 3.11 Documentation that supports a winning submission

We keep several documents to make the project easy to defend:

- `IMPLEMENTATION_CUTLINE_V2.md`: locked spec for the offline deterministic demo
- `PITCH_CHEAT_SHEET.md`: judge-safe pitch bullets + Q&A
- `COACHING_VALUE.md`: ROI framing (time saved, workflow compression)
- `VALIDATION.md`: humble validation notes and limitations (demo dataset only)
- `THEME.md`: design rules (JetBrains devtools × Cloud9 esports)
- `DEMO_VIDEO_SCRIPT.md`: backup 90–120s talk track for a recorded demo

### 3.12 Explicit limitations (why we don’t overclaim)

This project is designed to win on reliability and evidence trails.
To stay defensible:

- We do not claim league-wide accuracy from a 6-match demo dataset.
- Pattern confidence is sample-size derived; demo uses `n=6`, so confidence is expected to be LOW.
- We do not require external replay links or live auth.
- We do not use runtime LLM calls.

#### 3.12.1 Non-goals (things we intentionally avoided for judge safety)

- No claims like “87% accuracy” unless we can fully defend methodology and dataset.
- No significance testing / p-values (easy to interrogate, low demo value).
- No live data ingestion during the demo path.
- No external replay links (auth/timestamp formats are brittle; judges can’t validate them offline).

### 3.13 If we had more time (safe extension points)

Without changing the demo-safe core, future work could include:

- Larger offline packs (still deterministic) for stronger pattern baselines
- Better moment labeling templates (still deterministic)
- More structured “coach actions” for each pattern (playbook-like)
- Additional E2E scripts for screenshot/video capture (already scaffolded via `CAPTURE_SCREENSHOTS=1`)

The important point is that the architecture already supports production hardening: content is precomputed, references are stable, and integrity is measurable.
