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
# Default bundle folder (override: OUTPUT_DIR=...). Also valid: output/container-images
OUT_DIR="${OUTPUT_DIR:-$ROOT/container-images}"
IMAGE_PREFIX="${IMAGE_PREFIX:-ghcr.io/michaelsouder}"
TAG="${IMAGE_TAG:-latest}"
# Red Hat / typical prod servers are linux/amd64. Export arm64 Mac images without this.
TARGET_PLATFORM="${TARGET_PLATFORM:-linux/amd64}"

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
echo "Target platform: $TARGET_PLATFORM (RHEL/x86_64 and most servers)"
echo ""

pull_image() {
  local ref="$1"
  if [[ "$DOCKER_CMD" == "podman" ]]; then
    $DOCKER_CMD pull --platform "$TARGET_PLATFORM" "$ref"
  else
    $DOCKER_CMD pull --platform "$TARGET_PLATFORM" "$ref"
  fi
}

build_image() {
  local tag="$1"
  local context="$2"
  shift 2
  if [[ "$DOCKER_CMD" == "docker" ]]; then
    if ! docker buildx version >/dev/null 2>&1; then
      echo "Error: docker buildx required to build $TARGET_PLATFORM images on this host." >&2
      exit 1
    fi
    docker buildx build --platform "$TARGET_PLATFORM" --load -t "$tag" "$@" "$context"
  else
    $DOCKER_CMD build --platform "$TARGET_PLATFORM" -t "$tag" "$@" "$context"
  fi
}

if [[ "$DOCKER_CMD" == "docker" ]]; then
  docker buildx inspect recruit-export-builder >/dev/null 2>&1 \
    || docker buildx create --name recruit-export-builder --use >/dev/null
  docker buildx inspect --bootstrap >/dev/null 2>&1 || true
fi

echo ""
echo "This export includes ALL FOUR images required for air-gapped deploy:"
echo "  1. postgres:15          -> postgres-15.tar          (PostgreSQL — from Docker Hub)"
echo "  2. redis:7-alpine       -> redis-7-alpine.tar       (Redis — from Docker Hub)"
echo "  3. ${IMAGE_PREFIX}/recruit-backend:${TAG}  -> recruit-backend.tar"
echo "  4. ${IMAGE_PREFIX}/recruit-frontend:${TAG} -> recruit-frontend.tar"
echo ""

echo "==> Pull base images ($TARGET_PLATFORM)"
pull_image "docker.io/library/postgres:15"
pull_image "docker.io/library/redis:7-alpine"
# Tags used after load (match load-container-images.sh)
$DOCKER_CMD tag "docker.io/library/postgres:15" postgres:15 2>/dev/null || true
$DOCKER_CMD tag "docker.io/library/redis:7-alpine" redis:7-alpine 2>/dev/null || true

echo "==> Build application images ($TARGET_PLATFORM)"
build_image "${IMAGE_PREFIX}/recruit-backend:${TAG}" "$ROOT/src/backend"

build_image "${IMAGE_PREFIX}/recruit-frontend:${TAG}" "$ROOT/src/frontend" \
  --build-arg "VITE_BASE_PATH=/recruit/" \
  --build-arg "VITE_API_URL=" \
  --build-arg "NGINX_CONFIG=recruit" \
  --build-arg "HEALTH_URI=/recruit/health"

echo "==> Save images to tar archives"

