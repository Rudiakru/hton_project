### Title: Evidence-First Assistant Coach (Offline Demo)

**[🎥 Watch the 2-Minute Demo Video](https://youtu.be/PENDING_UPLOAD_PLEASE_UPDATE)**

We built an assistant coach that turns full match review into a few minutes: it automatically surfaces 3–5 “coach‑plausible” critical moments per match and generates a scouting report with evidence trails. Every insight is verifiable: click any moment or pattern to open an internal evidence panel with event details and a match‑scoped context window (±60s).

To make the demo judge‑proof, we implemented a deterministic, fully offline “demo pack” system: all analytics are precomputed into frozen JSON stores and served through a demo‑only API. The app does zero runtime compute and requires no internet during the demo. We also ship integrity and determinism proofs (double‑build identical artifacts, broken_refs=0) so judges can trust what they’re seeing. See [HACKATHON_CHANGES.md](./HACKATHON_CHANGES.md) for full technical details.

How to run: one command via `make demo` (or `scripts/run_demo.ps1` on Windows, `scripts/run_demo.sh` on mac/Linux). Alternatively, follow the three copy/paste steps in the README to build + verify the pack, run tests, and start backend/frontend demo servers.

Limitations: the demo dataset contains 6 matches, and baselines/confidence are computed within that dataset (we explicitly label confidence as low due to small n). In production, the same pipeline would ingest a team’s full match history.