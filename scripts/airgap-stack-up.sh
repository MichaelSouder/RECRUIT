#!/usr/bin/env bash
# Start RECRUIT stack on an air-gapped host after images are loaded (docker/podman).
# Reads IMAGE_PREFIX / IMAGE_TAG from MANIFEST.txt in the bundle directory unless overridden.
#
# Usage:
#   cp recruit-airgap.env.example recruit-airgap.env   # in bundle dir; edit secrets
#   ./airgap-stack-up.sh .
# Or export variables in the shell; shell overrides recruit-airgap.env.
# Optional: --env-file /path/to/custom.env

set -euo pipefail

NC=$'\033[0m'
BOLD=$'\033[1m'
RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[0;33m'
CYAN=$'\033[0;36m'

log_info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[ OK ]${NC}  $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_err()   { echo -e "${RED}[ERR ]${NC}  $*" >&2; }

trap 'log_err "Command failed (line ${LINENO}). See messages above."' ERR

usage() {
  cat <<'EOF'
airgap-stack-up.sh — start RECRUIT containers after images are loaded (Podman/Docker).

Options:
  --dry-run              Print actions only (no docker/podman changes).
  --recreate-app         Remove backend and frontend containers if present, then start fresh.
  --env-file PATH        Load KEY=value pairs from this file (must exist).
  -h, --help             Show this help.

Environment file (optional):
  If recruit-airgap.env exists in the bundle directory (next to MANIFEST.txt), it is
  loaded automatically. Copy recruit-airgap.env.example to recruit-airgap.env and edit.
  Variables already exported in the shell are NOT overwritten by the file.
  RECRUIT_ENV_FILE may be set instead of --env-file (same precedence as --env-file).

Required environment (unless noted):
  SECRET_KEY             Long random string for JWT signing.
  INITIAL_ADMIN_PASSWORD Password for first admin (see SEED_INITIAL_ADMIN).

Common environment (defaults shown):
  CORS_ORIGINS           Browser origins (scheme+host+port, no path). Default includes
                         http://127.0.0.1:18080 and http://localhost:18080 only.
  POSTGRES_PASSWORD      Default: postgres (must match DATABASE_URL used by backend).
  POSTGRES_USER          Default: postgres
  POSTGRES_DB            Default: recruit_db
  DOCKER_CMD             Force: docker | podman (auto-detected if unset).
  IMAGE_PREFIX           Parsed from MANIFEST.txt if unset.
  TAG / IMAGE_TAG        App image tag; parsed from MANIFEST.txt if unset (IMAGE_TAG wins).

Image references (override if your engine shows different names after load):
  POSTGRES_IMAGE         Default: postgres:15
  REDIS_IMAGE            Default: redis:7-alpine

Ports (host:container):
  POSTGRES_PUBLISH       Default: 15432:5432
  REDIS_PUBLISH          Default: 16379:6379
  BACKEND_PUBLISH        Default: 18000:8000
  FRONTEND_PUBLISH       Default: 18080:80

Timeouts:
  PG_READY_TIMEOUT       Seconds to wait for Postgres readiness (default: 120).
  HTTP_CHECK_TIMEOUT     Seconds for curl health checks (default: 15).
  STACK_SETTLE_SEC       Sleep before HTTP checks (default: 5; set 0 to skip).

Optional:
  SEED_INITIAL_ADMIN     Default: true
  INITIAL_ADMIN_EMAIL    Default: admin@example.com
  RECRUIT_NETWORK        Default: recruit_network
  RECRUIT_PG_VOLUME      Default: recruit_postgres_data
EOF
}

DRY_RUN=0
RECREATE_APP=0
BUNDLE_DIR=""
ENV_FILE_OPT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)       DRY_RUN=1; shift ;;
    --recreate-app)  RECREATE_APP=1; shift ;;
    --env-file)
      shift
      if [[ $# -eq 0 ]]; then
        log_err "--env-file requires a path"
        exit 2
      fi
      ENV_FILE_OPT="$1"
      shift
      ;;
    -h|--help)       usage; exit 0 ;;
    -*)
      log_err "Unknown option: $1"
      usage >&2
      exit 2
      ;;
    *)
      if [[ -n "$BUNDLE_DIR" ]]; then
        log_err "Extra argument: $1"
        exit 2
      fi
      BUNDLE_DIR="$1"
      shift
      ;;
  esac
