#!/usr/bin/env bash
# Manual stack startup — runs each podman command directly without airgap-stack-up.sh.
# Use this if airgap-stack-up.sh gives "invalid reference format".
#
# Usage (from repo root):
#   chmod +x scripts/start-stack-manual.sh
#   ./scripts/start-stack-manual.sh
#
# Reads output/container-images/recruit-airgap.env for configuration.
# Override any value by exporting it before running:
#   export POSTGRES_PASSWORD=mypassword
#   ./scripts/start-stack-manual.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${REPO_ROOT}/output/container-images/recruit-airgap.env"
MANIFEST="${REPO_ROOT}/output/container-images/MANIFEST.txt"

# ── load env file ────────────────────────────────────────────────────────────
if [[ -f "$ENV_FILE" ]]; then
  echo "Loading $ENV_FILE ..."
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%$'\r'}"
    [[ -z "${line//[[:space:]]/}" ]] && continue
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]] || continue
    key="${BASH_REMATCH[1]}"
    val="${BASH_REMATCH[2]}"
    val="${val#"${val%%[! ]*}"}"   # strip leading spaces
    val="${val%"${val##*[! ]}"}"   # strip trailing spaces
    if [[ ${#val} -ge 2 ]]; then
      fc="${val:0:1}" lc="${val: -1}"
      if [[ "$fc$lc" == '""' || "$fc$lc" == "''" ]]; then val="${val:1:-1}"; fi
    fi
    [[ -n "${!key+x}" ]] && continue
    export "$key=$val"
  done < "$ENV_FILE"
else
  echo "WARNING: $ENV_FILE not found — using defaults / exported vars only." >&2
fi

# ── defaults ─────────────────────────────────────────────────────────────────
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-recruit_db}"
POSTGRES_IMAGE="${POSTGRES_IMAGE:-docker.io/library/postgres:15}"
REDIS_IMAGE="${REDIS_IMAGE:-docker.io/library/redis:7-alpine}"
RECRUIT_NETWORK="${RECRUIT_NETWORK:-recruit_network}"
RECRUIT_PG_VOLUME="${RECRUIT_PG_VOLUME:-recruit_postgres_data}"
POSTGRES_PUBLISH="${POSTGRES_PUBLISH:-15432:5432}"
REDIS_PUBLISH="${REDIS_PUBLISH:-16379:6379}"
BACKEND_PUBLISH="${BACKEND_PUBLISH:-18000:8000}"
FRONTEND_PUBLISH="${FRONTEND_PUBLISH:-18080:80}"

if [[ -f "$MANIFEST" ]]; then
  IMAGE_PREFIX="$(grep '^IMAGE_PREFIX=' "$MANIFEST" | head -1 | cut -d= -f2 | tr -d '[:space:]')"
  IMAGE_TAG="$(grep '^IMAGE_TAG=' "$MANIFEST" | head -1 | cut -d= -f2 | tr -d '[:space:]')"
else
  IMAGE_PREFIX="${IMAGE_PREFIX:-ghcr.io/michaelsouder}"
  IMAGE_TAG="${IMAGE_TAG:-latest}"
fi
BACKEND_IMAGE="${IMAGE_PREFIX}/recruit-backend:${IMAGE_TAG}"
FRONTEND_IMAGE="${IMAGE_PREFIX}/recruit-frontend:${IMAGE_TAG}"

DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}"

# ── validate required secrets ─────────────────────────────────────────────────
[[ -z "${SECRET_KEY:-}" ]]             && { echo "ERROR: SECRET_KEY not set in $ENV_FILE"; exit 1; }
[[ -z "${INITIAL_ADMIN_PASSWORD:-}" ]] && { echo "ERROR: INITIAL_ADMIN_PASSWORD not set in $ENV_FILE"; exit 1; }

echo ""
echo "=== Configuration ==="
echo "  Postgres image : $POSTGRES_IMAGE"
echo "  Redis image    : $REDIS_IMAGE"
echo "  Backend image  : $BACKEND_IMAGE"
echo "  Frontend image : $FRONTEND_IMAGE"
echo "  Network        : $RECRUIT_NETWORK"
echo "  PG volume      : $RECRUIT_PG_VOLUME"
echo "  PG port        : $POSTGRES_PUBLISH"
echo "  Frontend port  : $FRONTEND_PUBLISH"
echo ""

# ── network and volume ────────────────────────────────────────────────────────
echo "==> Network: $RECRUIT_NETWORK"
podman network inspect "$RECRUIT_NETWORK" >/dev/null 2>&1 \
  || podman network create "$RECRUIT_NETWORK"

echo "==> Volume: $RECRUIT_PG_VOLUME"
podman volume create "$RECRUIT_PG_VOLUME" 2>/dev/null || true

# ── postgres ──────────────────────────────────────────────────────────────────
echo ""
echo "==> Postgres"
podman rm -f postgres 2>/dev/null || true
podman run -d \
  --name postgres \
  --network "$RECRUIT_NETWORK" \
  -e "POSTGRES_USER=$POSTGRES_USER" \
  -e "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" \
  -e "POSTGRES_DB=$POSTGRES_DB" \
  -p "$POSTGRES_PUBLISH" \
  -v "${RECRUIT_PG_VOLUME}:/var/lib/postgresql/data" \
  --restart unless-stopped \
  "$POSTGRES_IMAGE"

echo "   Waiting for Postgres ..."
for i in $(seq 1 60); do
  podman exec postgres pg_isready -U "$POSTGRES_USER" >/dev/null 2>&1 && break
  sleep 2
done
podman exec postgres pg_isready -U "$POSTGRES_USER"
echo "   Postgres ready."

# ── redis ─────────────────────────────────────────────────────────────────────
echo ""
echo "==> Redis"
podman rm -f redis 2>/dev/null || true
podman run -d \
  --name redis \
  --network "$RECRUIT_NETWORK" \
  -p "$REDIS_PUBLISH" \
  --restart unless-stopped \
  "$REDIS_IMAGE"

# ── backend ───────────────────────────────────────────────────────────────────
echo ""
echo "==> Backend"
podman rm -f backend 2>/dev/null || true
podman run -d \
  --name backend \
  --network "$RECRUIT_NETWORK" \
  -e "DATABASE_URL=$DATABASE_URL" \
  -e "PGHOST=postgres" \
  -e "PGPORT=5432" \
  -e "REDIS_URL=redis://redis:6379/0" \
  -e "SECRET_KEY=$SECRET_KEY" \
  -e "ALGORITHM=HS256" \
  -e "ACCESS_TOKEN_EXPIRE_MINUTES=30" \
  -e "CORS_ORIGINS=${CORS_ORIGINS:-http://127.0.0.1:18080,http://localhost:18080}" \
  -e "ENVIRONMENT=production" \
  -e "DEBUG=false" \
  -e "SEED_INITIAL_ADMIN=${SEED_INITIAL_ADMIN:-true}" \
  -e "INITIAL_ADMIN_EMAIL=${INITIAL_ADMIN_EMAIL:-admin@example.com}" \
  -e "INITIAL_ADMIN_PASSWORD=$INITIAL_ADMIN_PASSWORD" \
  -p "$BACKEND_PUBLISH" \
  --restart unless-stopped \
  "$BACKEND_IMAGE" \
  sh -c "
    until pg_isready -h postgres -p 5432 -U ${POSTGRES_USER}; do sleep 1; done &&
    python -c 'from app.database import Base, engine; Base.metadata.create_all(bind=engine)' 2>&1 || true &&
    python scripts/add_assessment_time_to_assessments.py 2>&1 || true &&
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
  "

# ── frontend ──────────────────────────────────────────────────────────────────
echo ""
echo "==> Frontend"
podman rm -f frontend 2>/dev/null || true
podman run -d \
  --name frontend \
  --network "$RECRUIT_NETWORK" \
  -p "$FRONTEND_PUBLISH" \
  --restart unless-stopped \
  "$FRONTEND_IMAGE"

# ── verify ────────────────────────────────────────────────────────────────────
echo ""
echo "==> Waiting 5s for services to settle ..."
sleep 5

echo ""
echo "=== Container status ==="
podman ps --filter "network=$RECRUIT_NETWORK"

echo ""
_fe_port="${FRONTEND_PUBLISH%%:*}"
_be_port="${BACKEND_PUBLISH%%:*}"
curl -sf "http://127.0.0.1:${_be_port}/health"  && echo "Backend  health: OK" || echo "Backend  health: not ready yet (check: podman logs backend)"
curl -sf "http://127.0.0.1:${_fe_port}/recruit/health" && echo "Frontend health: OK" || echo "Frontend health: not ready yet"

echo ""
echo "Done. Open: http://YOUR_SERVER:${_fe_port}/recruit/"
