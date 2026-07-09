#!/usr/bin/env bash
# Reassemble a recruit_prod_cutover dump from its gzip parts + optional SHA-256 check.
# Part count is auto-detected (globs ${BASE}.part*.gz) - no fixed number of parts.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=_common.sh
source "${SCRIPT_DIR}/_common.sh"

BACKUPS_DIR="${BACKUPS_DIR:-${DEFAULT_BACKUPS}}"
BASE="${DUMP_BASE:-${DEFAULT_DUMP_BASE}}"

usage() {
  cat <<EOF
Usage: $(basename "$0") [options]

  Reassemble \${BASE}.dump from \${BASE}.part<N>.gz (any number of parts, in order)

Options:
  --backups-dir DIR   Directory containing part files (default: data/backups)
  --base NAME         Dump base name without .dump (default: ${DEFAULT_DUMP_BASE})
  -h, --help          Show this help

Requires: gzip, shasum (or sha256sum)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --backups-dir) BACKUPS_DIR="$2"; shift 2 ;;
    --base) BASE="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

need_cmd gunzip awk
if command -v shasum >/dev/null 2>&1; then
  SHA_CMD=(shasum -a 256)
elif command -v sha256sum >/dev/null 2>&1; then
  SHA_CMD=(sha256sum)
else
  echo "Need shasum or sha256sum for checksum verify" >&2
  exit 1
fi

OUT="${BACKUPS_DIR}/${BASE}.dump"
SHA_FILE="${BACKUPS_DIR}/${BASE}.dump.sha256"
cd "$BACKUPS_DIR"

# Discover parts in numeric order (part0.gz, part1.gz, ... partN.gz - any N).
PART_FILES=()
i=0
while [[ -f "${BASE}.part${i}.gz" ]]; do
  PART_FILES+=("${BASE}.part${i}.gz")
  i=$((i + 1))
done

if [[ "${#PART_FILES[@]}" -eq 0 ]]; then
  echo "No parts found matching ${BACKUPS_DIR}/${BASE}.part*.gz" >&2
  exit 1
fi
echo "Found ${#PART_FILES[@]} part(s)."

echo "Assembling ${OUT} ..."
gunzip -c "${PART_FILES[@]}" > "${OUT}.tmp"
mv "${OUT}.tmp" "$OUT"

if [[ -f "$SHA_FILE" ]]; then
  echo "Checking SHA-256 ..."
  expected="$(awk '{print $1}' "$SHA_FILE")"
  actual="$("${SHA_CMD[@]}" "$OUT" | awk '{print $1}')"
  if [[ "$expected" != "$actual" ]]; then
    echo "Checksum mismatch!" >&2
    echo "  expected: $expected" >&2
    echo "  actual:   $actual" >&2
    exit 1
  fi
  echo "Checksum OK."
fi

echo "Done: ${OUT}"
