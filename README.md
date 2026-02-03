# Offline Scouting Demo — Judge‑Ready

An offline, deterministic demo that turns League of Legends match telemetry into:

- Critical Moments with an internal evidence drawer (match‑scoped context)
- Scouting Report patterns with click‑to‑verify example evidence
- Integrity panel proving `broken_refs: 0` on a frozen demo pack

Quickstart (Windows)
```powershell
$env:DEMO_PACK_ROOT="artifacts\demo_pack"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
```powershell
cd frontend
$env:VITE_DEMO_MODE="true"
npm run dev -- --host 127.0.0.1 --port 5173
```

Quickstart (mac/Linux)
```sh
export DEMO_PACK_ROOT="artifacts/demo_pack"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
```sh
cd frontend
export VITE_DEMO_MODE=true
npm run dev -- --host 127.0.0.1 --port 5173
```

Then: Start Demo → Next → Integrity (expect `broken_refs: 0`, `match_count: 6`).

More details
- Checklist (commands for judges): `CHECKLIST_JUDGE_READY.md`
- Verified outputs and determinism proof: `VERIFICATION_REPORT.md`

Known limitations
- Demo dataset size is 6 matches → conservative confidence (LOW).
- Fully offline: no internet, no runtime LLM calls, no heavy compute at runtime.
