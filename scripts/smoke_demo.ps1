$ErrorActionPreference = "Stop"

python scripts\generate_demo_matches.py --frames 120
python scripts\build_demo_pack.py

tar -xzf artifacts\demo_pack.tar.gz -C artifacts
python artifacts\demo_pack\verify_integrity.py --pack-root artifacts\demo_pack

pytest -q

Write-Host ''
Write-Host 'Smoke OK' -ForegroundColor Green
Write-Host 'Next (manual):'
Write-Host '  $env:DEMO_PACK_ROOT=artifacts\demo_pack'
Write-Host '  python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000'
Write-Host '  cd frontend; $env:REACT_APP_DEMO_MODE=true; npm run dev'
