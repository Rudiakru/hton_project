#!/usr/bin/env bash
set -euo pipefail

# One-command demo runner (POSIX shell)
# - Builds demo pack
# - Verifies integrity (offline)
# - Starts backend and frontend demo servers
# - Prints the URL to open

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PACK_TAR="$ROOT_DIR/artifacts/demo_pack.tar.gz"
PACK_DIR="$ROOT_DIR/artifacts/demo_pack"

printf "[1/5] Build demo matches + pack\n"
python "$ROOT_DIR/scripts/generate_demo_matches.py" --frames 120
python "$ROOT_DIR/scripts/build_demo_pack.py"

printf "[2/5] Extract pack\n"
rm -rf "$PACK_DIR"
mkdir -p "$ROOT_DIR/artifacts"
tar -xzf "$PACK_TAR" -C "$ROOT_DIR/artifacts"

printf "[3/5] Offline integrity verifier\n"
python "$PACK_DIR/verify_integrity.py" --pack-root "$PACK_DIR"

printf "[4/5] Start backend (http://127.0.0.1:8000)\n"
export DEMO_PACK_ROOT="$PACK_DIR"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
BACK_PID=$!

printf "[5/5] Start frontend (http://127.0.0.1:5173)\n"
export REACT_APP_DEMO_MODE=true
export VITE_DEMO_MODE=true
cd "$ROOT_DIR/frontend"
# Serve the prebuilt app if available, else run dev
if [ -d "dist" ]; then
  npx vite preview --host 127.0.0.1 --port 5173 --strictPort &
else
  npm run dev -- --host 127.0.0.1 --port 5173 &
fi
FRONT_PID=$!
cd "$ROOT_DIR"

sleep 2

echo "Demo is ready."
echo "Open: http://127.0.0.1:5173"
echo "Backend PID: $BACK_PID, Frontend PID: $FRONT_PID"
echo "Stop with: kill $BACK_PID $FRONT_PID"