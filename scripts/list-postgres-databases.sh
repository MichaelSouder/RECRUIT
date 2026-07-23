#!/usr/bin/env bash
# Lists every database on a local Postgres server, then every table in each
# database (schema, estimated row count, on-disk size).
#
# See docs/LIST_POSTGRES_DATABASES.md for background on this repo's local
# Postgres setups and more examples.
#
# Usage:
#   ./scripts/list-postgres-databases.sh                  # auto-detect connection
#   ./scripts/list-postgres-databases.sh -d recruit_db     # only list tables for one database
#   ./scripts/list-postgres-databases.sh -u postgresql://postgres:postgres@localhost:25432/postgres
#   ./scripts/list-postgres-databases.sh -c recruit_postgres  # force docker/podman exec mode
#
# Connection resolution (first match wins):
#   1. -u/--url, or the DATABASE_URL env var, used with a local `psql` client.
#   2. A local `psql` client + this repo's default snapshot DB
#      (postgresql://postgres:postgres@localhost:15432/recruit_db).
#   3. `docker exec` / `podman exec` into a running Postgres container
#      (default candidates: recruit_postgres_snapshot, recruit_postgres;
#      override with -c/--container or the PG_CONTAINER env var).
#
# Container-exec mode credentials default to user "postgres" / password
# "postgres" (matching this repo's compose files); override with PGUSER /
# PGPASSWORD if your container uses different ones.

set -euo pipefail

NC=$'\033[0m'; GREEN=$'\033[0;32m'; RED=$'\033[0;31m'; CYAN=$'\033[0;36m'; YELLOW=$'\033[0;33m'
log_info() { echo -e "${CYAN}[INFO]${NC}  $*"; }
log_ok()   { echo -e "${GREEN}[ OK ]${NC}  $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_err()  { echo -e "${RED}[ERR ]${NC}  $*" >&2; }

usage() {
  cat <<'EOF'
Usage: list-postgres-databases.sh [-d database] [-u connection-url] [-c container] [-h]

  -d, --database   Only list tables for this one database (default: all of them)
  -u, --url        Postgres connection URL (implies a local psql client)
  -c, --container  Force docker/podman exec mode against this container name
  -h, --help       Show this help

See docs/LIST_POSTGRES_DATABASES.md for details and examples.
EOF
}

ONLY_DB=""
URL_OVERRIDE=""
CONTAINER_OVERRIDE="${PG_CONTAINER:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -d|--database) ONLY_DB="$2"; shift 2 ;;
    -u|--url) URL_OVERRIDE="$2"; shift 2 ;;
    -c|--container) CONTAINER_OVERRIDE="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) log_err "Unknown argument: $1"; usage; exit 1 ;;
  esac
done

DEFAULT_URL="postgresql://postgres:postgres@localhost:15432/recruit_db"
MASK_URL() { sed -E 's#(://[^:]+:)[^@]+@#\1***@#' <<<"$1"; }

# Run "$@" in the background and kill it if it's still alive after $1 seconds.
# A `docker`/`podman` CLI whose daemon is unreachable can hang indefinitely
# rather than failing fast, so container detection below must be bounded.
with_timeout() {
  local secs="$1"; shift
  "$@" &
  local cmd_pid=$!
  ( sleep "$secs"; kill -9 "$cmd_pid" 2>/dev/null ) &
  local watchdog_pid=$!
  local status=0
  wait "$cmd_pid" 2>/dev/null || status=1
  kill "$watchdog_pid" 2>/dev/null
  wait "$watchdog_pid" 2>/dev/null
  return "$status"
}

