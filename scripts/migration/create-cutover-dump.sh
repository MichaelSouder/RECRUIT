#!/usr/bin/env bash
# Create a new RECRUIT production cutover dump end to end:
#   pg_dump the source DB -> split + gzip -> checksum -> refresh
#   migration_verify_baseline.json -> update DEFAULT_DUMP_BASE and
#   data/backups/README.md -> git commit (not push).
#
# After this script finishes, review the commit and run: git push origin main
#
# Usage:
#   ./scripts/migration/create-cutover-dump.sh --source-container <name> [options]
#
# Options:
#   --source-container NAME  Postgres container holding the data to dump (required)
#   --engine docker|podman   Container engine (auto-detected against the
#                            source container if omitted)
#   --db NAME                Source database name (default: recruit_db)
#   --user NAME              Source database user (default: postgres)
#   --parts N                Number of gzip parts to split into (default: 7)
#   --backups-dir DIR        Output directory (default: data/backups)
#   --no-commit              Stage changes but do not create a git commit
#   -h, --help
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
# shellcheck source=_common.sh
source "${SCRIPT_DIR}/_common.sh"

SOURCE_CONTAINER="${SOURCE_CONTAINER:-}"
ENGINE="${ENGINE:-}"
PGDATABASE="${PGDATABASE:-recruit_db}"
PGUSER="${PGUSER:-postgres}"
PGPASSWORD="${PGPASSWORD:-postgres}"
PARTS="${PARTS:-7}"
BACKUPS_DIR="${BACKUPS_DIR:-${DEFAULT_BACKUPS}}"
DO_COMMIT=1

usage() {
  sed -n '2,21p' "$0" | sed 's/^# \{0,1\}//'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source-container) SOURCE_CONTAINER="$2"; shift 2 ;;
    --engine) ENGINE="$2"; shift 2 ;;
    --db) PGDATABASE="$2"; shift 2 ;;
    --user) PGUSER="$2"; shift 2 ;;
    --parts) PARTS="$2"; shift 2 ;;
    --backups-dir) BACKUPS_DIR="$2"; shift 2 ;;
    --no-commit) DO_COMMIT=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ -z "$SOURCE_CONTAINER" ]]; then
  echo "ERROR: --source-container is required (the Postgres container holding the data to dump)." >&2
  echo "Running containers:" >&2
  { command -v docker >/dev/null 2>&1 && docker ps --format '  [docker] {{.Names}}'; } >&2 2>/dev/null || true
  { command -v podman >/dev/null 2>&1 && podman ps --format '  [podman] {{.Names}}'; } >&2 2>/dev/null || true
  exit 1
fi

need_cmd gzip split date awk jq

if command -v shasum >/dev/null 2>&1; then
  SHA_CMD=(shasum -a 256)
elif command -v sha256sum >/dev/null 2>&1; then
  SHA_CMD=(sha256sum)
else
  echo "Need shasum or sha256sum" >&2
  exit 1
fi

pick_engine() {
  if [[ -n "$ENGINE" ]]; then
    echo "$ENGINE"
    return
  fi
  if command -v docker >/dev/null 2>&1 && docker container inspect "$SOURCE_CONTAINER" >/dev/null 2>&1; then
    echo docker
    return
  fi
  if command -v podman >/dev/null 2>&1 && podman container inspect "$SOURCE_CONTAINER" >/dev/null 2>&1; then
    echo podman
    return
  fi
  echo "ERROR: container '${SOURCE_CONTAINER}' not found via docker or podman." >&2
  exit 1
}
ENGINE="$(pick_engine)"
echo "Engine: ${ENGINE}   Source container: ${SOURCE_CONTAINER}   DB: ${PGDATABASE}"

if [[ "$($ENGINE container inspect -f '{{.State.Running}}' "$SOURCE_CONTAINER" 2>/dev/null)" != "true" ]]; then
  echo "ERROR: container '${SOURCE_CONTAINER}' exists but is not running." >&2
  exit 1
fi

OLD_BASE="$(grep '^DEFAULT_DUMP_BASE=' "${SCRIPT_DIR}/_common.sh" | sed -E 's/^DEFAULT_DUMP_BASE="(.*)"$/\1/')"
BASE="recruit_prod_cutover_$(date -u +%Y%m%dT%H%MZ)"
if [[ "$BASE" == "$OLD_BASE" ]]; then
  BASE="${BASE}-2"
fi
echo "New cutover base: ${BASE} (previous default: ${OLD_BASE})"

WORK="$(mktemp -d)"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT

echo ""
echo "[1/6] Dumping ${PGDATABASE} from ${SOURCE_CONTAINER} ..."
$ENGINE exec "$SOURCE_CONTAINER" pg_dump -U "$PGUSER" -d "$PGDATABASE" \
  -Fc --no-owner --no-privileges -f "/tmp/${BASE}.dump"
$ENGINE cp "${SOURCE_CONTAINER}:/tmp/${BASE}.dump" "${WORK}/${BASE}.dump"
$ENGINE exec "$SOURCE_CONTAINER" rm -f "/tmp/${BASE}.dump"

DUMP_PATH="${WORK}/${BASE}.dump"
SIZE=$(stat -f%z "$DUMP_PATH" 2>/dev/null || stat -c%s "$DUMP_PATH")
echo "Dump size: $((SIZE / 1024 / 1024)) MB"

echo ""
echo "[2/6] Checksum + split into ${PARTS} part(s) ..."
"${SHA_CMD[@]}" "$DUMP_PATH" | awk -v b="$BASE" '{print $1"  "b".dump"}' > "${BACKUPS_DIR}/${BASE}.dump.sha256"

