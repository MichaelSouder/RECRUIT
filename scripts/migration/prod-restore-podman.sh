#!/usr/bin/env bash
# Assemble split dump, pg_restore into Postgres running in a Podman container, then verify.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=_common.sh
source "${SCRIPT_DIR}/_common.sh"

PODMAN_CONTAINER="${PODMAN_CONTAINER:-postgres}"
PGUSER="${PGUSER:-postgres}"
PGDATABASE="${PGDATABASE:-recruit_db}"
PGPASSWORD="${PGPASSWORD:-postgres}"
BACKUPS_DIR="${BACKUPS_DIR:-${DEFAULT_BACKUPS}}"
DUMP_BASE="${DUMP_BASE:-${DEFAULT_DUMP_BASE}}"
SKIP_VERIFY="${SKIP_VERIFY:-0}"
CREATE_DB="${CREATE_DB:-1}"
ENGINE="${CONTAINER_ENGINE:-podman}"

usage() {
  cat <<EOF
Usage: $(basename "$0") [options]

  1) Assemble ${DUMP_BASE}.dump from part*.gz in data/backups
  2) Copy dump into Podman container and pg_restore into ${PGDATABASE}
  3) Run migration-verify.sh against the restored DB

Environment:
  PODMAN_CONTAINER   Postgres container name (default: postgres)
  PGUSER             (default: postgres)
  PGDATABASE         Target database (default: recruit_db)
  PGPASSWORD         (default: postgres)
  CONTAINER_ENGINE   docker | podman (default: podman)
  DATABASE_URL       If set, used for verify step instead of container exec
                     e.g. postgresql://postgres:postgres@127.0.0.1:5432/recruit_db

Options:
  --container NAME   Container name (default: postgres)
  --db NAME          Database name (default: recruit_db)
  --backups-dir DIR
  --skip-verify      Skip post-restore verification
  --no-create-db     Fail if database does not exist (do not CREATE DATABASE)
  -h, --help

Requires: podman or docker (set CONTAINER_ENGINE=docker), gzip, psql client optional for verify via DATABASE_URL

Published-port example (verify via host):
  export DATABASE_URL='postgresql://postgres:postgres@127.0.0.1:5432/recruit_db'
  ./scripts/migration/prod-restore-podman.sh --container postgres

Docker example:
  CONTAINER_ENGINE=docker ./scripts/migration/prod-restore-podman.sh
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --container) PODMAN_CONTAINER="$2"; shift 2 ;;
    --db) PGDATABASE="$2"; shift 2 ;;
    --backups-dir) BACKUPS_DIR="$2"; shift 2 ;;
    --skip-verify) SKIP_VERIFY=1; shift ;;
    --no-create-db) CREATE_DB=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

need_cmd "$ENGINE" gunzip
"${SCRIPT_DIR}/assemble-recruit-dump.sh" --backups-dir "$BACKUPS_DIR" --base "$DUMP_BASE"

DUMP="${BACKUPS_DIR}/${DUMP_BASE}.dump"
REMOTE="/tmp/${DUMP_BASE}.dump"

"$ENGINE" inspect "$PODMAN_CONTAINER" >/dev/null 2>&1 || {
  echo "Container not found: ${PODMAN_CONTAINER} (engine: ${ENGINE})" >&2
  echo "List: ${ENGINE} ps -a" >&2
  exit 1
}

echo "Waiting for Postgres in ${PODMAN_CONTAINER} ..."
for _ in $(seq 1 120); do
  if "$ENGINE" exec -e PGPASSWORD="$PGPASSWORD" "$PODMAN_CONTAINER" \
    pg_isready -U "$PGUSER" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
"$ENGINE" exec -e PGPASSWORD="$PGPASSWORD" "$PODMAN_CONTAINER" \
  pg_isready -U "$PGUSER" >/dev/null 2>&1 || {
  echo "Postgres not ready in ${PODMAN_CONTAINER}" >&2
  exit 1
}

if [[ "$CREATE_DB" == "1" ]]; then
  exists="$("$ENGINE" exec -e PGPASSWORD="$PGPASSWORD" "$PODMAN_CONTAINER" \
    psql -U "$PGUSER" -d postgres -tAc \
    "SELECT 1 FROM pg_database WHERE datname = '${PGDATABASE}'" | tr -d '[:space:]')"
  if [[ "$exists" != "1" ]]; then
    echo "Creating database ${PGDATABASE} ..."
    "$ENGINE" exec -e PGPASSWORD="$PGPASSWORD" "$PODMAN_CONTAINER" \
      psql -U "$PGUSER" -d postgres -c "CREATE DATABASE \"${PGDATABASE}\";"
  fi
fi

echo "Copying dump into container (${REMOTE}) ..."
"$ENGINE" cp "$DUMP" "${PODMAN_CONTAINER}:${REMOTE}"

echo "Running pg_restore into ${PGDATABASE} ..."
# --clean --if-exists: the target may already have tables/rows (e.g. an empty
# schema or a seeded admin user from a fresh deploy's create_all()/seed step).
# Drop those first so the restore is a clean, repeatable full replacement
# rather than colliding with pre-existing primary keys.
"$ENGINE" exec -e PGPASSWORD="$PGPASSWORD" "$PODMAN_CONTAINER" \
  pg_restore -U "$PGUSER" -d "$PGDATABASE" --clean --if-exists --no-owner --no-acl --verbose "$REMOTE" \
  || {
    # pg_restore may exit 1 with warnings; treat as success if DB has core tables
    if "$ENGINE" exec -e PGPASSWORD="$PGPASSWORD" "$PODMAN_CONTAINER" \
      psql -U "$PGUSER" -d "$PGDATABASE" -tAc "SELECT to_regclass('public.subjects')" | grep -q subjects; then
      echo "pg_restore reported warnings but public.subjects exists; continuing." >&2
    else
      exit 1
    fi
  }

"$ENGINE" exec "$PODMAN_CONTAINER" rm -f "$REMOTE" 2>/dev/null || true

if [[ "$SKIP_VERIFY" != "1" ]]; then
  echo ""
  if [[ -z "${DATABASE_URL:-}" ]]; then
    export PODMAN_CONTAINER PGUSER PGDATABASE PGPASSWORD
    export CONTAINER_ENGINE="$ENGINE"
    echo "Tip: set DATABASE_URL to the published host port for faster verify, or verify uses ${ENGINE} exec."
  fi
  "${SCRIPT_DIR}/migration-verify.sh"
fi

echo ""
echo "Restore complete. Database: ${PGDATABASE} in container: ${PODMAN_CONTAINER}"
