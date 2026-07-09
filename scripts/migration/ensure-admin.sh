#!/usr/bin/env bash
# Ensure a known-good superuser/admin account exists with a known password,
# independent of whatever else is in the users table.
#
# Why this is needed: prod-restore-podman.sh runs pg_restore --clean, which
# replaces the entire users table with only the real historical accounts
# from the dump. Any INITIAL_ADMIN_EMAIL/INITIAL_ADMIN_PASSWORD account
# seeded when the backend container was first created (by
# app/startup_seed.py) does not survive that restore - it was never part
# of the production snapshot. Run this afterward to restore that login.
#
# Computes the bcrypt hash using the backend container's own app code
# (guaranteed compatible with app/core/security.py), then upserts the
# account directly in Postgres via ON CONFLICT (email). Safe to re-run.
#
# Usage:
#   ./scripts/migration/ensure-admin.sh
#     Reads ADMIN_EMAIL/ADMIN_PASSWORD from the backend container's own
#     INITIAL_ADMIN_EMAIL/INITIAL_ADMIN_PASSWORD env vars if not set below.
#
#   ADMIN_EMAIL=you@example.com ADMIN_PASSWORD='...' ./scripts/migration/ensure-admin.sh
#     Use different credentials than the container's own INITIAL_ADMIN_*.
#
# Environment:
#   ADMIN_EMAIL         Default: read from backend container's INITIAL_ADMIN_EMAIL
#   ADMIN_PASSWORD      Default: read from backend container's INITIAL_ADMIN_PASSWORD
#   BACKEND_CONTAINER   Default: backend
#   PODMAN_CONTAINER    Postgres container. Default: postgres
#   PGDATABASE          Default: recruit_db
#   PGUSER              Default: postgres
#   PGPASSWORD          Default: postgres
#   ENGINE              docker | podman (auto-detected against BACKEND_CONTAINER if unset)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=_common.sh
source "${SCRIPT_DIR}/_common.sh"

ADMIN_EMAIL="${ADMIN_EMAIL:-}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-}"
BACKEND_CONTAINER="${BACKEND_CONTAINER:-backend}"
PODMAN_CONTAINER="${PODMAN_CONTAINER:-postgres}"
PGDATABASE="${PGDATABASE:-recruit_db}"
PGUSER="${PGUSER:-postgres}"
PGPASSWORD="${PGPASSWORD:-postgres}"
ENGINE="${ENGINE:-${CONTAINER_ENGINE:-}}"

pick_engine() {
  if [[ -n "$ENGINE" ]]; then
    echo "$ENGINE"
    return
  fi
  if command -v docker >/dev/null 2>&1 && docker container inspect "$BACKEND_CONTAINER" >/dev/null 2>&1; then
    echo docker
    return
  fi
  if command -v podman >/dev/null 2>&1 && podman container inspect "$BACKEND_CONTAINER" >/dev/null 2>&1; then
    echo podman
    return
  fi
  echo "ERROR: container '${BACKEND_CONTAINER}' not found via docker or podman." >&2
  exit 1
}
ENGINE="$(pick_engine)"

container_env_var() {
  local var="$1"
  $ENGINE inspect "$BACKEND_CONTAINER" --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null \
    | grep "^${var}=" | head -1 | cut -d'=' -f2-
}

if [[ -z "$ADMIN_EMAIL" ]]; then
  ADMIN_EMAIL="$(container_env_var INITIAL_ADMIN_EMAIL)"
fi
if [[ -z "$ADMIN_PASSWORD" ]]; then
  ADMIN_PASSWORD="$(container_env_var INITIAL_ADMIN_PASSWORD)"
fi

if [[ -z "$ADMIN_EMAIL" || -z "$ADMIN_PASSWORD" ]]; then
  echo "ERROR: could not determine admin email/password." >&2
  echo "Set ADMIN_EMAIL and ADMIN_PASSWORD explicitly, or ensure INITIAL_ADMIN_EMAIL /" >&2
  echo "INITIAL_ADMIN_PASSWORD are set on the '${BACKEND_CONTAINER}' container." >&2
  exit 1
fi

echo "Engine: ${ENGINE}   Backend: ${BACKEND_CONTAINER}   Postgres: ${PODMAN_CONTAINER}   Admin: ${ADMIN_EMAIL}"

echo "Hashing password using ${BACKEND_CONTAINER}'s app code ..."
HASH="$($ENGINE exec -e ADMIN_PASSWORD="$ADMIN_PASSWORD" "$BACKEND_CONTAINER" \
  python -c "import os; from app.core.security import get_password_hash; print(get_password_hash(os.environ['ADMIN_PASSWORD']))")"

if [[ -z "$HASH" ]]; then
  echo "ERROR: failed to compute password hash via ${BACKEND_CONTAINER}." >&2
  exit 1
fi

echo "Upserting admin user ${ADMIN_EMAIL} in ${PGDATABASE} on ${PODMAN_CONTAINER} ..."
$ENGINE exec -i -e PGPASSWORD="$PGPASSWORD" "$PODMAN_CONTAINER" \
  psql -U "$PGUSER" -d "$PGDATABASE" -v ON_ERROR_STOP=1 \
  -v email="$ADMIN_EMAIL" -v hash="$HASH" <<'SQL'
INSERT INTO users (email, hashed_password, full_name, is_active, is_superuser, role, created_at, updated_at)
VALUES (:'email', :'hash', 'Administrator', true, true, 'admin', now(), now())
ON CONFLICT (email) DO UPDATE SET
  hashed_password = EXCLUDED.hashed_password,
  is_active = true,
  is_superuser = true,
  role = 'admin',
  updated_at = now();
SQL

echo ""
echo "Done. ${ADMIN_EMAIL} is now an active superuser/admin with the given password."
