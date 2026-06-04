#!/usr/bin/env bash
# Combine data/postgres.zip.part00 … part09 into a valid zip, extract the
# embedded PostgreSQL 13 cluster (var/lib/pgsql/data), fix ownership for the
# official postgres image, then print next steps for Docker.
#
# Usage: from repo root — ./scripts/restore-postgres-from-data-parts.sh
#
# Requires: bash, cat, sort, unzip, docker
# Disk: ~8+ GB free under data/.postgres-restore/ after extract.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA="${ROOT}/data"
RESTORE_ROOT="${DATA}/.postgres-restore"
PGDATA="${RESTORE_ROOT}/pgdata"
EXTRACT="${RESTORE_ROOT}/_extract.$$"
COMBINED_ZIP="$(mktemp -t recruit_postgres.XXXXXX.zip)"

cleanup_zip() {
  rm -f "${COMBINED_ZIP}"
}
trap cleanup_zip EXIT

log() {
  printf '%s\n' "$*" >&2
}

die() {
  log "ERROR: $*"
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing command: $1"
}

list_parts() {
  find "${DATA}" -maxdepth 1 -type f \( -name 'postgres.zip.part[0-9][0-9]' -o -name 'postgres.zip.part[0-9]' \) 2>/dev/null | LC_ALL=C sort -V
}

main() {
  require_cmd docker
  require_cmd unzip
  require_cmd cat
  require_cmd find

  local parts
  parts="$(list_parts)"
  if [[ -z "${parts}" ]]; then
    die "no postgres.zip.part* files under ${DATA}. Pull from Git (and Git LFS if used) first."
  fi

  local n
  n="$(echo "${parts}" | wc -l | tr -d ' ')"
  log "Found ${n} part file(s). Combining into temporary zip…"
  : >"${COMBINED_ZIP}"
  while IFS= read -r f; do
    [[ -n "${f}" ]] || continue
    cat "${f}" >>"${COMBINED_ZIP}"
  done <<<"${parts}"

  if ! unzip -t "${COMBINED_ZIP}" >/dev/null 2>&1; then
    die "combined archive failed zip test; check part files are complete and ordered."
  fi

  local ver
  ver="$(unzip -p "${COMBINED_ZIP}" var/lib/pgsql/data/PG_VERSION 2>/dev/null | tr -d '[:space:]' || true)"
  if [[ "${ver}" != "13" ]]; then
    log "WARNING: cluster PG_VERSION is '${ver:-unknown}', expected 13 for postgres:13 image."
  fi

  log "Removing old extract target (if any)…"
  rm -rf "${EXTRACT}" "${PGDATA}"
  mkdir -p "${EXTRACT}"

  log "Extracting cluster (this is large, several minutes)…"
  unzip -q "${COMBINED_ZIP}" -d "${EXTRACT}" "var/lib/pgsql/data/*"

  mkdir -p "${RESTORE_ROOT}"
  mv "${EXTRACT}/var/lib/pgsql/data" "${PGDATA}"
  rm -rf "${EXTRACT}"

  log "Fixing ownership for postgres UID/GID 999 in container…"
  docker run --rm --pull=missing \
    -v "${PGDATA}:/pg" \
    alpine:3.19 \
    sh -c 'chown -R 999:999 /pg'

  log ""
  log "Done. Data directory: ${PGDATA}"
  log ""
  log "Start PostgreSQL 13 (compose project name is isolated from docker-compose.yml):"
  log "  docker compose -f docker-compose.postgres-snapshot.yml up -d"
  log ""
  log "Snapshot pg_hba uses md5 for TCP; local socket is trust. Set a known superuser password (optional, for GUI clients):"
  log "  docker exec -it recruit_postgres_snapshot psql -U postgres -h /var/run/postgresql -c \"ALTER USER postgres PASSWORD 'postgres';\""
  log ""
  log "List databases — pick the DB you need (this dump may not include recruit_db):"
  log "  docker exec -it recruit_postgres_snapshot psql -U postgres -h /var/run/postgresql -c '\\l'"
  log ""
  log "Connect from host (after ALTER above):"
  log "  psql \"postgresql://postgres:postgres@127.0.0.1:15432/DATABASE_NAME\""
  log ""
}

main "$@"
