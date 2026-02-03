# Demo Hardening Report (offline + deterministic)

Date: 2026-02-02

This report documents the verification + break-testing performed to make the demo judge-proof under the cutline constraints:
- fully offline (no internet)
- no runtime LLM calls
- demo mode loads from frozen artifacts only
- evidence drilldown is internal
- `broken_refs == 0` under normal conditions

## Phase A1 — Cold boot rehearsal (repo state)

### Commands executed

```sh
python scripts/generate_demo_matches.py --frames 120
python scripts/build_demo_pack.py --source auto
tar -xzf artifacts/demo_pack.tar.gz -C artifacts
python artifacts/demo_pack/verify_integrity.py --pack-root artifacts/demo_pack
pytest -q
```

### Outcome
- Pack built successfully.
- Pack verifier output: `✓ All integrity checks passed`
- Test suite: `39 passed`

## Phase A2 — Failure-mode injection

### 1) Delete one evidence panel entry

Injection: remove a single entry from `artifacts/demo_pack/processed/evidence_refs.json`.

Expected behavior:
- `/api/demo/integrity` must surface broken references clearly.

Observed behavior:
- `/api/demo/integrity` returns `broken_refs: 1` after deleting one panel.
- This is enforced by integrity checks that require a panel for **every** event evidence id.

### 2) Corrupt a core JSON store

Injection: corrupt `artifacts/demo_pack/processed/events_store.json` (invalid JSON).

Expected behavior:
- Backend should return an actionable error.
- UI should show a single actionable fix (“rebuild pack”).

Observed behavior:
- `/api/demo/health` returns HTTP `500` with detail containing `Demo pack corrupted... Fix: Rebuild the demo pack.`

## Notes / follow-ups

- Manual UI rehearsal (Start Demo → Next → Integrity panel) should still be executed on the target demo machine.
- If real match exports are available, place them under `data/demo_matches_real/` and build with `--source real`.