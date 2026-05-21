#!/usr/bin/env bash
# Reassemble recruit_prod_cutover_20260521T1455Z.dump from 7 gzip parts, then pg_restore.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
BASE="recruit_prod_cutover_20260521T1455Z"
OUT="${DIR}/${BASE}.dump"
SHA_FILE="${DIR}/${BASE}.dump.sha256"

cd "$DIR"
for i in 0 1 2 3 4 5 6; do
  if [[ ! -f "${BASE}.part${i}.gz" ]]; then
    echo "Missing ${BASE}.part${i}.gz" >&2
    exit 1
  fi
done

echo "Assembling ${OUT} ..."
gunzip -c \
  "${BASE}.part0.gz" "${BASE}.part1.gz" "${BASE}.part2.gz" \
  "${BASE}.part3.gz" "${BASE}.part4.gz" "${BASE}.part5.gz" \
  "${BASE}.part6.gz" > "${OUT}.tmp"
mv "${OUT}.tmp" "${OUT}"

if [[ -f "$SHA_FILE" ]]; then
  echo "Checking SHA-256 ..."
  expected="$(awk '{print $1}' "$SHA_FILE")"
  actual="$(shasum -a 256 "$OUT" | awk '{print $1}')"
  if [[ "$expected" != "$actual" ]]; then
    echo "Checksum mismatch!" >&2
    echo "  expected: $expected" >&2
    echo "  actual:   $actual" >&2
    exit 1
  fi
  echo "Checksum OK."
fi

echo "Done: ${OUT}"
echo "Restore example:"
echo "  pg_restore --dbname=\"\$PROD_DATABASE_URL\" --no-owner --no-acl --verbose \"${OUT}\""