save_one() {
  local ref="$1"
  local file="$2"
  echo "    saving $ref -> $(basename "$file")"
  rm -f "$file"
  if command -v skopeo >/dev/null 2>&1; then
    # Reliable linux/amd64 export on Apple Silicon (avoids docker save digest bugs).
    if [[ "$ref" == docker.io/* ]] || [[ "$ref" == */*/* ]]; then
      skopeo copy "docker://${ref}" "docker-archive:${file}" \
        --override-os linux --override-arch amd64 2>/dev/null \
        || skopeo copy "docker://${ref}" "docker-archive:${file}"
    else
      skopeo copy "docker-daemon:${ref}" "docker-archive:${file}" \
        --override-os linux --override-arch amd64 2>/dev/null \
        || skopeo copy "docker-daemon:${ref}" "docker-archive:${file}"
    fi
  else
    echo "    (install skopeo for reliable linux/amd64 exports on Apple Silicon)" >&2
    $DOCKER_CMD save -o "$file" "$ref"
  fi
}

if ! command -v skopeo >/dev/null 2>&1; then
  echo "Warning: skopeo not found; docker save may fail for multi-arch base images on arm64 Macs." >&2
  echo "  Install: brew install skopeo" >&2
fi

save_one "docker.io/library/postgres:15" "$OUT_DIR/postgres-15.tar"
save_one "docker.io/library/redis:7-alpine" "$OUT_DIR/redis-7-alpine.tar"
save_one "${IMAGE_PREFIX}/recruit-backend:${TAG}" "$OUT_DIR/recruit-backend.tar"
save_one "${IMAGE_PREFIX}/recruit-frontend:${TAG}" "$OUT_DIR/recruit-frontend.tar"

MANIFEST="$OUT_DIR/MANIFEST.txt"
{
  echo "RECRUIT container image export"
  echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "TARGET_PLATFORM=${TARGET_PLATFORM}"
  echo "IMAGE_PREFIX=${IMAGE_PREFIX}"
  echo "IMAGE_TAG=${TAG}"
  echo ""
  echo "Required files (all four — Postgres & Redis are NOT in GHCR; they ship only in this export):"
  echo "  postgres-15.tar"
  echo "  redis-7-alpine.tar"
  echo "  recruit-backend.tar"
  echo "  recruit-frontend.tar"
  echo ""
  echo "Bundled documentation (same folder after export):"
  echo "  AIRGAP_DEPLOY.md"
  echo "  load-container-images.sh"
  echo "  airgap-stack-up.sh"
  echo "  recruit-airgap.env.example"
  echo "  README-AIR-GAP.txt"
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

README_AIRGAP="$OUT_DIR/README-AIR-GAP.txt"
{
  echo "Air-gapped deployment — required container images"
  echo "=================================================="
  echo ""
  echo "You need ALL of the following .tar files on the offline machine:"
  echo ""
  echo "  Infrastructure (Docker Hub originals):"
  echo "    postgres-15.tar       -> image: postgres:15"
  echo "    redis-7-alpine.tar    -> image: redis:7-alpine"
  echo ""
  echo "  RECRUIT application (built from this repo):"
  echo "    recruit-backend.tar   -> image: ${IMAGE_PREFIX}/recruit-backend:${TAG}"
  echo "    recruit-frontend.tar  -> image: ${IMAGE_PREFIX}/recruit-frontend:${TAG}"
  echo ""
  echo "GitHub Container Registry only stores the app images; Postgres and Redis are"
  echo "included only in the offline export (this bundle / CI artifacts)."
  echo ""
  echo "Full procedure: read AIRGAP_DEPLOY.md in this folder (copy of docs/AIRGAP_DEPLOY.md)."
  echo "Load images: ./load-container-images.sh ."
  echo "Start stack: copy recruit-airgap.env.example to recruit-airgap.env, edit, then ./airgap-stack-up.sh ."
  echo "Or from repo: ./scripts/load-container-images.sh /path/to/bundle"
} > "$README_AIRGAP"

echo "==> Copy air-gap documentation and helper scripts into bundle"
cp "$ROOT/docs/AIRGAP_DEPLOY.md" "$OUT_DIR/AIRGAP_DEPLOY.md"
cp "$ROOT/scripts/load-container-images.sh" "$OUT_DIR/load-container-images.sh"
cp "$ROOT/scripts/airgap-stack-up.sh" "$OUT_DIR/airgap-stack-up.sh"
cp "$ROOT/scripts/recruit-airgap.env.example" "$OUT_DIR/recruit-airgap.env.example"
chmod +x "$OUT_DIR/load-container-images.sh" "$OUT_DIR/airgap-stack-up.sh"

echo "==> Done. Files in $OUT_DIR:"
ls -lh "$OUT_DIR"
echo ""
echo "Manifest: $MANIFEST"
echo "Air-gap readme: $README_AIRGAP"
