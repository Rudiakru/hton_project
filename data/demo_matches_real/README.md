# Real demo matches (offline inputs)

Place **6 real match JSON files** in this folder to build a demo pack from real inputs.

Requirements (per `IMPLEMENTATION_CUTLINE_V2.md`):
- Exactly **6** files with `.json` extension.
- Each file must be a valid match export and must include a stable `match_id` (or the filename stem will be used).

Build commands:

```sh
# Prefer real if present; otherwise falls back to synthetic
python scripts/build_demo_pack.py --source auto

# Force real only (fails with a clear error if 6 files are not present)
python scripts/build_demo_pack.py --source real
```

Note: This repo does **not** ship real match exports by default.