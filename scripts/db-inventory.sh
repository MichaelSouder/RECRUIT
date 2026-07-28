#!/usr/bin/env bash
# Generates a Markdown inventory document for one or more PostgreSQL databases:
# the database list, every table with its EXACT row count and on-disk size, and
# the first N rows (default 20) of each table.
#
# Unlike scripts/db_snapshot_pdf.py (PDF, needs `pip install psycopg2-binary
# fpdf2`), this uses only bash + psql, so it runs on an air-gapped deploy host
# with nothing to install. Markdown instead of PDF also means the output diffs
# and greps, which is what you want when comparing before/after a migration.
#
# Usage:
#   ./scripts/db-inventory.sh                          # auto-detect connection, all databases
#   ./scripts/db-inventory.sh -d recruit_db            # one database
#   ./scripts/db-inventory.sh -n 50                    # 50 sample rows per table
#   ./scripts/db-inventory.sh -o - > inventory.md      # write to stdout
#   ./scripts/db-inventory.sh -u postgresql://postgres:postgres@localhost:25432/postgres
#   ./scripts/db-inventory.sh -c recruit_postgres      # force docker/podman exec mode
#
# Connection resolution matches list-postgres-databases.sh (first match wins):
#   1. -u/--url, or the DATABASE_URL env var, used with a local `psql` client.
#   2. A local `psql` client + this repo's default snapshot DB
#      (postgresql://postgres:postgres@localhost:15432/recruit_db).
#   3. `docker exec` / `podman exec` into a running Postgres container
#      (default candidates: recruit_postgres_snapshot, recruit_postgres;
#      override with -c/--container or the PG_CONTAINER env var).
#
# SENSITIVE DATA: sample rows are real data. Columns named ssn, password, or
# hashed_password are replaced with [REDACTED] by default. Everything else --
# names, DOBs, contact details -- is written verbatim. Treat the output as
# containing PHI: the default output path is gitignored, and you should not
# commit it or move it off the host without the same handling as a DB dump.
# --no-redact disables masking; it is not the default for a reason.

set -euo pipefail

NC=$'\033[0m'; GREEN=$'\033[0;32m'; RED=$'\033[0;31m'; CYAN=$'\033[0;36m'; YELLOW=$'\033[0;33m'
log_info() { echo -e "${CYAN}[INFO]${NC}  $*" >&2; }
log_ok()   { echo -e "${GREEN}[ OK ]${NC}  $*" >&2; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*" >&2; }
log_err()  { echo -e "${RED}[ERR ]${NC}  $*" >&2; }

usage() {
  cat <<'EOF'
Usage: db-inventory.sh [-d database] [-n rows] [-o output] [-u url] [-c container] [--no-redact] [-h]

  -d, --database    Only inventory this one database (default: all non-template databases)
  -n, --limit       Sample rows per table (default: 20)
  -o, --output      Output file, or "-" for stdout
                    (default: output/db-inventory-<host>-<UTC timestamp>.md)
  -u, --url         Postgres connection URL (implies a local psql client)
  -c, --container   Force docker/podman exec mode against this container name
      --no-redact   Do NOT mask ssn/password/hashed_password columns
  -h, --help        Show this help

Sample rows contain real data. See the header comment in this script before
sharing or committing the output.
EOF
}

ONLY_DB=""
LIMIT=20
OUTPUT=""
URL_OVERRIDE=""
CONTAINER_OVERRIDE="${PG_CONTAINER:-}"
REDACT=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    -d|--database)  ONLY_DB="$2"; shift 2 ;;
    -n|--limit)     LIMIT="$2"; shift 2 ;;
    -o|--output)    OUTPUT="$2"; shift 2 ;;
    -u|--url)       URL_OVERRIDE="$2"; shift 2 ;;
    -c|--container) CONTAINER_OVERRIDE="$2"; shift 2 ;;
    --no-redact)    REDACT=0; shift ;;
    -h|--help)      usage; exit 0 ;;
    *) log_err "Unknown argument: $1"; usage; exit 1 ;;
  esac
done

if ! [[ "$LIMIT" =~ ^[0-9]+$ ]]; then
  log_err "-n/--limit must be a non-negative integer, got: $LIMIT"
  exit 1
fi

# Columns masked in sample-row output. Matched case-insensitively on the bare
# column name, so it applies across every table and database in the run.
REDACT_COLUMNS="'ssn','password','hashed_password'"

DEFAULT_URL="postgresql://postgres:postgres@localhost:15432/recruit_db"
MASK_URL() { sed -E 's#(://[^:]+:)[^@]+@#\1***@#' <<<"$1"; }

# Run "$@" in the background and kill it if it's still alive after $1 seconds.
# A docker/podman CLI whose daemon is unreachable hangs rather than failing
# fast, so container detection has to be bounded.
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

