#!/usr/bin/env bash
# Export all images needed to run RECRUIT (same stack as docker-compose.prod.yml)
# into output/container-images/ as .tar files plus a manifest.
#
# Usage (from repo root):
#   ./scripts/export-container-images.sh
#   IMAGE_PREFIX=ghcr.io/myuser IMAGE_TAG=latest ./scripts/export-container-images.sh
#
# Requires: docker or podman (DOCKER_CMD overrides, e.g. DOCKER_CMD=podman)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${OUTPUT_DIR:-$ROOT/output/container-images}"
IMAGE_PREFIX="${IMAGE_PREFIX:-ghcr.io/michaelsouder}"
TAG="${IMAGE_TAG:-latest}"

DOCKER_CMD="${DOCKER_CMD:-}"
if [[ -n "$DOCKER_CMD" ]] && ! command -v "$DOCKER_CMD" >/dev/null 2>&1; then
  echo "Error: DOCKER_CMD=$DOCKER_CMD not found" >&2
  exit 1
fi
if [[ -z "$DOCKER_CMD" ]]; then
  if command -v docker >/dev/null 2>&1; then
    DOCKER_CMD=docker
  elif command -v podman >/dev/null 2>&1; then
    DOCKER_CMD=podman
  else
    echo "Error: install docker or podman, or set DOCKER_CMD" >&2
    exit 1
  fi
fi

mkdir -p "$OUT_DIR"

echo "Using: $DOCKER_CMD"
echo "Output: $OUT_DIR"
echo "App images: ${IMAGE_PREFIX}/recruit-backend:${TAG} and ${IMAGE_PREFIX}/recruit-frontend:${TAG}"

echo "==> Pull base images"
$DOCKER_CMD pull postgres:15
$DOCKER_CMD pull redis:7-alpine

echo "==> Build application images"
$DOCKER_CMD build -t "${IMAGE_PREFIX}/recruit-backend:${TAG}" "$ROOT/src/backend"

$DOCKER_CMD build \
  --build-arg "VITE_BASE_PATH=/recruit/" \
  --build-arg "VITE_API_URL=" \
  --build-arg "NGINX_CONFIG=recruit" \
  --build-arg "HEALTH_URI=/recruit/health" \
  -t "${IMAGE_PREFIX}/recruit-frontend:${TAG}" \
  "$ROOT/src/frontend"

echo "==> Save images to tar archives"

save_one() {
  local ref="$1"
  local file="$2"
  echo "    saving $ref -> $(basename "$file")"
  $DOCKER_CMD save -o "$file" "$ref"
}

save_one "postgres:15" "$OUT_DIR/postgres-15.tar"
save_one "redis:7-alpine" "$OUT_DIR/redis-7-alpine.tar"
save_one "${IMAGE_PREFIX}/recruit-backend:${TAG}" "$OUT_DIR/recruit-backend.tar"
save_one "${IMAGE_PREFIX}/recruit-frontend:${TAG}" "$OUT_DIR/recruit-frontend.tar"

MANIFEST="$OUT_DIR/MANIFEST.txt"
{
  echo "RECRUIT container image export"
  echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "IMAGE_PREFIX=${IMAGE_PREFIX}"
  echo "IMAGE_TAG=${TAG}"
  echo ""
  echo "Load on an offline machine (requires docker or podman):"
  echo "  for f in postgres-15.tar redis-7-alpine.tar recruit-backend.tar recruit-frontend.tar; do"
  echo "    $DOCKER_CMD load -i \"\$f\""
  echo "  done"
  echo ""
  echo "Image references after load:"
  echo "  postgres:15"
  echo "  redis:7-alpine"
  echo "  ${IMAGE_PREFIX}/recruit-backend:${TAG}"
  echo "  ${IMAGE_PREFIX}/recruit-frontend:${TAG}"
} > "$MANIFEST"

echo "==> Done. Files in $OUT_DIR:"
ls -lh "$OUT_DIR"
echo ""
echo "Manifest: $MANIFEST"
