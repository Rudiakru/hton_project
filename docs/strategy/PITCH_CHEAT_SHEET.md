# 📋 Pitch Cheat Sheet: Offline Scouting Report + Evidence Console

## 🚀 The product claim (judge-safe)

“We turn match telemetry into a **scouting report you can trust**: critical moments + tendencies + click-to-verify evidence — all **offline and deterministic**.”

## 📊 Proofs (what we can defend)

### 0. Judge-proof demo claims (Offline / Deterministic / Verified)

**What’s offline + deterministic**
- Demo UI talks only to local backend endpoints under `/api/demo/*` loading from `DEMO_PACK_ROOT`.
- Demo pack is a frozen dataset (6 matches) with stable evidence IDs: `match_id:000001`.
- Demo pack archive hash is stable across runs (CI prints `demo_pack.tar.gz sha256`).

**What’s precomputed (within the demo pack only)**
- Critical moments (3–5 per match) + validity reasons.
- Scouting patterns + confidence derived from sample size (demo uses `n=6`, so confidence is LOW).
- Evidence panels (no external replay links) and match-scoped context windows.
- Benchmarks + context-efficiency metric (observation masking) computed at build-time.

**Where the integrity proof lives**
- Offline verifier embedded in the pack: `artifacts/demo_pack/verify_integrity.py` (runs with no repo imports).
- Backend integrity endpoint: `/api/demo/integrity`.
- CI artifact output: `artifacts/ci_demo/integrity_report.json` (and logs/screenshots on failure).

### What we show in the live demo

- **Start Demo** → opens a top moment + evidence panel (match-scoped context).
- **Next** → opens scouting report patterns + opens evidence instance.
- **Integrity** → shows everything is internally consistent (`broken_refs == 0`).

### Validation (honest)

- We describe outputs as **observed tendencies in the demo dataset** (6 matches), not league-wide truth.
- Confidence is sample-size derived; demo uses `n=6` so confidence is **LOW**.
- Full write-up: `VALIDATION.md`.

## 💡 Quick Q&A for judges

**Q: Why no runtime AI / no internet?**

- **A:** Reliability. The demo is designed to work under worst-case stage conditions (offline). All insights are precomputed into the demo pack.

**Q: How accurate is this?**

- **A:** We don’t overclaim. In the demo dataset we show observed tendencies with low confidence labels and always provide evidence drilldown.

**Q: What’s the business / coaching value?**

- **A:** It compresses prep time: fast triage of what happened, what tends to repeat, and evidence to align players.
