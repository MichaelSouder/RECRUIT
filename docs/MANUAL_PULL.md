# Manually pull all container images

Use this when you have network access and want to **`docker pull`** / **`podman pull`** every image the stack needs—no Actions artifacts required.

## 1. Log in to GitHub Container Registry (app images only)

Private packages need a GitHub **Personal Access Token** with **`read:packages`**.

```bash
echo YOUR_GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

For Podman:

```bash
echo YOUR_GITHUB_TOKEN | podman login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

Public packages can be pulled **without** login.

## 2. Set your image prefix

Use your GitHub username or org in **lowercase** (GHCR requires lowercase paths):

```bash
export IMAGE_PREFIX=ghcr.io/michaelsouder   # change to your namespace
export TAG=latest
```

## 3. Pull RECRUIT app images (GHCR)

```bash
docker pull "${IMAGE_PREFIX}/recruit-backend:${TAG}"
docker pull "${IMAGE_PREFIX}/recruit-frontend:${TAG}"
```

## 4. Pull Postgres and Redis (Docker Hub)

These are **not** stored in GHCR for this project; they come from Docker Hub’s official images:

```bash
docker pull docker.io/library/postgres:15
docker pull docker.io/library/redis:7-alpine
```

Short form (same images):

```bash
docker pull postgres:15
docker pull redis:7-alpine
```

## 5. One-shot script (optional)

From the repo root:

```bash
chmod +x scripts/pull-all-images.sh
IMAGE_PREFIX=ghcr.io/youruser ./scripts/pull-all-images.sh
```

## 6. Air-gapped use after pulling

On a connected machine, pull everything above, then save to files and transfer:

```bash
docker save -o postgres-15.tar postgres:15
docker save -o redis-7-alpine.tar redis:7-alpine
docker save -o recruit-backend.tar "${IMAGE_PREFIX}/recruit-backend:${TAG}"
docker save -o recruit-frontend.tar "${IMAGE_PREFIX}/recruit-frontend:${TAG}"
```

Or use **`scripts/export-container-images.sh`**, which pulls/builds and saves all four into `output/container-images/`.

## Reference: what runs in production

| Image | Pull command |
|-------|----------------|
| PostgreSQL | `postgres:15` |
| Redis | `redis:7-alpine` |
| API | `${IMAGE_PREFIX}/recruit-backend:${TAG}` |
| Web UI | `${IMAGE_PREFIX}/recruit-frontend:${TAG}` |

These match **`docker-compose.prod.yml`** and **`docs/DEPLOY_PODMAN.md`**.
