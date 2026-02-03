#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ART_DIR="$ROOT_DIR/artifacts/ci_demo"

BACKEND_LOG="$ART_DIR/backend.log"
FRONTEND_LOG="$ART_DIR/frontend.log"
PYTEST_LOG="$ART_DIR/pytest.log"
SUMMARY="$ART_DIR/run_summary.md"
INTEGRITY_JSON="$ART_DIR/integrity_report.json"

mkdir -p "$ART_DIR"
rm -rf "$ART_DIR"
mkdir -p "$ART_DIR"

BACK_PID=""
FRONT_PID=""

ts_ms() {
  python -c "import time; print(int(time.time()*1000))"
}

sha256_file() {
  local path="$1"
  python - <<PY "$path"
import hashlib
import sys
from pathlib import Path

p = Path(sys.argv[1])
h = hashlib.sha256()
with p.open('rb') as f:
    for chunk in iter(lambda: f.read(1024 * 1024), b''):
        h.update(chunk)
print(h.hexdigest())
PY
}

wait_http() {
  local url="$1"
  local timeout_s="$2"
  local t0
  t0="$(ts_ms)"
  while true; do
    python - <<PY "$url" 1>/dev/null 2>&1 && return 0
import sys
import urllib.request

url = sys.argv[1]
with urllib.request.urlopen(url, timeout=1) as r:
    if r.status != 200:
        raise SystemExit(1)
PY

    local t1
    t1="$(ts_ms)"
    local elapsed_s=$(( (t1 - t0) / 1000 ))
    if (( elapsed_s >= timeout_s )); then
      return 1
    fi
    sleep 0.2
  done
}

cleanup() {
  set +e
  if [[ -n "$FRONT_PID" ]]; then
    kill "$FRONT_PID" 2>/dev/null || true
  fi
  if [[ -n "$BACK_PID" ]]; then
    kill "$BACK_PID" 2>/dev/null || true
  fi
  wait "$FRONT_PID" 2>/dev/null || true
  wait "$BACK_PID" 2>/dev/null || true
}

trap cleanup EXIT

START_ALL="$(ts_ms)"
echo "# CI Demo Run Summary" > "$SUMMARY"
echo "" >> "$SUMMARY"
echo "- Started: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$SUMMARY"

step() {
  echo "" >> "$SUMMARY"
  echo "## $1" >> "$SUMMARY"
}

fail() {
  echo "" >> "$SUMMARY"
  echo "### Status: FAIL" >> "$SUMMARY"
  echo "- Reason: $1" >> "$SUMMARY"
  exit 1
}

step "Install deps (python + node)"
T_DEPS0="$(ts_ms)"
(cd "$ROOT_DIR" && python -m pip install -r requirements.txt) > "$ART_DIR/pip.log" 2>&1 || fail "pip install"
(cd "$ROOT_DIR/frontend" && npm ci) > "$ART_DIR/npm_ci.log" 2>&1 || fail "npm ci"
(cd "$ROOT_DIR/frontend" && npx playwright install chromium) >> "$ART_DIR/npm_ci.log" 2>&1 || fail "playwright install"
T_DEPS1="$(ts_ms)"
echo "- duration_s: $(( (T_DEPS1 - T_DEPS0) / 1000 ))" >> "$SUMMARY"

step "Build demo matches + pack"
T_BUILD0="$(ts_ms)"
(cd "$ROOT_DIR" && python scripts/generate_demo_matches.py --frames 120) > "$ART_DIR/build_matches.log" 2>&1 || fail "generate_demo_matches"
(cd "$ROOT_DIR" && python scripts/build_demo_pack.py) > "$ART_DIR/build_pack.log" 2>&1 || fail "build_demo_pack"

# Determinism self-check: rebuild and ensure tarball hash matches
PACK_TAR="$ROOT_DIR/artifacts/demo_pack.tar.gz"
PACK_SHA1="$(sha256_file "$PACK_TAR")"
(cd "$ROOT_DIR" && python scripts/build_demo_pack.py) > "$ART_DIR/build_pack_2.log" 2>&1 || fail "build_demo_pack (second pass)"
PACK_SHA2="$(sha256_file "$PACK_TAR")"
if [[ "$PACK_SHA1" != "$PACK_SHA2" ]]; then
  fail "demo_pack.tar.gz is not deterministic (sha1=$PACK_SHA1 sha2=$PACK_SHA2)"
