# Hackathon Changes — Evidence-First Assistant Coach

This document tracks the core architectural and feature work completed during the hackathon period.

## 核心成果 (Core Achievements)

### 1. Deterministic "Demo Pack" System
- **Precomputed Analytics**: Moved all logic (moment detection, pattern recognition) from runtime to a precomputed "frozen" pipeline.
- **Offline Guarantee**: The application performs **zero** runtime LLM calls or external API requests during demo mode.
- **Integrity Proofs**: Implemented `verify_integrity.py` which validates that 100% of evidence IDs in the timeline have matching evidence panels in the pack.

### 2. Evidence-First UI/UX
- **Evidence Drawer**: Created a slide-out panel that provides event-level context (±60s window) for every coach-plausible moment.
- **Scouting Report**: Implemented a "Pattern" view that aggregates tendencies across matches, each linked to verifiable evidence instances.
- **Integrity Dashboard**: Added a judge-facing panel showing `broken_refs=0` and total event counts to prove data consistency.

### 3. Verification Suite
- **Determinism Proof**: Built `verify_determinism_twice.py` to ensure the match generation and pack building pipeline is 100% repeatable (bit-for-bit identical tarball hashes).
- **Adversarial Error Handling**: Hardened the backend to detect and report demo pack corruption with actionable "Fix" instructions instead of generic stack traces.

## Timeline of Work
- **Day 1**: Core parsing engine and risk scoring implementation.
- **Day 2**: Pivot to Offline Demo Pack architecture to ensure judge-proof execution.
- **Day 3**: UI refinement, integrity dashboard, and "One-Command" automation (`make demo`).
- **Day 4**: Determinism hardening and release preparation.
