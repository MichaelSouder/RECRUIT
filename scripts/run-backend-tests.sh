#!/usr/bin/env bash
# Runs the backend pytest suite against a real, throwaway Postgres container.
# Tests never run against SQLite: SQLite silently accepts things Postgres rejects
# (e.g. the JSONB column on migration_events has no SQLite equivalent), which hides
# real bugs instead of catching them.
#
# Usage (from repo root):
#   chmod +x scripts/run-backend-tests.sh
#   ./scripts/run-backend-tests.sh
#
# Reuses an already-running recruit_test_postgres container if present; otherwise
# starts one and leaves it running for the next invocation (stop it with:
#   docker rm -f recruit_test_postgres
# ). Override the port with TEST_POSTGRES_PORT if 55432 is taken.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="${REPO_ROOT}/src/backend"

TEST_POSTGRES_PORT="${TEST_POSTGRES_PORT:-55432}"
CONTAINER_NAME="recruit_test_postgres"

# ── postgres ─────────────────────────────────────────────────────────────────
if docker inspect "$CONTAINER_NAME" >/dev/null 2>&1; then
  if [[ "$(docker inspect -f '{{.State.Running}}' "$CONTAINER_NAME")" != "true" ]]; then
    echo "==> Starting existing $CONTAINER_NAME container..."
    docker start "$CONTAINER_NAME" >/dev/null
  else
    echo "==> $CONTAINER_NAME already running."
  fi
else
  echo "==> Creating $CONTAINER_NAME (postgres:15) on port $TEST_POSTGRES_PORT..."
  docker run -d \
    --name "$CONTAINER_NAME" \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_DB=recruit_test \
    -p "${TEST_POSTGRES_PORT}:5432" \
    postgres:15 >/dev/null
fi

echo "==> Waiting for Postgres..."
for _ in $(seq 1 30); do
  docker exec "$CONTAINER_NAME" pg_isready -U postgres >/dev/null 2>&1 && break
  sleep 1
done
docker exec "$CONTAINER_NAME" pg_isready -U postgres >/dev/null 2>&1 || {
  echo "ERROR: Postgres did not become ready in time." >&2
  exit 1
}
echo "    Postgres ready."

# ── tests ────────────────────────────────────────────────────────────────────
export TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:${TEST_POSTGRES_PORT}/recruit_test"
export SECRET_KEY="${SECRET_KEY:-test-secret-key-not-for-production-use-only-32chars}"
export SSN_ENCRYPTION_KEY="${SSN_ENCRYPTION_KEY:-test-ssn-encryption-key-not-for-prod-32chars}"

cd "$BACKEND_DIR"
PYTHON_BIN="python3"
[[ -x "venv/bin/python" ]] && PYTHON_BIN="venv/bin/python"
exec "$PYTHON_BIN" -m pytest tests/ "$@"
