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

echo "Done. See MANIFEST.txt in the same folder for image names."