done

BUNDLE_DIR="${BUNDLE_DIR:-.}"
BUNDLE_DIR="$(cd "$BUNDLE_DIR" && pwd)"

run() {
  if [[ "$DRY_RUN" == 1 ]]; then
    log_info "[dry-run] $*"
    return 0
  fi
  "$@"
}

# Resolve relative path to absolute (POSIX dirname/basename).
abs_path() {
  local p="$1"
  if [[ "$p" == /* ]]; then
    printf '%s\n' "$p"
    return
  fi
  local d b
  d="$(dirname -- "$p")"
  b="$(basename -- "$p")"
  printf '%s/%s\n' "$(cd -- "$d" && pwd)" "$b"
}

# Load KEY=value from file. Skips blank lines and # comments. Optional leading "export ".
# Strips one matching pair of surrounding ' or " on values.
# Does not override variables already set in the environment (before this runs).
load_env_file() {
  local file="$1"
  local line key val applied fc lc had_extglob
  applied=0
  if [[ ! -f "$file" ]]; then
    log_err "Env file not found: $file"
    exit 1
  fi
  had_extglob=0
  shopt -q extglob && had_extglob=1
  shopt -s extglob
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%$'\r'}"
    [[ -z "${line//[[:space:]]/}" ]] && continue
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    if [[ ! "$line" =~ ^[[:space:]]*(export[[:space:]]+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
      log_warn "Skipping malformed env line: ${line:0:72}"
      continue
    fi
    key="${BASH_REMATCH[2]}"
    val="${BASH_REMATCH[3]}"
    val="${val##+([[:space:]])}"
    val="${val%%+([[:space:]])}"
    if ((${#val} >= 2)); then
      fc="${val:0:1}"
      lc="${val: -1}"
      if [[ "$fc" == '"' && "$lc" == '"' ]] || [[ "$fc" == "'" && "$lc" == "'" ]]; then
        val="${val:1:-1}"
      fi
    fi
    if [[ -n ${!key+x} ]]; then
      continue
    fi
    printf -v "$key" '%s' "$val"
    export "$key"
    ((++applied)) || true
  done < "$file"
  if [[ "$had_extglob" == 0 ]]; then
    shopt -u extglob
  fi
  log_ok "Loaded env file: $file (${applied} variable(s) applied; existing shell vars kept)."
}

resolve_and_load_env() {
  local chosen="" src
  if [[ -n "$ENV_FILE_OPT" ]]; then
    chosen="$(abs_path "$ENV_FILE_OPT")"
    load_env_file "$chosen"
    return
  fi
  if [[ -n "${RECRUIT_ENV_FILE:-}" ]]; then
    chosen="$(abs_path "$RECRUIT_ENV_FILE")"
    load_env_file "$chosen"
    return
  fi
  src="$BUNDLE_DIR/recruit-airgap.env"
  if [[ -f "$src" ]]; then
    load_env_file "$src"
    return
  fi
  log_info "No env file loaded (optional). Create $src or use --env-file / RECRUIT_ENV_FILE."
  log_info "Template: recruit-airgap.env.example in the same folder (from export) or scripts/ in the repo."
}

manifest_get() {
  local key="$1"
  local line
  line="$(grep -E "^${key}=" "$MANIFEST_FILE" | head -1)" || true
  if [[ -z "$line" ]]; then
    echo ""
    return 1
  fi
  echo "${line#*=}"
}

pick_engine() {
  if [[ -n "${DOCKER_CMD:-}" ]]; then
    if ! command -v "$DOCKER_CMD" >/dev/null 2>&1; then
      log_err "DOCKER_CMD=$DOCKER_CMD not found in PATH."
      exit 1
    fi
    log_ok "Using container engine: $DOCKER_CMD (from DOCKER_CMD)"
    return
  fi
  if command -v docker >/dev/null 2>&1; then
    DOCKER_CMD=docker
  elif command -v podman >/dev/null 2>&1; then
    DOCKER_CMD=podman
  else
    log_err "Neither docker nor podman found. Install one or set DOCKER_CMD."
    exit 1
  fi
  log_ok "Using container engine: $DOCKER_CMD (auto-detected)"
}

container_exists() {
  $DOCKER_CMD container inspect "$1" >/dev/null 2>&1
}

container_running() {
  [[ "$($DOCKER_CMD container inspect -f '{{.State.Running}}' "$1" 2>/dev/null)" == "true" ]]
}

image_exists() {
  $DOCKER_CMD image inspect "$1" >/dev/null 2>&1
}

require_images() {
  local missing=0
  local img
  for img in "$@"; do
    if image_exists "$img"; then
      log_ok "Image present: $img"
    else
      log_err "Missing image: $img (load tarballs first; see load-container-images.sh)"
      missing=1
    fi
  done
  if [[ "$missing" == 1 ]]; then
    log_info "Hint: podman/docker may list Hub images as docker.io/library/postgres:15 — set POSTGRES_IMAGE / REDIS_IMAGE if needed."
    exit 1
  fi
}

require_secrets() {
  if [[ -z "${SECRET_KEY:-}" ]]; then
    log_err "SECRET_KEY is not set. Add it to recruit-airgap.env in the bundle directory or export it."
    log_info "Example: openssl rand -hex 32"
    exit 1
  fi
  if ((${#SECRET_KEY} < 16)); then
    log_err "SECRET_KEY is too short (use at least 16 characters; 32+ recommended)."
    exit 1
  fi
  if [[ "${SEED_INITIAL_ADMIN:-true}" == "true" ]] || [[ "${SEED_INITIAL_ADMIN:-true}" == "1" ]]; then
    if [[ -z "${INITIAL_ADMIN_PASSWORD:-}" ]]; then
      log_err "INITIAL_ADMIN_PASSWORD is not set (required when SEED_INITIAL_ADMIN is true). Set it in recruit-airgap.env or export it."
      exit 1
    fi
    if ((${#INITIAL_ADMIN_PASSWORD} < 8)); then
      log_err "INITIAL_ADMIN_PASSWORD must be at least 8 characters."
      exit 1
    fi
  fi
}

wait_pg_ready() {
  if [[ "$DRY_RUN" == 1 ]]; then
    log_info "Skipping Postgres readiness wait (dry-run)."
    return 0
  fi
  local max="${PG_READY_TIMEOUT:-120}"
  local i=0
  log_info "Waiting for Postgres (timeout ${max}s)..."
  while (( i < max )); do
    if run $DOCKER_CMD exec postgres pg_isready -U "${POSTGRES_USER:-postgres}" >/dev/null 2>&1; then
      log_ok "Postgres is accepting connections."
      return 0
    fi
    sleep 1
    ((++i)) || true
    if (( i % 10 == 0 )); then
      log_info "  ... still waiting (${i}s / ${max}s)"
    fi
  done
  log_err "Postgres did not become ready within ${max}s. Check: $DOCKER_CMD logs postgres"
  exit 1
}

recreate_app_containers() {
  for c in backend frontend; do
    if container_exists "$c"; then
      log_warn "Removing container: $c"
      run $DOCKER_CMD rm -f "$c"
    fi
  done
}

echo ""
echo -e "${BOLD}RECRUIT air-gap stack startup${NC}"
echo -e "${BOLD}==============================${NC}"
log_info "Bundle directory: $BUNDLE_DIR"

MANIFEST_FILE="$BUNDLE_DIR/MANIFEST.txt"
if [[ ! -f "$MANIFEST_FILE" ]]; then
  log_err "MANIFEST.txt not found in $BUNDLE_DIR"
  log_info "Pass the directory that contains MANIFEST.txt (same folder as the .tar files)."
  exit 1
fi

resolve_and_load_env

pick_engine

if [[ -z "${IMAGE_PREFIX:-}" ]]; then
  IMAGE_PREFIX="$(manifest_get IMAGE_PREFIX)"
  if [[ -z "$IMAGE_PREFIX" ]]; then
    log_err "Could not read IMAGE_PREFIX from MANIFEST.txt and none set in environment."
    exit 1
  fi
fi

TAG="${TAG:-${IMAGE_TAG:-}}"
if [[ -z "$TAG" ]]; then
  TAG="$(manifest_get IMAGE_TAG)"
fi
if [[ -z "$TAG" ]]; then
  log_err "Could not read IMAGE_TAG from MANIFEST.txt and TAG/IMAGE_TAG not set."
  exit 1
fi

log_ok "Manifest: IMAGE_PREFIX=$IMAGE_PREFIX  TAG=$TAG"

POSTGRES_IMAGE="${POSTGRES_IMAGE:-postgres:15}"
REDIS_IMAGE="${REDIS_IMAGE:-redis:7-alpine}"
BACKEND_IMAGE="${IMAGE_PREFIX}/recruit-backend:${TAG}"
FRONTEND_IMAGE="${IMAGE_PREFIX}/recruit-frontend:${TAG}"

POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-recruit_db}"
RECRUIT_NETWORK="${RECRUIT_NETWORK:-recruit_network}"
RECRUIT_PG_VOLUME="${RECRUIT_PG_VOLUME:-recruit_postgres_data}"

CORS_ORIGINS="${CORS_ORIGINS:-http://127.0.0.1:18080,http://localhost:18080}"
if [[ "$CORS_ORIGINS" == "http://127.0.0.1:18080,http://localhost:18080" ]]; then
  log_warn "CORS_ORIGINS left at localhost defaults. Set CORS_ORIGINS for real browser URLs (scheme+host+port, no path)."
fi

DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}"

require_secrets

if [[ "$RECREATE_APP" == 1 ]]; then
  recreate_app_containers
fi

log_info "Checking local images..."
require_images "$POSTGRES_IMAGE" "$REDIS_IMAGE" "$BACKEND_IMAGE" "$FRONTEND_IMAGE"

echo ""
log_info "[1/6] Network: $RECRUIT_NETWORK"
if [[ "$DRY_RUN" == 1 ]] || ! $DOCKER_CMD network inspect "$RECRUIT_NETWORK" >/dev/null 2>&1; then
  run $DOCKER_CMD network inspect "$RECRUIT_NETWORK" >/dev/null 2>&1 || run $DOCKER_CMD network create "$RECRUIT_NETWORK"
  log_ok "Network ready."
else
  log_ok "Network already exists."
fi

log_info "[2/6] Volume: $RECRUIT_PG_VOLUME"
run $DOCKER_CMD volume create "$RECRUIT_PG_VOLUME" 2>/dev/null || true
log_ok "Volume ready (created or already present)."

echo ""
log_info "[3/6] Postgres container"
if container_exists postgres; then
  if container_running postgres; then
    log_ok "Postgres already running."
  else
    log_warn "Postgres container exists but is stopped; starting..."
    run $DOCKER_CMD start postgres
  fi
else
  log_info "Creating Postgres ($POSTGRES_IMAGE)..."
  run $DOCKER_CMD run -d \
    --name postgres \
    --network "$RECRUIT_NETWORK" \
    -e "POSTGRES_USER=$POSTGRES_USER" \
    -e "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" \
    -e "POSTGRES_DB=$POSTGRES_DB" \
    -p "${POSTGRES_PUBLISH:-15432:5432}" \
    -v "${RECRUIT_PG_VOLUME}:/var/lib/postgresql/data" \
    --restart unless-stopped \
    "$POSTGRES_IMAGE"
fi
wait_pg_ready

echo ""
log_info "[4/6] Redis container"
if container_exists redis; then
  if container_running redis; then
    log_ok "Redis already running."
  else
    log_warn "Redis container exists but is stopped; starting..."
    run $DOCKER_CMD start redis
  fi
else
  log_info "Creating Redis ($REDIS_IMAGE)..."
  run $DOCKER_CMD run -d \
    --name redis \
    --network "$RECRUIT_NETWORK" \
    -p "${REDIS_PUBLISH:-16379:6379}" \
    --restart unless-stopped \
    "$REDIS_IMAGE"
fi

BACKEND_INNER=$(cat <<EOS
echo 'Waiting for PostgreSQL...' &&
until pg_isready -h postgres -U ${POSTGRES_USER}; do sleep 1; done &&
echo 'PostgreSQL is ready!' &&
echo 'Initializing database...' &&
python -c 'from app.database import Base, engine; Base.metadata.create_all(bind=engine)' 2>&1 || true &&
python scripts/add_assessment_time_to_assessments.py 2>&1 || echo 'Migration may have already run' &&
echo 'Database initialized!' &&
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
EOS
)

echo ""
log_info "[5/6] Backend container ($BACKEND_IMAGE)"
if container_exists backend; then
  if container_running backend; then
    log_ok "Backend already running."
  else
    log_warn "Backend container exists but is stopped; starting..."
    run $DOCKER_CMD start backend
  fi
else
  log_info "Creating backend..."
  run $DOCKER_CMD run -d \
    --name backend \
    --network "$RECRUIT_NETWORK" \
    -e "DATABASE_URL=$DATABASE_URL" \
    -e "REDIS_URL=${REDIS_URL:-redis://redis:6379/0}" \
    -e "SECRET_KEY=$SECRET_KEY" \
    -e "ALGORITHM=${ALGORITHM:-HS256}" \
    -e "ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES:-30}" \
    -e "CORS_ORIGINS=$CORS_ORIGINS" \
    -e "ENVIRONMENT=${ENVIRONMENT:-production}" \
    -e "DEBUG=${DEBUG:-false}" \
    -e "SEED_INITIAL_ADMIN=${SEED_INITIAL_ADMIN:-true}" \
    -e "INITIAL_ADMIN_EMAIL=${INITIAL_ADMIN_EMAIL:-admin@example.com}" \
    -e "INITIAL_ADMIN_PASSWORD=$INITIAL_ADMIN_PASSWORD" \
    -p "${BACKEND_PUBLISH:-18000:8000}" \
    --restart unless-stopped \
    "$BACKEND_IMAGE" \
    sh -c "$BACKEND_INNER"
fi

echo ""
log_info "[6/6] Frontend container ($FRONTEND_IMAGE)"
if container_exists frontend; then
  if container_running frontend; then
    log_ok "Frontend already running."
  else
    log_warn "Frontend container exists but is stopped; starting..."
    run $DOCKER_CMD start frontend
  fi
else
  log_info "Creating frontend..."
  run $DOCKER_CMD run -d \
    --name frontend \
    --network "$RECRUIT_NETWORK" \
    -p "${FRONTEND_PUBLISH:-18080:80}" \
    --restart unless-stopped \
    "$FRONTEND_IMAGE"
fi

echo ""
if [[ "$DRY_RUN" == 1 ]]; then
  log_ok "Dry-run finished (no changes applied). Re-run without --dry-run to start containers."
  exit 0
fi

if [[ "${STACK_SETTLE_SEC:-5}" != "0" ]] && ((${STACK_SETTLE_SEC:-5} > 0)); then
  log_info "Waiting ${STACK_SETTLE_SEC:-5}s for HTTP endpoints to settle..."
  sleep "${STACK_SETTLE_SEC:-5}"
fi

log_info "Verifying stack..."
if ! container_running postgres; then
  log_err "Postgres is not running."
  exit 1
fi
run $DOCKER_CMD exec postgres pg_isready -U "$POSTGRES_USER" >/dev/null
log_ok "Postgres: pg_isready OK"

if command -v curl >/dev/null 2>&1; then
  local_to="${HTTP_CHECK_TIMEOUT:-15}"
  _be_pub="${BACKEND_PUBLISH:-18000:8000}"
  _be_host_port="${_be_pub%%:*}"
  _fe_pub="${FRONTEND_PUBLISH:-18080:80}"
  _fe_host_port="${_fe_pub%%:*}"
  if curl -sf --connect-timeout 3 --max-time "$local_to" "http://127.0.0.1:${_be_host_port}/health" >/dev/null 2>&1; then
    log_ok "Backend health: OK (http://127.0.0.1:${_be_host_port}/health)"
  else
    log_warn "Backend health check failed or not ready yet. Try: curl -sf http://127.0.0.1:${_be_host_port}/health"
    log_info "If the container just started, wait a few seconds and check: $DOCKER_CMD logs -f backend"
  fi
  if curl -sf --connect-timeout 3 --max-time "$local_to" "http://127.0.0.1:${_fe_host_port}/recruit/health" >/dev/null 2>&1; then
    log_ok "Frontend health: OK (http://127.0.0.1:${_fe_host_port}/recruit/health)"
  else
    log_warn "Frontend health check failed or not ready yet."
    log_info "Try: curl -sf http://127.0.0.1:${_fe_host_port}/recruit/health"
  fi
else
  log_warn "curl not installed; skipping HTTP health checks."
fi

echo ""
echo -e "${GREEN}${BOLD}Done.${NC}"
_fe_pub="${FRONTEND_PUBLISH:-18080:80}"
log_info "UI (with trailing slash): http://YOUR_HOST:${_fe_pub%%:*}/recruit/"
log_info "Container status: $DOCKER_CMD ps --filter network=$RECRUIT_NETWORK"
echo ""
