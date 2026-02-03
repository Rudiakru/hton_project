# Evidence-First Assistant Coach (Offline Demo)

[![Watch the 2-minute demo](https://img.shields.io/badge/Demo-Watch%20Video-red?style=for-the-badge&logo=youtube)](https://youtu.be/PENDING_UPLOAD_PLEASE_UPDATE)
[**Hackathon Changes Log**](./HACKATHON_CHANGES.md)

## 1) What this is
An AI assistant coach demo that surfaces critical moments and a scouting report with click-to-verify evidence. The entire demo is offline and deterministic: all analytics are precomputed into a frozen demo pack. Every insight links to event-level evidence so judges can verify claims in seconds.

## 2) Demo in 3 steps

Build + verify demo pack
```
python scripts/generate_demo_matches.py --frames 120
python scripts/build_demo_pack.py
tar -xzf artifacts/demo_pack.tar.gz -C artifacts
python artifacts/demo_pack/verify_integrity.py --pack-root artifacts/demo_pack
```

Run tests
```
pytest -q
```

Run demo mode

Backend:
```
export DEMO_PACK_ROOT=artifacts/demo_pack
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Frontend:
```
cd frontend
export REACT_APP_DEMO_MODE=true
npm run dev
```

Tip: Or use one command: `make demo` (or `scripts/run_demo.ps1` on Windows, `scripts/run_demo.sh` on mac/Linux). The script builds the pack, verifies integrity, and prints the URL to open.

**Note:** Run `make setup` first to install dependencies.

## 3) “Start Demo” stage path
Start Demo → evidence drawer opens → Next → scouting report + evidence opens → Integrity panel shows `broken_refs=0`.

## 4) Honesty / limitations (judge-safe)
- Demo dataset = 6 matches
- Baseline computed within demo dataset
- Confidence is conservative (n=6 → low)
- Demo does no runtime compute / no external calls

## 5) Architecture
Small diagram (offline path): `docs/architecture.svg`
UI → `/api/demo` → frozen pack (`events/`, `moments/`, `patterns/`, `evidence_refs`)
