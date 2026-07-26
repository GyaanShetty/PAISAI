#!/usr/bin/env bash
# Run the PAISAI product locally without Docker: backend (FastAPI) + frontend
# (Next.js). Uses a local SQLite database by default. Ctrl-C stops both.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cleanup() { kill 0 2>/dev/null || true; }
trap cleanup EXIT INT TERM

echo "→ Starting backend on http://localhost:8000"
(
  cd "$ROOT/backend"
  python -m pip install -q -e ".[api]"
  exec uvicorn paisai.api.app:app --port 8000
) &

echo "→ Starting frontend on http://localhost:3000"
(
  cd "$ROOT/frontend"
  [ -d node_modules ] || npm install
  NEXT_PUBLIC_API_BASE_URL="http://localhost:8000" exec npm run dev
) &

wait
