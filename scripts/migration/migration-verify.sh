#!/usr/bin/env bash
# Post-restore verification: compare RECRUIT DB to migration_verify_baseline.json (bash only).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=_common.sh
source "${SCRIPT_DIR}/_common.sh"

BASELINE="${BASELINE:-${DEFAULT_BASELINE}}"
TOLERANCE="${TOLERANCE:-0}"
FAILURES=0

minimum_for() {
  case "$1" in
    subjects) echo 55000 ;;
    studies) echo 50 ;;
    assessments) echo 370000 ;;
    legacy_id_map) echo 430000 ;;
    session_notes) echo 4350 ;;
    study_procedures) echo 160 ;;
    user_study) echo 100 ;;
    users) echo 30 ;;
    subject_study) echo 5800 ;;
    *) echo 0 ;;
  esac
}

usage() {
  cat <<EOF
Usage: $(basename "$0") [options]

  Requires DATABASE_URL or a container engine (PODMAN_CONTAINER, PGUSER, PGDATABASE, PGPASSWORD,
  CONTAINER_ENGINE=docker|podman, default podman).
  Requires: psql or docker/podman, jq

Options:
  --baseline PATH     Baseline JSON (default: data/migration_verify_baseline.json)
  --tolerance N       Allowed absolute count delta vs baseline (default: 0)
  -h, --help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --baseline) BASELINE="$2"; shift 2 ;;
    --tolerance) TOLERANCE="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

need_cmd jq
if [[ -n "${DATABASE_URL:-}" ]]; then
  need_cmd psql
  scalar() { recruit_scalar "$1"; }
else
  need_cmd "${CONTAINER_ENGINE:-podman}"
  : "${PODMAN_CONTAINER:?Set DATABASE_URL or PODMAN_CONTAINER}"
  scalar() { podman_scalar "$1"; }
fi

[[ -f "$BASELINE" ]] || {
  echo "Baseline not found: ${BASELINE}" >&2
  exit 1
}

fail() {
  echo "FAIL: $*" >&2
  FAILURES=$((FAILURES + 1))
}

pass() {
  echo "OK:  $*"
}

current_count() {
  local table="$1"
  scalar "SELECT COUNT(*)::bigint FROM ${table}"
}

echo "=== Migration verify (bash) ==="
echo "Baseline: ${BASELINE} ($(jq -r .generated_at "$BASELINE"))"
echo ""

exp_head="$(jq -r '.alembic_head // empty' "$BASELINE")"
if [[ -n "$exp_head" ]]; then
  act_head="$(scalar "SELECT version_num FROM alembic_version LIMIT 1" 2>/dev/null || true)"
  if [[ "$act_head" != "$exp_head" ]]; then
    fail "alembic_head expected=${exp_head} actual=${act_head:-<missing>}"
  else
    pass "alembic_head=${exp_head}"
  fi
fi

for key in subjects studies assessments legacy_id_map session_notes study_procedures user_study users subject_study; do
  exp="$(jq -r ".counts.${key} // empty" "$BASELINE")"
  [[ -n "$exp" && "$exp" != "null" ]] || continue
  act="$(current_count "$key")"
  delta=$((act - exp))
  adelta=${delta#-}
  if [[ "$adelta" -gt "$TOLERANCE" ]]; then
    fail "${key} expected=${exp} actual=${act} delta=${delta} (tolerance=${TOLERANCE})"
  else
    pass "${key}=${act} (baseline ${exp})"
  fi
  min="$(minimum_for "$key")"
  if [[ "$min" -gt 0 && "$act" -lt "$min" ]]; then
    fail "${key} below minimum ${min} (actual ${act})"
  fi
done

dup="$(scalar "
  WITH x AS (
    SELECT data->>'proc_num' AS pn, COUNT(*)::bigint AS c
    FROM assessments
    WHERE assessment_type LIKE 'arc-proc-%' AND (data::jsonb) ? 'proc_num'
    GROUP BY 1
  )
  SELECT COALESCE(SUM(c - 1), 0)::bigint FROM x WHERE c > 1
")"
if [[ "$dup" != "0" ]]; then
  fail "duplicate_arc_proc_extras=${dup} (expected 0)"
else
  pass "duplicate_arc_proc_extras=0"
fi

echo ""
if [[ "$FAILURES" -gt 0 ]]; then
  echo "Status: FAIL (${FAILURES} check(s))"
  exit 1
fi
echo "Status: PASS"
exit 0