fi
PACK_SHA="$PACK_SHA2"
T_BUILD1="$(ts_ms)"

echo "- demo_pack.tar.gz sha256: \
\`$PACK_SHA\`" >> "$SUMMARY"
echo "- duration_s: $(( (T_BUILD1 - T_BUILD0) / 1000 ))" >> "$SUMMARY"

step "Extract + offline integrity verifier"
T_VERIFY0="$(ts_ms)"
rm -rf "$ROOT_DIR/artifacts/demo_pack"
tar -xzf "$PACK_TAR" -C "$ROOT_DIR/artifacts" > "$ART_DIR/extract_pack.log" 2>&1 || fail "extract demo pack"
python "$ROOT_DIR/artifacts/demo_pack/verify_integrity.py" --pack-root "$ROOT_DIR/artifacts/demo_pack" --out-json "$INTEGRITY_JSON" > "$ART_DIR/offline_verify.log" 2>&1 || fail "offline verify_integrity.py"
T_VERIFY1="$(ts_ms)"
echo "- duration_s: $(( (T_VERIFY1 - T_VERIFY0) / 1000 ))" >> "$SUMMARY"

step "Run pytest"
T_PY0="$(ts_ms)"
(cd "$ROOT_DIR" && pytest -q) > "$PYTEST_LOG" 2>&1 || fail "pytest"
T_PY1="$(ts_ms)"
echo "- duration_s: $(( (T_PY1 - T_PY0) / 1000 ))" >> "$SUMMARY"

step "Start backend + frontend (demo mode)"
T_SERVE0="$(ts_ms)"
export DEMO_PACK_ROOT="$ROOT_DIR/artifacts/demo_pack"

python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 > "$BACKEND_LOG" 2>&1 &
BACK_PID=$!

if ! wait_http "http://127.0.0.1:8000/api/demo/health" 60; then
  fail "backend did not become ready"
fi

(cd "$ROOT_DIR/frontend" && REACT_APP_DEMO_MODE=true npm run dev -- --host 127.0.0.1 --port 5173 --strictPort) > "$FRONTEND_LOG" 2>&1 &
FRONT_PID=$!

if ! wait_http "http://127.0.0.1:5173/" 60; then
  fail "frontend did not become ready"
fi
T_SERVE1="$(ts_ms)"
echo "- duration_s: $(( (T_SERVE1 - T_SERVE0) / 1000 ))" >> "$SUMMARY"

step "Playwright E2E (demo flow)"
T_E2E0="$(ts_ms)"
PW_OUT="$ART_DIR/playwright"
rm -rf "$PW_OUT"
mkdir -p "$PW_OUT"

set +e
(cd "$ROOT_DIR/frontend" && PLAYWRIGHT_OUTPUT_DIR="$PW_OUT" E2E_BASE_URL="http://127.0.0.1:5173" npm run e2e:demo) > "$ART_DIR/e2e.log" 2>&1
E2E_CODE=$?
set -e

if [[ $E2E_CODE -ne 0 ]]; then
  i=0
  while IFS= read -r -d '' f; do
    cp "$f" "$ART_DIR/e2e_screenshot_${i}.png" || true
    i=$((i+1))
  done < <(find "$PW_OUT" -type f -name '*.png' -print0 2>/dev/null || true)

  first_video="$(find "$PW_OUT" -type f -name '*.webm' -print -quit 2>/dev/null || true)"
  if [[ -n "$first_video" ]]; then
    cp "$first_video" "$ART_DIR/e2e_video.webm" || true
  fi

  fail "playwright e2e"
fi
T_E2E1="$(ts_ms)"
echo "- duration_s: $(( (T_E2E1 - T_E2E0) / 1000 ))" >> "$SUMMARY"

END_ALL="$(ts_ms)"
TOTAL_S=$(( (END_ALL - START_ALL) / 1000 ))

echo "" >> "$SUMMARY"
echo "### Status: PASS" >> "$SUMMARY"
echo "- Total time: ${TOTAL_S}s" >> "$SUMMARY"
echo "" >> "$SUMMARY"

echo "✓ CI demo run OK"
