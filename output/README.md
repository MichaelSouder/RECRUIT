# Offline container images

This folder is where **`scripts/export-container-images.sh`** writes **`.tar`** archives of every image needed to run the production stack (Postgres, Redis, backend, frontend).

## Why this folder is usually empty in git

Image tarballs are **large** (often 1–2+ GB total) and are **not committed** to the repository. They are listed in `.gitignore`.

## How to get the files

### Option A — GitHub Actions (recommended)

1. Open the repository on GitHub → **Actions**.
2. Run the workflow **“Export container images”** (**Run workflow**).
3. When it finishes, open the run → **Artifacts** → download **`recruit-container-images`**.

Unzip the artifact; you will have `postgres-15.tar`, `redis-7-alpine.tar`, `recruit-backend.tar`, `recruit-frontend.tar`, and `MANIFEST.txt` in `output/container-images/` (or the layout described in the workflow).

### Option B — Generate locally

From the repo root (Docker or Podman installed):

```bash
chmod +x scripts/export-container-images.sh
./scripts/export-container-images.sh
```

Optional:

```bash
export IMAGE_PREFIX=ghcr.io/yourgithubuser
export IMAGE_TAG=latest
./scripts/export-container-images.sh
```

Output path defaults to **`output/container-images/`** (override with `OUTPUT_DIR`).

## Load images on the target machine

```bash
chmod +x scripts/load-container-images.sh
./scripts/load-container-images.sh output/container-images
```

Then deploy with Podman or Docker using the same image names as in `docker-compose.prod.yml` and `docs/DEPLOY_PODMAN.md`.
