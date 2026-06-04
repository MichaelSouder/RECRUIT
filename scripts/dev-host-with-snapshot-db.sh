#!/usr/bin/env bash
# Run RECRUIT API on the host against the migrated DB on the snapshot Postgres (default :15432).
# Prerequisite: snapshot container up, e.g.
#   docker compose -f docker-compose.postgres-snapshot.yml up -d
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/src/backend"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@127.0.0.1:15432/recruit_db}"
export CORS_ORIGINS="${CORS_ORIGINS:-http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174}"

if [[ -x .venv-migrate/bin/python ]]; then
  PY=".venv-migrate/bin/python"
elif [[ -x venv/bin/python ]]; then
  PY="venv/bin/python"
else
  PY="python3"
fi

PORT="${RECRUIT_BACKEND_PORT:-8000}"
echo "DATABASE_URL (host): ${DATABASE_URL}"
echo "Starting uvicorn on http://127.0.0.1:${PORT} (reload). In another terminal:"
echo "  cd src/frontend && VITE_DEV_SERVER_PORT=5174 npm run dev"
echo "Then open http://127.0.0.1:5174/  (use 5174 if another app uses 5173)"
exec "$PY" -m uvicorn app.main:app --reload --host 127.0.0.1 --port "$PORT"
