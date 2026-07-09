#!/usr/bin/env bash
# Create missing database tables on a RECRUIT backend that is already deployed
# and running, without rebuilding or redeploying images.
#
# Background: older versions of the DB-init one-liner used by docker-compose
# and the airgap scripts ran:
#   python -c 'from app.database import Base, engine; Base.metadata.create_all(bind=engine)'
# which never imports the model modules, so Base.metadata had zero tables
# registered and create_all() silently created nothing. Symptom: 500 on
# login with "relation \"users\" does not exist" in the backend logs.
# See docs/FIX_MISSING_TABLES.md for details.
#
# This script re-runs create_all() correctly (with app.models imported)
# inside the already-running backend container. Safe to re-run any time:
# create_all() only creates tables that don't already exist.
#
# Usage:
#   ./scripts/fix-missing-tables.sh [container_name]
#
# Environment:
#   DOCKER_CMD   Force docker | podman (auto-detected if unset).

set -euo pipefail

NC=$'\033[0m'
GREEN=$'\033[0;32m'
RED=$'\033[0;31m'
CYAN=$'\033[0;36m'

log_info() { echo -e "${CYAN}[INFO]${NC}  $*"; }
log_ok()   { echo -e "${GREEN}[ OK ]${NC}  $*"; }
log_err()  { echo -e "${RED}[ERR ]${NC}  $*" >&2; }

CANDIDATE_NAMES=(backend recruit_backend)
if [[ $# -gt 0 ]]; then
  CANDIDATE_NAMES=("$1")
fi

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
    log_err "Neither docker nor podman found in PATH. Set DOCKER_CMD or run this on the host where the stack is deployed."
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
  log_err "Could not find a running backend container (tried: ${CANDIDATE_NAMES[*]})."
  log_info "Pass the container name explicitly: ./scripts/fix-missing-tables.sh <container_name>"
  log_info "List containers with: $ENGINE ps"
  exit 1
fi

if [[ "$($ENGINE container inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null)" != "true" ]]; then
  log_err "Container '$CONTAINER' exists but is not running. Start it first: $ENGINE start $CONTAINER"
  exit 1
fi

log_ok "Found running backend container: $CONTAINER"
log_info "Creating any missing tables (existing tables/data are left untouched)..."
log_info "Note: this only creates empty table structures. It loads no data/rows."

if $ENGINE exec "$CONTAINER" python -c "import app.models; from app.database import Base, engine; Base.metadata.create_all(bind=engine); print('Tables present: ' + ', '.join(sorted(Base.metadata.tables.keys())))"; then
  log_ok "Database schema is up to date."
else
  log_err "create_all() failed inside the container. Check DB connectivity: $ENGINE logs $CONTAINER"
  exit 1
fi

user_count() {
  $ENGINE exec "$CONTAINER" python -c "from app.database import SessionLocal; from app.models.user import User; db = SessionLocal(); print(db.query(User).count()); db.close()" 2>/dev/null | tr -d '[:space:]'
}

COUNT="$(user_count || echo "")"
if [[ "$COUNT" == "0" ]]; then
  log_info "users table is empty. The initial-admin seed only runs once, at container"
  log_info "startup — and it already ran (and silently failed) before these tables existed."
  log_info "Restarting '$CONTAINER' so the seed step runs again now that tables exist..."
  $ENGINE restart "$CONTAINER" >/dev/null
  log_info "Waiting for the seed step to run..."
  for _ in $(seq 1 30); do
    sleep 1
    if [[ "$($ENGINE container inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null)" == "true" ]]; then
      NEW_COUNT="$(user_count || echo "")"
      if [[ -n "$NEW_COUNT" && "$NEW_COUNT" != "0" ]]; then
        log_ok "Admin user seeded ($NEW_COUNT user(s) now in the database)."
        COUNT="$NEW_COUNT"
        break
      fi
    fi
  done
  if [[ "$COUNT" == "0" ]]; then
    log_err "Still no users after restart. Check: $ENGINE logs $CONTAINER | grep -i seed"
    log_info "Confirm SEED_INITIAL_ADMIN=true and INITIAL_ADMIN_PASSWORD were set when the"
    log_info "backend container was created — if not, recreate it with those variables set"
    log_info "(see docs/AIRGAP_DEPLOY.md section 11), or register a user via"
    log_info "POST /api/v1/auth/register and promote it to admin in the database."
  fi
elif [[ -z "$COUNT" ]]; then
  log_err "Could not check user count. Check: $ENGINE logs $CONTAINER"
else
  log_ok "users table already has $COUNT user(s) — nothing to seed."
fi

echo ""
log_info "Try logging in again now."