# Look for a running postgres container across both engines, trying the
# requested/default candidate names in order. Prints "<engine> <name>" on
# success so the caller can `read -r ENGINE CONTAINER < <(find_container)`.
find_container() {
  local candidates=()
  if [[ -n "$CONTAINER_OVERRIDE" ]]; then
    candidates=("$CONTAINER_OVERRIDE")
  else
    candidates=(recruit_postgres_snapshot recruit_postgres)
  fi
  local engine name
  for engine in docker podman; do
    command -v "$engine" >/dev/null 2>&1 || continue
    for name in "${candidates[@]}"; do
      if with_timeout 5 "$engine" container inspect "$name" >/dev/null 2>&1; then
        echo "$engine $name"
        return 0
      fi
    done
  done
  return 1
}

MODE=""
BASE_URL=""
ENGINE=""
CONTAINER=""

if [[ -n "$URL_OVERRIDE" ]]; then
  command -v psql >/dev/null 2>&1 || {
    log_err "-u/--url given but no local psql client found."
    log_err "Install one (e.g. 'brew install libpq') or omit -u to use container exec mode."
    exit 1
  }
  BASE_URL="$URL_OVERRIDE"
  MODE="tcp"
elif [[ -n "${DATABASE_URL:-}" ]] && command -v psql >/dev/null 2>&1; then
  BASE_URL="$DATABASE_URL"
  MODE="tcp"
elif command -v psql >/dev/null 2>&1 && [[ -z "$CONTAINER_OVERRIDE" ]]; then
  BASE_URL="$DEFAULT_URL"
  MODE="tcp"
else
  if read -r ENGINE CONTAINER < <(find_container); then
    MODE="container"
  else
    log_err "No local psql client, and no running postgres container found among:" \
            "${CONTAINER_OVERRIDE:-recruit_postgres_snapshot, recruit_postgres}."
    log_err "Install psql (e.g. 'brew install libpq'), or start a stack, e.g.:"
    log_err "  docker compose -f docker-compose.postgres-snapshot.yml up -d"
    exit 1
  fi
fi

# Run a psql command/query against a given database, transparently using a
# direct TCP connection or a docker/podman exec into the container.
run_psql() {
  local db="$1"; shift
  if [[ "$MODE" == "tcp" ]]; then
    psql "${BASE_URL%/*}/$db" -v ON_ERROR_STOP=1 "$@"
  else
    "$ENGINE" exec -e "PGPASSWORD=${PGPASSWORD:-postgres}" "$CONTAINER" \
      psql -U "${PGUSER:-postgres}" -d "$db" -v ON_ERROR_STOP=1 "$@"
  fi
}

if [[ "$MODE" == "tcp" ]]; then
  log_info "Connecting via psql to $(MASK_URL "$BASE_URL")"
else
  log_info "Connecting via '$ENGINE exec' into container '$CONTAINER'"
fi

if ! run_psql postgres -tAc "SELECT 1;" >/dev/null 2>&1; then
  log_err "Could not connect to Postgres. Check that it's running and reachable, then retry."
  exit 1
fi

DATABASES=()
while IFS= read -r db; do
  [[ -n "$db" ]] && DATABASES+=("$db")
done < <(run_psql postgres -tAc \
  "SELECT datname FROM pg_database WHERE datistemplate = false AND datname != 'postgres' ORDER BY datname;")

if [[ ${#DATABASES[@]} -eq 0 ]]; then
  log_err "No user databases found on this server."
  exit 1
fi

echo
log_info "Databases on this server:"
run_psql postgres -c "
  SELECT datname AS database, pg_size_pretty(pg_database_size(datname)) AS size
  FROM pg_database
  WHERE datistemplate = false
  ORDER BY datname;
"

if [[ -n "$ONLY_DB" ]]; then
  DATABASES=("$ONLY_DB")
fi

for db in "${DATABASES[@]}"; do
  echo
  log_ok "Tables in database '$db':"
  if ! run_psql "$db" -c "
    SELECT schemaname AS schema,
           relname     AS table,
           n_live_tup  AS est_rows,
           pg_size_pretty(pg_total_relation_size(relid)) AS total_size
    FROM pg_stat_user_tables
    ORDER BY schema, table;
  "; then
    log_warn "Could not list tables for '$db' (check permissions/connectivity)."
  fi
done
