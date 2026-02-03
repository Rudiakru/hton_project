#!/usr/bin/env bash
set -euo pipefail

python scripts/generate_demo_matches.py --frames 120
python scripts/build_demo_pack.py

tar -xzf artifacts/demo_pack.tar.gz -C artifacts
python artifacts/demo_pack/verify_integrity.py --pack-root artifacts/demo_pack

pytest -q

echo ""
echo "✓ Smoke OK"
echo "Next (manual):"
echo "  export DEMO_PACK_ROOT=artifacts/demo_pack"
echo "  python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"
echo "  cd frontend && export REACT_APP_DEMO_MODE=true && npm run dev"
