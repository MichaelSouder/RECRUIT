#!/usr/bin/env bash
# Load images produced by export-container-images.sh.
#
# Usage:
#   ./scripts/load-container-images.sh output/container-images/
#   ./load-container-images.sh .   (from inside the bundle directory)

set -euo pipefail

DIR="${1:-.}"
[[ -d "$DIR" ]] || { echo "Usage: $0 [directory-containing-tar-files]" >&2; exit 1; }

if command -v podman >/dev/null 2>&1; then
  CMD=podman
elif command -v docker >/dev/null 2>&1; then
  CMD=docker
else
  echo "Install docker or podman" >&2; exit 1
fi
echo "Using: $CMD"

# Load each tar.  Archives now embed explicit fully-qualified RepoTags so
# podman tags them correctly on load without any retag tricks.
for f in postgres-15.tar redis-7-alpine.tar recruit-backend.tar recruit-frontend.tar; do
  path="$DIR/$f"
  [[ -f "$path" ]] || { echo "Missing: $path" >&2; exit 1; }
  echo ""
  echo "==> $f"
  "$CMD" load -i "$path"
done

# Safety net: if any base image still landed as <none>:<none> (e.g. older
# archives without embedded tags), identify and tag by image ENV variables.
tag_if_untagged() {
  local want_tag="$1"
  local env_pattern="$2"
  if "$CMD" image inspect "$want_tag" >/dev/null 2>&1; then
    return 0  # already tagged
  fi
  echo "  $want_tag not found — scanning untagged images by ENV pattern '$env_pattern' ..."
  local id
  for id in $("$CMD" images -q 2>/dev/null); do
    local env_str
    env_str=$("$CMD" inspect "$id" --format '{{range .Config.Env}}{{.}} {{end}}' 2>/dev/null || true)
    if echo "$env_str" | grep -q "$env_pattern"; then
      echo "  Tagging $id -> $want_tag"
      "$CMD" tag "$id" "$want_tag"
      return 0
    fi
  done
  echo "  WARNING: could not find image to tag as $want_tag" >&2
}

tag_if_untagged "docker.io/library/postgres:15"    "PGDATA"
tag_if_untagged "docker.io/library/redis:7-alpine" "REDIS_VERSION"

MANIFEST="$DIR/MANIFEST.txt"
if [[ -f "$MANIFEST" ]]; then
  IMAGE_PREFIX=$(grep '^IMAGE_PREFIX=' "$MANIFEST" | head -1 | cut -d= -f2 | tr -d '[:space:]')
  IMAGE_TAG=$(grep    '^IMAGE_TAG='    "$MANIFEST" | head -1 | cut -d= -f2 | tr -d '[:space:]')
  tag_if_untagged "${IMAGE_PREFIX}/recruit-backend:${IMAGE_TAG}"  "APP_MODULE\|uvicorn\|PYTHONDONTWRITEBYTECODE"
  tag_if_untagged "${IMAGE_PREFIX}/recruit-frontend:${IMAGE_TAG}" "NGINX_VERSION"
fi

echo ""
echo "Images loaded:"
"$CMD" images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}"
