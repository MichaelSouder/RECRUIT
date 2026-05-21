#!/usr/bin/env bash
# Shared helpers for bash-only migration cutover scripts.
[[ -n "${_RECRUIT_MIGRATION_COMMON_LOADED:-}" ]] && return 0
_RECRUIT_MIGRATION_COMMON_LOADED=1

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEFAULT_BASELINE="${REPO_ROOT}/data/migration_verify_baseline.json"
DEFAULT_BACKUPS="${REPO_ROOT}/data/backups"
DEFAULT_DUMP_BASE="recruit_prod_cutover_20260521T1455Z"

need_cmd() {
  local c
  for c in "$@"; do
    command -v "$c" >/dev/null 2>&1 || {
      echo "Required command not found: $c" >&2
      exit 1
    }
  done
}

require_database_url() {
  if [[ -z "${DATABASE_URL:-}" ]]; then
    echo "Set DATABASE_URL, e.g.:" >&2
    echo "  export DATABASE_URL='postgresql://postgres:postgres@127.0.0.1:5432/recruit_db'" >&2
    echo "For Podman-published Postgres on the host, use the published host:port." >&2
    exit 1
  fi
}

recruit_psql() {
  require_database_url
  psql "$DATABASE_URL" -v ON_ERROR_STOP=1 "$@"
}

recruit_scalar() {
  recruit_psql -tAc "$1" | tr -d '[:space:]'
}

podman_psql() {
  local container="${PODMAN_CONTAINER:?Set PODMAN_CONTAINER (e.g. postgres)}"
  local user="${PGUSER:-postgres}"
  local db="${PGDATABASE:-postgres}"
  podman exec -e PGPASSWORD="${PGPASSWORD:-postgres}" "$container" \
    psql -U "$user" -d "$db" -v ON_ERROR_STOP=1 "$@"
}

podman_scalar() {
  podman_psql -tAc "$1" | tr -d '[:space:]'
}

# Use DATABASE_URL if set; otherwise Podman exec into PODMAN_CONTAINER.
recruit_or_podman_scalar() {
  local sql="$1"
  if [[ -n "${DATABASE_URL:-}" ]]; then
    recruit_scalar "$sql"
  else
    podman_scalar "$sql"
  fi
}
