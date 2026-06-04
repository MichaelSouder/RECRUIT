#!/usr/bin/env bash
# Load images produced by export-container-images.sh (run from directory containing the .tar files).
#
# Usage:
#   cd output/container-images
#   ../../scripts/load-container-images.sh
#
# Or:
#   ./scripts/load-container-images.sh /path/to/container-images

set -euo pipefail

DIR="${1:-.}"
if [[ ! -d "$DIR" ]]; then
  echo "Usage: $0 [directory-containing-tar-files]" >&2
  exit 1
fi

if command -v docker >/dev/null 2>&1; then
  CMD=docker
elif command -v podman >/dev/null 2>&1; then
  CMD=podman
else
  echo "Install docker or podman" >&2
  exit 1
fi

for f in postgres-15.tar redis-7-alpine.tar recruit-backend.tar recruit-frontend.tar; do
  path="$DIR/$f"
  if [[ ! -f "$path" ]]; then
    echo "Missing: $path" >&2
    exit 1
  fi
  echo "Loading $f ..."
  $CMD load -i "$path"
done

# Ensure both short and fully-qualified names exist for the base images.
#
# RHEL Podman strict short-name mode stores a loaded "postgres:15" as
# "localhost/postgres:15", not "docker.io/library/postgres:15".  The old
# logic only tried to alias fq→short, so on RHEL neither alias was created.
# We now try all three source prefixes so the right tag is always added
# regardless of which name the engine assigned after load.
add_alias() {
  local src="$1" dst="$2"
  if $CMD image inspect "$src" >/dev/null 2>&1; then
    $CMD tag "$src" "$dst" 2>/dev/null && echo "  aliased $src -> $dst" || true
  fi
}

for base in "postgres:15" "redis:7-alpine"; do
  fq="docker.io/library/${base}"
  loc="localhost/${base}"
  # localhost/ -> fq  (RHEL strict mode: loaded as localhost/)
  add_alias "$loc" "$fq"
  # fq -> short       (non-strict mode / Docker: loaded as fq)
  add_alias "$fq"  "$base"
  # short -> fq       (already short but fq missing)
  add_alias "$base" "$fq"
done

echo "Done. See MANIFEST.txt in the same folder for image names."
