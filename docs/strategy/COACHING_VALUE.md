# Coaching Value + ROI (Judge-facing)

This project is designed to **replace the slowest parts of coaching prep** with a fast, repeatable workflow that a coach can trust.

## The coaching workflow problem

Before a scrim or stage match, coaches typically spend a lot of time doing:

- **VOD scanning** to find the few moments that actually change a game.
- **Opponent scouting** to extract repeatable tendencies (and how to punish them).
- **Evidence gathering** (screenshots/notes/timestamps) so players believe the claim.

That process is effective, but it’s labor-intensive and hard to repeat consistently.

## What we automate (without demo risk)

In demo mode, everything is **offline, deterministic, and precomputed** into a frozen demo pack (`artifacts/demo_pack.tar.gz`).

The demo flow is intentionally stage-safe:

1. `Start Demo` → immediately shows a “what happened” moment + opens evidence.
2. `Next` → shows a scouting report (patterns) + opens a pattern evidence instance.
3. `Integrity` → shows that every reference in the pack is valid (`broken_refs == 0`).

## Time saved (how to frame it to judges)

We avoid overclaiming exact numbers and frame ROI as **workflow acceleration**:

- A manual review of a full match can take **30+ minutes** (often longer) before you even reach actionable takeaways.
- With our demo pack, a coach can reach:
  - **critical moments (3–5)**,
  - **a scouting report with evidence**, and
  - **a verification panel**
  in **~60–90 seconds of clicking** (and the UI responses are effectively instant because the pack is precomputed).

## Why it’s trustworthy

The core trust mechanism is: **every claim is click-to-verify**.

- Every insight links to an internal evidence panel with a **match-scoped ±60s context window**.
- The integrity verifier runs offline and proves that:
  - evidence references exist
  - context windows do not leak cross-match
  - moment counts are within spec

## What we are *not* claiming

- No league-wide statistical claims (demo pack is 6 matches).
- No runtime LLM calls.
- No heavy compute at runtime.
