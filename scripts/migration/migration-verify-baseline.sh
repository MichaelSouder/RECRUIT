#!/usr/bin/env bash
# Write data/migration_verify_baseline.json from the current RECRUIT database (bash + psql + jq).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=_common.sh
source "${SCRIPT_DIR}/_common.sh"

BASELINE="${BASELINE:-${DEFAULT_BASELINE}}"
TOLERANCE_NOTE="Compare after pg_restore: scripts/migration/migration-verify.sh"

usage() {
  cat <<EOF
Usage: $(basename "$0") [options]

  Requires DATABASE_URL or Podman: PODMAN_CONTAINER, PGUSER, PGDATABASE, PGPASSWORD

Options:
  --baseline PATH   Output JSON (default: data/migration_verify_baseline.json)
  -h, --help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --baseline) BASELINE="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

need_cmd jq
if [[ -n "${DATABASE_URL:-}" ]]; then
  need_cmd psql
  scalar() { recruit_scalar "$1"; }
else
  need_cmd podman
  : "${PODMAN_CONTAINER:?Set DATABASE_URL or PODMAN_CONTAINER}"
  scalar() { podman_scalar "$1"; }
fi

count_subjects() { scalar "SELECT COUNT(*)::bigint FROM subjects"; }
count_studies() { scalar "SELECT COUNT(*)::bigint FROM studies"; }
count_assessments() { scalar "SELECT COUNT(*)::bigint FROM assessments"; }
count_legacy_id_map() { scalar "SELECT COUNT(*)::bigint FROM legacy_id_map"; }
count_session_notes() { scalar "SELECT COUNT(*)::bigint FROM session_notes"; }
count_study_procedures() { scalar "SELECT COUNT(*)::bigint FROM study_procedures"; }
count_user_study() { scalar "SELECT COUNT(*)::bigint FROM user_study"; }
count_users() { scalar "SELECT COUNT(*)::bigint FROM users"; }
count_subject_study() { scalar "SELECT COUNT(*)::bigint FROM subject_study"; }

alembic_head() {
  scalar "SELECT version_num FROM alembic_version LIMIT 1" 2>/dev/null || echo ""
}

duplicate_arc_proc_extras() {
  scalar "
    WITH x AS (
      SELECT data->>'proc_num' AS pn, COUNT(*)::bigint AS c
      FROM assessments
      WHERE assessment_type LIKE 'arc-proc-%' AND (data::jsonb) ? 'proc_num'
      GROUP BY 1
    )
    SELECT COALESCE(SUM(c - 1), 0)::bigint FROM x WHERE c > 1
  "
}

cutover_audit_present() {
  local n
  n="$(scalar "
    SELECT COUNT(*)::bigint FROM audit_logs
    WHERE change_summary ILIKE '%Tier 1 spine complete%'
       OR change_summary ILIKE '%prod cutover%'
  ")"
  [[ "$n" -gt 0 ]] && echo true || echo false
}

migration_events_rows() {
  scalar "SELECT COUNT(*)::bigint FROM migration_events"
}

# Build legacy_id_map JSON object via jq from psql CSV
legacy_map_json() {
  if [[ -n "${DATABASE_URL:-}" ]]; then
    psql "$DATABASE_URL" -tAc "
      SELECT source_system || '/' || source_table, COUNT(*)::bigint
      FROM legacy_id_map
      GROUP BY 1 ORDER BY 1
    "
  else
    podman_psql -tAc "
      SELECT source_system || '/' || source_table, COUNT(*)::bigint
      FROM legacy_id_map
      GROUP BY 1 ORDER BY 1
    "
  fi | jq -Rs '
    split("\n") | map(select(length > 0)) |
    map(split("|")) |
    map({(.[0]): (.[1] | tonumber)}) |
    add
  '
}

generated_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
map_json="$(legacy_map_json)"

jq -n \
  --arg generated_at "$generated_at" \
  --arg note "$TOLERANCE_NOTE" \
  --arg alembic_head "$(alembic_head)" \
  --argjson legacy_map "$map_json" \
  --argjson subjects "$(count_subjects)" \
  --argjson studies "$(count_studies)" \
  --argjson assessments "$(count_assessments)" \
  --argjson legacy_id_map "$(count_legacy_id_map)" \
  --argjson session_notes "$(count_session_notes)" \
  --argjson study_procedures "$(count_study_procedures)" \
  --argjson user_study "$(count_user_study)" \
  --argjson users "$(count_users)" \
  --argjson subject_study "$(count_subject_study)" \
  --argjson duplicate_arc "$(duplicate_arc_proc_extras)" \
  --argjson migration_events "$(migration_events_rows)" \
  --argjson cutover_audit "$(cutover_audit_present)" \
  '{
    generated_at: $generated_at,
    note: $note,
    alembic_head: $alembic_head,
    counts: {
      subjects: $subjects,
      studies: $studies,
      assessments: $assessments,
      legacy_id_map: $legacy_id_map,
      session_notes: $session_notes,
      study_procedures: $study_procedures,
      user_study: $user_study,
      users: $users,
      subject_study: $subject_study
    },
    legacy_id_map_by_source: $legacy_map,
    duplicate_arc_proc_extras: $duplicate_arc,
    migration_events_rows: $migration_events,
    cutover_audit_log_present: $cutover_audit
  }' > "${BASELINE}.tmp"
mv "${BASELINE}.tmp" "$BASELINE"
echo "Wrote baseline: ${BASELINE}"
jq '.counts' "$BASELINE"
