#!/usr/bin/env bash
# Load images produced by export-container-images.sh.
#
# Usage:
#   ./scripts/load-container-images.sh output/container-images/
#   # or from inside the bundle directory:
#   ./load-container-images.sh .
#
# RHEL Podman strict short-name mode strips short-name RepoTags (postgres:15,
# redis:7-alpine) from loaded archives, leaving images as <none>:<none>.
# This script detects that case via before/after image-ID comparison and
# applies the correct fully-qualified tag explicitly.

set -euo pipefail

DIR="${1:-.}"
[[ -d "$DIR" ]] || { echo "Usage: $0 [directory-containing-tar-files]" >&2; exit 1; }

# Prefer podman when both are present (production target is RHEL/Podman).
if command -v podman >/dev/null 2>&1; then
  CMD=podman
elif command -v docker >/dev/null 2>&1; then
  CMD=docker
else
  echo "Install docker or podman" >&2; exit 1
fi
echo "Using: $CMD"

# Load a tar and ensure it ends up tagged as $want_tag.
# If the engine strips the embedded tag (RHEL strict mode), we find the new
# image by diffing image IDs before and after, then tag by ID.
load_and_tag() {
  local file="$1"
  local want_tag="$2"

  [[ -f "$file" ]] || { echo "Missing: $file" >&2; exit 1; }
  echo ""
  echo "Loading $(basename "$file") ..."

  # Snapshot IDs already present
  local before
  before=$("$CMD" images --no-trunc -q 2>/dev/null | sort -u)

  "$CMD" load -i "$file"

  # If the archive's own tag was accepted, we're done
  if "$CMD" image inspect "$want_tag" >/dev/null 2>&1; then
    echo "  OK: $want_tag"
    return 0
  fi

  # Find the newly added image ID
  local after new_id
  after=$("$CMD" images --no-trunc -q 2>/dev/null | sort -u)
  new_id=$(comm -13 <(printf '%s\n' "$before") <(printf '%s\n' "$after") | head -1)

  if [[ -n "$new_id" ]]; then
    echo "  Tag was stripped (RHEL strict mode); tagging $new_id -> $want_tag"
    "$CMD" tag "$new_id" "$want_tag"
  else
    # Image was already in store (re-run); just verify the tag
    if ! "$CMD" image inspect "$want_tag" >/dev/null 2>&1; then
      echo "  WARNING: could not find or tag image for $want_tag" >&2
    fi
  fi
}

# Add short-name alias (best-effort; may be refused on strict mode but the fq
# name is what airgap-stack-up.sh uses when POSTGRES_IMAGE / REDIS_IMAGE are set)
alias_short() {
  local fq="$1" short="$2"
  if "$CMD" image inspect "$fq" >/dev/null 2>&1 && \
     ! "$CMD" image inspect "$short" >/dev/null 2>&1; then
    "$CMD" tag "$fq" "$short" 2>/dev/null && echo "  Also tagged: $short" || true
  fi
}

# --- base images (tags in archives are short names; use fq as canonical) ---
load_and_tag "$DIR/postgres-15.tar"    "docker.io/library/postgres:15"
alias_short  "docker.io/library/postgres:15" "postgres:15"

load_and_tag "$DIR/redis-7-alpine.tar" "docker.io/library/redis:7-alpine"
alias_short  "docker.io/library/redis:7-alpine" "redis:7-alpine"

# --- app images (read canonical tag from MANIFEST.txt) ---
MANIFEST="$DIR/MANIFEST.txt"
if [[ -f "$MANIFEST" ]]; then
  IMAGE_PREFIX=$(grep '^IMAGE_PREFIX=' "$MANIFEST" | head -1 | cut -d= -f2 | tr -d '[:space:]')
  IMAGE_TAG=$(grep    '^IMAGE_TAG='    "$MANIFEST" | head -1 | cut -d= -f2 | tr -d '[:space:]')
  load_and_tag "$DIR/recruit-backend.tar"  "${IMAGE_PREFIX}/recruit-backend:${IMAGE_TAG}"
  load_and_tag "$DIR/recruit-frontend.tar" "${IMAGE_PREFIX}/recruit-frontend:${IMAGE_TAG}"
else
  echo "MANIFEST.txt not found; loading app images without tag verification."
  "$CMD" load -i "$DIR/recruit-backend.tar"
  "$CMD" load -i "$DIR/recruit-frontend.tar"
fi

echo ""
echo "Done. Loaded images:"
"$CMD" images --format "{{.Repository}}:{{.Tag}}" | grep -v '<none>' || true
