#!/usr/bin/env bash
# Restore a pg_dump custom-format archive (see docs/RESTORE_PRODUCTION_DATA.md)
# into the Postgres container of an already-deployed RECRUIT stack.
#
# This is for moving real application data (subjects, assessments, session
# notes, users, etc.) onto a server whose database is currently empty or
# only has schema/seed data - NOT for routine backups.
#
# Usage:
#   ./scripts/restore-production-dump.sh /path/to/recruit_db_production.dump [postgres_container]
#
# Environment:
#   DOCKER_CMD    Force docker | podman (auto-detected if unset).
#   POSTGRES_DB   Target database name (default: recruit_db).
#   POSTGRES_USER Target database user (default: postgres).

set -euo pipefail

NC=$'\033[0m'
GREEN=$'\033[0;32m'
RED=$'\033[0;31m'
YELLOW=$'\033[0;33m'
CYAN=$'\033[0;36m'

log_info() { echo -e "${CYAN}[INFO]${NC}  $*"; }
log_ok()   { echo -e "${GREEN}[ OK ]${NC}  $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_err()  { echo -e "${RED}[ERR ]${NC}  $*" >&2; }

DUMP_FILE="${1:-}"
if [[ -z "$DUMP_FILE" ]]; then
  log_err "Usage: $0 /path/to/dump.file [postgres_container]"
  exit 2
fi
if [[ ! -f "$DUMP_FILE" ]]; then
  log_err "Dump file not found: $DUMP_FILE"
  exit 1
fi

CANDIDATE_NAMES=(postgres recruit_postgres)
if [[ $# -ge 2 ]]; then
  CANDIDATE_NAMES=("$2")
fi

POSTGRES_DB="${POSTGRES_DB:-recruit_db}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"

pick_engine() {
  if [[ -n "${DOCKER_CMD:-}" ]]; then
    echo "$DOCKER_CMD"
    return
  fi
  if command -v docker >/dev/null 2>&1; then
    echo docker
  elif command -v podman >/dev/null 2>&1; then
    echo podman
  else
    log_err "Neither docker nor podman found in PATH. Set DOCKER_CMD."
    exit 1
  fi
}

ENGINE="$(pick_engine)"
log_info "Using container engine: $ENGINE"

CONTAINER=""
for name in "${CANDIDATE_NAMES[@]}"; do
  if $ENGINE container inspect "$name" >/dev/null 2>&1; then
    CONTAINER="$name"
    break
  fi
done

if [[ -z "$CONTAINER" ]]; then
  log_err "Could not find a running Postgres container (tried: ${CANDIDATE_NAMES[*]})."
  log_info "Pass the container name explicitly: $0 $DUMP_FILE <container_name>"
  exit 1
fi

if [[ "$($ENGINE container inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null)" != "true" ]]; then
  log_err "Container '$CONTAINER' exists but is not running."
  exit 1
fi

log_ok "Found running Postgres container: $CONTAINER"

log_warn "This will DROP and recreate application tables in database '$POSTGRES_DB'"
log_warn "on container '$CONTAINER', replacing their contents with the dump file."
read -r -p "Type 'yes' to continue: " CONFIRM
if [[ "$CONFIRM" != "yes" ]]; then
  log_info "Aborted, no changes made."
  exit 0
fi

IN_CONTAINER_PATH="/tmp/$(basename "$DUMP_FILE")"
log_info "Copying dump into container..."
$ENGINE cp "$DUMP_FILE" "$CONTAINER:$IN_CONTAINER_PATH"

log_info "Restoring (schema + data, dropping existing conflicting objects first)..."
if $ENGINE exec "$CONTAINER" pg_restore \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  --clean --if-exists --no-owner --no-privileges \
  "$IN_CONTAINER_PATH"; then
  RESTORE_STATUS=0
else
  RESTORE_STATUS=$?
fi

$ENGINE exec "$CONTAINER" rm -f "$IN_CONTAINER_PATH"

if [[ "$RESTORE_STATUS" -ne 0 ]]; then
  log_warn "pg_restore reported errors (often harmless 'does not exist' messages for a"
  log_warn "first-time restore with --if-exists). Verify row counts below before trusting this."
fi

echo ""
log_info "Row counts after restore:"
$ENGINE exec "$CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "
  select 'users', count(*) from users
  union all select 'subjects', count(*) from subjects
  union all select 'studies', count(*) from studies
  union all select 'session_notes', count(*) from session_notes
  union all select 'assessments', count(*) from assessments;
"

echo ""
log_info "If the backend container is running, no restart is required - it opens a"
log_info "new DB connection per request. Try logging in with a real production account."