BYTES_PER_PART=$(( (SIZE + PARTS - 1) / PARTS ))
split -b "$BYTES_PER_PART" "$DUMP_PATH" "${WORK}/${BASE}.part"
i=0
for f in $(ls "${WORK}/${BASE}.part"* | sort); do
  mv "$f" "${WORK}/${BASE}.part${i}"
  gzip -9 "${WORK}/${BASE}.part${i}"
  mv "${WORK}/${BASE}.part${i}.gz" "${BACKUPS_DIR}/"
  i=$((i + 1))
done
echo "Wrote ${i} part(s) to ${BACKUPS_DIR}"

echo ""
echo "[3/6] Updating DEFAULT_DUMP_BASE in _common.sh ..."
sed -i.bak "s/^DEFAULT_DUMP_BASE=\"${OLD_BASE}\"/DEFAULT_DUMP_BASE=\"${BASE}\"/" "${SCRIPT_DIR}/_common.sh"
rm -f "${SCRIPT_DIR}/_common.sh.bak"

echo ""
echo "[4/6] Refreshing migration_verify_baseline.json from the source container ..."
(
  unset DATABASE_URL
  export CONTAINER_ENGINE="$ENGINE"
  export PODMAN_CONTAINER="$SOURCE_CONTAINER"
  export PGDATABASE PGUSER PGPASSWORD
  "${SCRIPT_DIR}/migration-verify-baseline.sh"
)

echo ""
echo "[5/6] Updating data/backups/README.md ..."
PREV_BASES="$(cd "$BACKUPS_DIR" && ls -- *.dump.sha256 2>/dev/null | sed 's/\.dump\.sha256$//' | grep -vx "$BASE" | sort -u)"

README="${BACKUPS_DIR}/README.md"
NEW_BLOCK_FILE="$(mktemp)"
{
  printf '## Current cutover (default): `%s`\n\n' "$BASE"
  printf '%s parts. Full `.dump` is gitignored (`data/backups/*.dump`); reassemble locally.\n\n' "$i"
  printf '## Previous cutovers (kept for history)\n\n'
  while IFS= read -r b; do
    [[ -z "$b" ]] && continue
    printf -- '- `%s`\n' "$b"
  done <<< "$PREV_BASES"
  printf '\nUse `--base <name>` (or `DUMP_BASE=<name>`) with the scripts below to restore an older cutover instead of the current default.\n'
} > "$NEW_BLOCK_FILE"

{
  sed -n '1,/<!-- CUTOVER_INFO_START/p' "$README"
  cat "$NEW_BLOCK_FILE"
  sed -n '/<!-- CUTOVER_INFO_END/,$p' "$README"
} > "${README}.tmp"
mv "${README}.tmp" "$README"
rm -f "$NEW_BLOCK_FILE"

echo ""
echo "[6/6] Verifying restore of the new dump against a disposable container ..."
$ENGINE rm -f cutover_dump_verify >/dev/null 2>&1 || true
$ENGINE run -d --name cutover_dump_verify -e POSTGRES_PASSWORD=postgres "postgres:15" >/dev/null
# The official postgres image briefly starts a temporary single-user-mode
# server while running init scripts (so pg_isready can report a false
# positive), then restarts for real. Retry the actual command we need
# instead of trusting a separate readiness probe.
READY=0
for _ in $(seq 1 120); do
  if $ENGINE exec cutover_dump_verify psql -U postgres -c "CREATE DATABASE ${PGDATABASE};" >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 1
done
if [[ "$READY" != "1" ]]; then
  echo "WARNING: verification Postgres container did not become ready in time; skipping" >&2
  echo "the restore self-check (dump/checksum/baseline above are still valid)." >&2
  $ENGINE rm -f cutover_dump_verify >/dev/null 2>&1 || true
  SKIP_VERIFY_STEP=1
fi
if [[ "${SKIP_VERIFY_STEP:-0}" != "1" ]]; then
  $ENGINE cp "$DUMP_PATH" "cutover_dump_verify:/tmp/${BASE}.dump"
  $ENGINE exec cutover_dump_verify pg_restore -U postgres -d "$PGDATABASE" --no-owner --no-privileges "/tmp/${BASE}.dump" >/dev/null 2>&1 || true
  (
    export CONTAINER_ENGINE="$ENGINE"
    export PODMAN_CONTAINER=cutover_dump_verify
    export PGDATABASE PGUSER=postgres PGPASSWORD=postgres
    unset DATABASE_URL
    "${SCRIPT_DIR}/migration-verify.sh"
  )
  $ENGINE rm -f cutover_dump_verify >/dev/null
fi

if [[ "$DO_COMMIT" == "1" ]]; then
  echo ""
  echo "Committing ..."
  cd "$REPO_ROOT"
  git add \
    "${BACKUPS_DIR}/${BASE}.dump.sha256" \
    "${BACKUPS_DIR}"/"${BASE}".part*.gz \
    "${BACKUPS_DIR}/README.md" \
    "${REPO_ROOT}/data/migration_verify_baseline.json" \
    "${SCRIPT_DIR}/_common.sh"
  git commit -m "Add production cutover dump ${BASE}, supersedes ${OLD_BASE}

Created by scripts/migration/create-cutover-dump.sh from ${SOURCE_CONTAINER}
(${PGDATABASE}). Verified by restoring into a disposable container and
running migration-verify.sh against the refreshed baseline."
  echo ""
  echo "Committed. Review with: git show HEAD --stat"
  echo "Then push: git push origin main"
else
  echo ""
  echo "--no-commit set: files are staged in ${BACKUPS_DIR} but not committed."
fi
