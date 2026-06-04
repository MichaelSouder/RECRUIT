#!/usr/bin/env bash
# Load images produced by export-container-images.sh.
#
# Usage:
#   ./scripts/load-container-images.sh output/container-images/
#   ./load-container-images.sh .   (from inside the bundle directory)

set -euo pipefail

DIR="${1:-.}"
[[ -d "$DIR" ]] || { echo "Usage: $0 [directory-containing-tar-files]" >&2; exit 1; }

# Prefer podman on RHEL/production hosts.
if command -v podman >/dev/null 2>&1; then
  CMD=podman
elif command -v docker >/dev/null 2>&1; then
  CMD=docker
else
  echo "Install docker or podman" >&2; exit 1
fi
echo "Using: $CMD"

# Remove untagged images left over from a previous failed load attempt,
# otherwise podman load may skip re-loading (image already in store).
echo "Removing leftover untagged images ..."
"$CMD" rmi $("$CMD" images -q -f dangling=true 2>/dev/null) 2>/dev/null || true

# Load a tar and ensure it ends up tagged as $want_tag.
#
# RHEL Podman strict short-name mode refuses to tag short names (postgres:15)
# so the image lands as <none>:<none>.  We capture "Loaded image: sha256:..."
# from podman's own output and retag by that ID.
load_and_tag() {
  local file="$1"
  local want_tag="$2"

  [[ -f "$file" ]] || { echo "ERROR: missing $file" >&2; exit 1; }
  echo ""
  echo "==> $(basename "$file")"

  # Capture stdout+stderr so we can parse the loaded image reference.
  local out
  out=$("$CMD" load -i "$file" 2>&1)
  echo "$out"

  # Already tagged correctly (archive tag was accepted or re-run)?
  if "$CMD" image inspect "$want_tag" >/dev/null 2>&1; then
    echo "    OK: $want_tag"
    return 0
  fi

  # Parse "Loaded image: sha256:..." or "Loaded image(s): name:tag" from output.
  local ref
  ref=$(printf '%s\n' "$out" \
        | grep -i 'loaded image' \
        | sed 's/.*Loaded image[s]*:[[:space:]]*//' \
        | tr -d '\r' \
        | head -1)

  if [[ -z "$ref" ]]; then
    echo "    ERROR: no 'Loaded image' line in load output." >&2
    echo "    Full output was:" >&2
    printf '%s\n' "$out" >&2
    exit 1
  fi

  echo "    Tagging: $ref  ->  $want_tag"
  "$CMD" tag "$ref" "$want_tag"
  echo "    OK: $want_tag"
}

# ── base images ──────────────────────────────────────────────────────────────
# The docker-archive embeds short RepoTags (postgres:15, redis:7-alpine).
# RHEL strict mode strips them; we tag explicitly with the fq name.
load_and_tag "$DIR/postgres-15.tar"    "docker.io/library/postgres:15"
load_and_tag "$DIR/redis-7-alpine.tar" "docker.io/library/redis:7-alpine"

# ── app images ───────────────────────────────────────────────────────────────
MANIFEST="$DIR/MANIFEST.txt"
if [[ -f "$MANIFEST" ]]; then
  IMAGE_PREFIX=$(grep '^IMAGE_PREFIX=' "$MANIFEST" | head -1 | cut -d= -f2 | tr -d '[:space:]')
  IMAGE_TAG=$(grep    '^IMAGE_TAG='    "$MANIFEST" | head -1 | cut -d= -f2 | tr -d '[:space:]')
  load_and_tag "$DIR/recruit-backend.tar"  "${IMAGE_PREFIX}/recruit-backend:${IMAGE_TAG}"
  load_and_tag "$DIR/recruit-frontend.tar" "${IMAGE_PREFIX}/recruit-frontend:${IMAGE_TAG}"
else
  echo "MANIFEST.txt not found in $DIR; loading app images without tag verification."
  "$CMD" load -i "$DIR/recruit-backend.tar"
  "$CMD" load -i "$DIR/recruit-frontend.tar"
fi

# ── summary ──────────────────────────────────────────────────────────────────
echo ""
echo "Images now present:"
"$CMD" images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}"
