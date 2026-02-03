### Verification Report (offline demo cutline)

Date: 2026-02-03

This report verifies the demo is compliant with `IMPLEMENTATION_CUTLINE_V2.md` and stage-safe offline.

#### Phase A — Build + verify demo pack offline

Commands:

```powershell
python scripts\generate_demo_matches.py --frames 120
python scripts\build_demo_pack.py
tar -xzf artifacts\demo_pack.tar.gz -C artifacts
python artifacts\demo_pack\verify_integrity.py --pack-root artifacts\demo_pack --out-json artifacts\demo_pack_integrity_report.json
```

Observed outputs:
- `verify_integrity.py`: `OK: All integrity checks passed`
- `artifacts/demo_pack_integrity_report.json`:
  - `integrity_ok: true`
  - `broken_refs: 0`
  - Match count requirement: enforced by verifier (`Expected 6 matches ...` would fail); PASS implies match count == `6`
  - `total_events: 840`
  - `total_moments: 30`
  - `total_patterns: 9`

#### Phase A — Determinism proof (double-build)

Command:

```powershell
python scripts\verify_determinism_twice.py
```

Observed output:
- `✓ Determinism verified (double-build outputs are identical)`

#### Phase A — Full test suite

Command:

```powershell
pytest -q
```

Observed output:
- `46 passed`

#### Phase A — Cold-boot demo run (machine-checked)

Automated E2E coverage (Playwright) exists for the required stage path:
- `Start Demo` → evidence drawer opens
- `Next` → scouting report + pattern evidence
- `Verification/Integrity` → `broken_refs == 0`, `match_count == 6`
- Stability: same critical path repeated **10×** (`frontend/e2e/demo-flow-stability.spec.ts`)

Notes:
- Evidence drawer header shows **match + timestamp** and UI/API are hardened to never echo raw `evidence_id`.
- Windows localhost hardening: Vite binds to IPv4 (`127.0.0.1`) and proxies `/api` to IPv4 to avoid `::1` mismatch flakes.

#### Phase A — Cold-boot demo run (human 10×)

Manual 10× repetition is still recommended on the final demo machine, but an automated 10× stability test is included and used as the primary flake-surfacing check.

#### Screenshots (internal-only proof panels)

Captured assets (repo):
- `submission_assets/screenshots/01_landing.png`
- `submission_assets/screenshots/02_start_demo_evidence.png`
- `submission_assets/screenshots/03_scouting_report.png`
- `submission_assets/screenshots/04_verification.png`

#### Flakes found

0 known flakes remaining.

Previously observed flakes and fixes:
- Start Demo race (clicked before matches/teams loaded) → Start Demo is now disabled until data is ready + actionable message.
- IPv6/IPv4 localhost mismatch → Vite binds to `127.0.0.1`, proxy targets `127.0.0.1:8000`, Playwright baseURL hardened.