# Run psql against a given database, transparently using a direct TCP
# connection or a docker/podman exec into the container.
run_psql() {
  local db="$1"; shift
  if [[ "$MODE" == "tcp" ]]; then
    psql "${BASE_URL%/*}/$db" -v ON_ERROR_STOP=1 "$@"
  else
    "$ENGINE" exec -e "PGPASSWORD=${PGPASSWORD:-postgres}" "$CONTAINER" \
      psql -U "${PGUSER:-postgres}" -d "$db" -v ON_ERROR_STOP=1 "$@"
  fi
}

# Scalar/tuple-only query.
psql_raw() { local db="$1"; shift; run_psql "$db" -tAc "$1"; }

# psql has no Markdown output format (aligned, asciidoc, csv, html, latex,
# troff-ms, unaligned, wrapped -- that's the whole list), so rows are rendered
# into Markdown by SQL string concatenation instead. Doing the escaping in SQL
# rather than in bash is what makes it safe: a cell containing a pipe or a
# newline would otherwise silently break the table structure.
md_cell_expr() {
  local ident="$1"
  printf "coalesce(replace(replace(%s::text, '|', '\\\\|'), chr(10), ' '), 'NULL')" "$ident"
}

if [[ "$MODE" == "tcp" ]]; then
  log_info "Connecting via psql to $(MASK_URL "$BASE_URL")"
  SOURCE_DESC="psql -> $(MASK_URL "$BASE_URL")"
else
  log_info "Connecting via '$ENGINE exec' into container '$CONTAINER'"
  SOURCE_DESC="$ENGINE exec -> container '$CONTAINER'"
fi

if ! psql_raw postgres "SELECT 1;" >/dev/null 2>&1; then
  log_err "Could not connect to Postgres. Check that it's running and reachable, then retry."
  exit 1
fi

SERVER_VERSION="$(psql_raw postgres "SHOW server_version;" | tr -d '[:space:]')"
GENERATED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

if [[ -z "$OUTPUT" ]]; then
  REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  OUTPUT="$REPO_ROOT/output/db-inventory-$(hostname -s 2>/dev/null || echo host)-$(date -u +%Y%m%dT%H%M%SZ).md"
fi

if [[ "$OUTPUT" == "-" ]]; then
  exec 3>&1
else
  mkdir -p "$(dirname "$OUTPUT")"
  exec 3>"$OUTPUT"
fi
emit() { printf '%s\n' "$*" >&3; }

DATABASES=()
while IFS= read -r db; do
  [[ -n "$db" ]] && DATABASES+=("$db")
done < <(psql_raw postgres \
  "SELECT datname FROM pg_database WHERE datistemplate = false AND datname != 'postgres' ORDER BY datname;")

