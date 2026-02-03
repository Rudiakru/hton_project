You are Junie, acting as a release engineer + adversarial QA for our hackathon submission.

0) Mission

We have a fully offline, deterministic “demo pack” system. Your job is to:

Verify the repo is truly demo-proof (offline, deterministic, no runtime compute/LLM).

Break it on purpose (corrupt/missing files, wrong env vars, cold boot) and ensure it fails gracefully.

Fix any issues you find (code, tests, docs, scripts).

Execute the next steps: cold-boot UI rehearsal + backup demo video checklist + submission hardening.

1) Non-negotiable constraints (do not violate)

Demo mode must load only from artifacts/demo_pack via DEMO_PACK_ROOT. No internet. No runtime analytics compute.

Evidence IDs are locked to: {match_id}:{global_seq:06d} (e.g., TL-C9-G2:000001), and must be deterministic across builds.

Evidence panels must be match-scoped (no cross-match contamination) with ±60s context windows.

Moments must always yield 3–5 coach-plausible moments per match (validity filter + fallback is allowed).

The “Start Demo” UI flow must always work on a cold boot: select hero match/team → load moments → open top moment evidence drawer → Next → open scouting report + first pattern evidence.

All integrity metrics must show broken_refs == 0.

These constraints are part of our cutline and contract tests. See the acceptance tests style in our implementation cutline doc.

IMPLEMENTATION_CUTLINE

IMPLEMENTATION_CUTLINE

2) First pass: reproduce from scratch (no assumptions)

From a clean environment (fresh venv + fresh node_modules):

A. Build the demo pack

Run:

python scripts/generate_demo_matches.py --frames 120

python scripts/build_demo_pack.py

Extract:

tar -xzf artifacts/demo_pack.tar.gz -C artifacts

Run offline integrity check (must not import repo code):

python artifacts/demo_pack/verify_integrity.py --pack-root artifacts/demo_pack

This must succeed and confirm structure, ID format, reference integrity, moment counts, and panel consistency.

B. Determinism proof

Run the “build twice → identical artifacts” proof:

pytest -q tests/contract/test_demo_pack_determinism.py

python scripts/verify_determinism_twice.py

If it fails: diagnose which non-determinism source remains (ordering, hashing, serialization, timestamps) and fix until it passes.

C. Full tests

pytest -q must pass fully.

3) Second pass: adversarial failure-mode injection

Intentionally break things and confirm failures are clear and actionable (not stack traces to judges):

Missing DEMO_PACK_ROOT

DEMO_PACK_ROOT points to wrong folder

Corrupt one of the JSON stores

Delete one evidence panel entry (simulate missing evidence_id)

Cross-match contamination attempt: ensure tests prevent it

Frontend starts before backend (should show friendly “backend not ready” state)

Where behavior isn’t judge-proof, fix:

API should return human-readable remediation (“Demo pack corrupted… rebuild pack”)

UI should show a stable error panel with exact fix steps.

4) Third pass: verify the demo API surface matches spec

Spin backend in demo mode and hit endpoints:

/api/demo/health

/api/demo/matches, /api/demo/teams

/api/demo/show-moments?match_id=...

/api/demo/analyze-moment?evidence_id=...

/api/demo/scout-team?team_id=...

/api/demo/integrity (must report broken_refs == 0)

Add/adjust integration tests if anything isn’t covered.

5) Fourth pass: verify “judge psychology” alignment in-product

Our judging pillars are: Technological Implementation, Design, Potential Impact, Quality of Idea.

doc


Make sure the UI/README explicitly demonstrates:

Reproducibility / offline reliability (one command / smoke scripts)

Evidence-first explainability (click to verify)

Honest uncertainty handling (small sample warnings)

ROI/time-saved metrics (measured, not marketing)

This alignment is central to judge expectations.

hackaton_jet

doc

6) Next steps you must complete (judge-ready)
(1) Cold-boot demo rehearsal checklist (manual)

On the target machine:

Start backend + frontend in demo mode

Click Start Demo

Confirm evidence drawer opens immediately

Click Next

Confirm scouting report loads and first pattern evidence opens

Open Integrity panel → confirm broken_refs: 0
Repeat 10× and record any flake.

If you find flake: fix it (race conditions, async state, caching, bad default selection).

(2) Backup demo video (90–120s) plan + script

Produce a tight recording plan:

Start Demo → evidence drilldown → Next → pattern evidence → integrity panel → closing “offline / deterministic”
Also create a spoken narration script (short, confident, honest).

(3) Submission hardening

Ensure README has:

one-command / smoke scripts for macOS/Linux + PowerShell

what demo mode does/doesn’t do

dataset honesty (demo baseline is within 6 matches)

troubleshooting section

Ensure repo has no stray artifacts, and CI-friendly commands.

7) Output format (what you deliver back to me)

Return a single report with:

✅/❌ checklist of every step above

Any bugs found + PR-ready fix summary

Demo rehearsal results (10×)

Final “ship readiness” verdict + remaining risks

If time remains: 1–2 safe improvements that increase judge score without risking determinism.

8) Scope cutline (don’t propose risky additions)

Do not add runtime tool-calling, external replay links, live GRID ingestion, or anything that can break offline determinism. If you propose improvements, they must be offline + deterministic + testable.

Your “are we enough to win?” score (0–10), critically

Score: 7.8 / 10 chance to win (not “place”, but win).

Why this is legitimately strong:

You’re nailing the #1 hackathon failure mode: demo fragility. Your deterministic, offline pack + integrity proofs is exactly what judges call “engineering quality / reproducibility.”

doc

You’re aligned with coaching usability: actionability + evidence drilldown (coach can verify claims fast).

doc

You added judge-facing “credibility artifacts” (integrity, benchmarks/masking), which is the kind of “show your work” that helps with JetBrains researchers and infra-minded judges