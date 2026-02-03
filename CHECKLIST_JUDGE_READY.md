### Judge-Ready Checklist

#### Exact commands (Windows PowerShell)

- Build + verify demo pack offline
```
python scripts\generate_demo_matches.py --frames 120
python scripts\build_demo_pack.py
# If you need extracted pack for manual demo:
tar -xzf artifacts\demo_pack.tar.gz -C artifacts
python artifacts\demo_pack\verify_integrity.py --pack-root artifacts\demo_pack
```
- Run tests
```
.\.venv\Scripts\pytest -q
```
- Start backend (offline demo)
```
$env:DEMO_PACK_ROOT="artifacts\demo_pack"; .\.venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
- Start frontend (demo mode)
```
cd frontend
$env:VITE_DEMO_MODE="true"
npm run dev -- --host 127.0.0.1 --port 5173
```

#### Exact commands (macOS/Linux)

- Build + verify demo pack offline
```
python3 scripts/generate_demo_matches.py --frames 120
python3 scripts/build_demo_pack.py
# If you need extracted pack for manual demo:
mkdir -p artifacts && tar -xzf artifacts/demo_pack.tar.gz -C artifacts
python3 artifacts/demo_pack/verify_integrity.py --pack-root artifacts/demo_pack
```
- Run tests
```
pytest -q
```
- Start backend (offline demo)
```
export DEMO_PACK_ROOT="artifacts/demo_pack"
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
- Start frontend (demo mode)
```
cd frontend
VITE_DEMO_MODE=true npm run dev -- --host 127.0.0.1 --port 5173
```

#### 3-minute demo flow

1) Click "Start Demo" — evidence drawer opens with match @ time header (no raw evidence_id).
2) Click "Next" — scouting report opens; click first pattern "Open example evidence" to show proof.
3) Scroll to Verification — shows All insights verified ✓, broken_refs: 0, match_count: 6.

#### Integrity + tests

- Offline verifier: `python artifacts/demo_pack/verify_integrity.py --pack-root artifacts/demo_pack` → integrity_ok true, broken_refs 0.
- Tests: `pytest -q` → all green.

#### Known limitations (explicit)

- Demo dataset is 6 matches; confidence labels are conservative (n=6 → LOW).
- Offline deterministic demo only; no league-wide claims.
- No internet or runtime LLM calls during demo; all insights precomputed in the demo pack.
