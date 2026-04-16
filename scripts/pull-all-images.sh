#!/usr/bin/env bash
# Manually pull every image needed for RECRUIT (GHCR app images + Docker Hub Postgres/Redis).
#
# Usage:
#   IMAGE_PREFIX=ghcr.io/yourgithubuser ./scripts/pull-all-images.sh
#   IMAGE_TAG=latest IMAGE_PREFIX=ghcr.io/foo ./scripts/pull-all-images.sh
#
# Optional: DOCKER_CMD=podman

set -euo pipefail

IMAGE_PREFIX="${IMAGE_PREFIX:?Set IMAGE_PREFIX, e.g. ghcr.io/michaelsouder (lowercase)}"
TAG="${IMAGE_TAG:-latest}"

DOCKER_CMD="${DOCKER_CMD:-}"
if [[ -z "$DOCKER_CMD" ]]; then
  if command -v docker >/dev/null 2>&1; then
    DOCKER_CMD=docker
  elif command -v podman >/dev/null 2>&1; then
    DOCKER_CMD=podman
  else
    echo "Install docker or podman" >&2
    exit 1
  fi
fi

echo "Using: $DOCKER_CMD"
echo "Pulling RECRUIT images from GHCR..."
$DOCKER_CMD pull "${IMAGE_PREFIX}/recruit-backend:${TAG}"
$DOCKER_CMD pull "${IMAGE_PREFIX}/recruit-frontend:${TAG}"

echo "Pulling Postgres and Redis from Docker Hub..."
$DOCKER_CMD pull postgres:15
$DOCKER_CMD pull redis:7-alpine

echo "Done. All four images are present locally:"
$DOCKER_CMD images --format 'table {{.Repository}}\t{{.Tag}}\t{{.ID}}' | head -1
$DOCKER_CMD images | grep -E "recruit-backend|recruit-frontend|^postgres|^redis" || true