if [[ ${#DATABASES[@]} -eq 0 ]]; then
  log_err "No user databases found on this server."
  exit 1
fi

emit "# PostgreSQL database inventory"
emit ""
emit "| | |"
emit "|---|---|"
emit "| Generated (UTC) | \`$GENERATED_AT\` |"
emit "| Source | \`$SOURCE_DESC\` |"
emit "| Server version | \`$SERVER_VERSION\` |"
emit "| Sample rows per table | $LIMIT |"
if [[ "$REDACT" -eq 1 ]]; then
  emit "| Redacted columns | \`ssn\`, \`password\`, \`hashed_password\` |"
else
  emit "| Redacted columns | **none — \`--no-redact\` was used** |"
fi
emit ""
emit "> Sample rows are real data from this server. Row counts are exact \`COUNT(*)\`,"
emit "> not planner estimates. Sample rows are ordered by primary key where one exists;"
emit "> tables without a primary key are noted inline and their row order is arbitrary."
emit ""

emit "## Databases"
emit ""
emit "| Database | Size |"
emit "|---|---:|"
while IFS='|' read -r dbname dbsize; do
  [[ -n "$dbname" ]] && emit "| \`$dbname\` | $dbsize |"
done < <(psql_raw postgres "
  SELECT datname || '|' || pg_size_pretty(pg_database_size(datname))
  FROM pg_database
  WHERE datistemplate = false
  ORDER BY datname;
")
emit ""

if [[ -n "$ONLY_DB" ]]; then
  DATABASES=("$ONLY_DB")
fi

for db in "${DATABASES[@]}"; do
  log_info "Inventorying database '$db'..."
  emit "---"
  emit ""
  emit "## Database: \`$db\`"
  emit ""

  if ! psql_raw "$db" "SELECT 1;" >/dev/null 2>&1; then
    log_warn "Could not connect to '$db'; skipping."
    emit "_Could not connect to this database; skipped._"
    emit ""
    continue
  fi

  emit "### Tables"
  emit ""

  # The per-table COUNT(*) loop is driven from the shell because SQL can't
  # COUNT(*) a table named by a value without dynamic SQL, and this script
  # deliberately creates no functions on the target database. Exact counts
  # (not n_live_tup estimates) also keep this summary and the per-table
  # sections below from ever disagreeing.
  TABLES=()
  while IFS='|' read -r schema tbl; do
    [[ -n "$schema" && -n "$tbl" ]] && TABLES+=("$schema|$tbl")
  done < <(psql_raw "$db" "
    SELECT table_schema || '|' || table_name
    FROM information_schema.tables
    WHERE table_type = 'BASE TABLE'
      AND table_schema NOT IN ('pg_catalog', 'information_schema')
    ORDER BY table_schema, table_name;
  ")

  if [[ ${#TABLES[@]} -eq 0 ]]; then
    emit "_No user tables in this database._"
    emit ""
    continue
  fi

  emit "| Schema | Table | Exact rows | Total size |"
  emit "|---|---|---:|---:|"
  declare -a COUNTS=()
  for entry in "${TABLES[@]}"; do
    schema="${entry%%|*}"; tbl="${entry##*|}"
    count="$(psql_raw "$db" "SELECT count(*) FROM \"$schema\".\"$tbl\";" 2>/dev/null || echo "?")"
    size="$(psql_raw "$db" "SELECT pg_size_pretty(pg_total_relation_size('\"$schema\".\"$tbl\"'::regclass));" 2>/dev/null || echo "?")"
    COUNTS+=("$count")
    emit "| \`$schema\` | \`$tbl\` | $count | $size |"
  done
  emit ""

  emit "### Sample rows (first $LIMIT per table)"
  emit ""
  idx=0
  for entry in "${TABLES[@]}"; do
    schema="${entry%%|*}"; tbl="${entry##*|}"
    count="${COUNTS[$idx]}"
    idx=$((idx + 1))

    emit "#### \`$schema.$tbl\`"
    emit ""
    emit "Exact row count: **$count**"
    emit ""

    if [[ "$count" == "0" ]]; then
      emit "_(no rows)_"
      emit ""
      continue
    fi

    # Column list drives both the Markdown header and the row expression.
    # quote_ident() comes from the server so odd column names stay valid.
    idents=(); headers=()
    while IFS=$'\t' read -r ident raw; do
      [[ -n "$ident" ]] || continue
      idents+=("$ident"); headers+=("$raw")
    done < <(psql_raw "$db" "
      SELECT quote_ident(column_name) || chr(9) || column_name
      FROM information_schema.columns
      WHERE table_schema = '$schema' AND table_name = '$tbl'
      ORDER BY ordinal_position;
    ")

    if [[ ${#idents[@]} -eq 0 ]]; then
      emit "_(could not read columns for this table)_"
      emit ""
      continue
    fi

    # Redacted columns become a literal in the SELECT, so the sensitive value
    # is never transmitted off the server at all -- not fetched and then masked.
    row_expr=""
    header_row="|"; divider_row="|"
    for i in "${!idents[@]}"; do
      col_lower="$(printf '%s' "${headers[$i]}" | tr '[:upper:]' '[:lower:]')"
      if [[ "$REDACT" -eq 1 && ",$REDACT_COLUMNS," == *"'$col_lower'"* ]]; then
        cell="'[REDACTED]'"
      else
        cell="$(md_cell_expr "${idents[$i]}")"
      fi
      [[ -n "$row_expr" ]] && row_expr="$row_expr || ' | ' || "
      row_expr="$row_expr$cell"
      header_row="$header_row ${headers[$i]} |"
      divider_row="$divider_row---|"
    done
    row_expr="'| ' || $row_expr || ' |'"

    # Order by primary key when there is one, so repeated runs are comparable.
    pk="$(psql_raw "$db" "
      SELECT string_agg(quote_ident(a.attname), ', ' ORDER BY k.ord)
      FROM pg_index i
      JOIN pg_class c ON c.oid = i.indrelid
      JOIN pg_namespace n ON n.oid = c.relnamespace
      CROSS JOIN LATERAL unnest(i.indkey) WITH ORDINALITY AS k(attnum, ord)
      JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum = k.attnum
      WHERE i.indisprimary AND n.nspname = '$schema' AND c.relname = '$tbl';
    " 2>/dev/null || echo "")"

    if [[ -n "$pk" ]]; then
      order_clause="ORDER BY $pk"
    else
      order_clause=""
      emit "_No primary key; row order is arbitrary._"
      emit ""
    fi

    if rows="$(psql_raw "$db" "
      SELECT $row_expr FROM \"$schema\".\"$tbl\" $order_clause LIMIT $LIMIT;
    " 2>/dev/null)"; then
      emit "$header_row"
      emit "$divider_row"
      [[ -n "$rows" ]] && printf '%s\n' "$rows" >&3
    else
      emit "_(could not read sample rows for this table)_"
    fi
    emit ""
  done
done

exec 3>&-

if [[ "$OUTPUT" != "-" ]]; then
  log_ok "Wrote $OUTPUT"
  log_warn "This file contains real row data. Do not commit or share it without PHI handling."
fi
