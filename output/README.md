# Offline container images (air-gapped deploy)

This folder is where **`scripts/export-container-images.sh`** writes **`.tar`** archives. A full deployment needs **four** images — **PostgreSQL**, **Redis**, **recruit-backend**, and **recruit-frontend**.

**Primary guide:** **`docs/AIRGAP_DEPLOY.md`** (end-to-end: bundle, transfer, load, `docker run` / `podman run`, verification). Each export also copies **`AIRGAP_DEPLOY.md`**, **`load-container-images.sh`**, **`airgap-stack-up.sh`**, and **`recruit-airgap.env.example`** (copy to **`recruit-airgap.env`** for local secrets) into **`output/container-images/`** so the transfer folder is self-contained.

**If you clone this repository:** the `*.tar` files under `output/container-images/` are stored with **Git LFS**. Install [Git LFS](https://git-lfs.com/), run `git lfs install` once, then `git lfs pull` (or clone with a client that supports LFS) so the archives are real files, not tiny pointer stubs.

## What is included (all four are required)

| # | File | Image | Source |
|---|------|--------|--------|
| 1 | `postgres-15.tar` | `postgres:15` | Docker Hub |
| 2 | `redis-7-alpine.tar` | `redis:7-alpine` | Docker Hub |
| 3 | `recruit-backend.tar` | `ghcr.io/your-user/recruit-backend:latest` | Built from this repo |
| 4 | `recruit-frontend.tar` | `ghcr.io/your-user/recruit-frontend:latest` | Built from this repo |

**Note:** GitHub Container Registry (Packages) only shows the **two RECRUIT app** images. **Postgres and Redis are not published to GHCR** — they only appear in this offline export (or in the CI artifacts below).

## Why this folder is usually empty in git

Tarballs are **large** (often 1–2+ GB total) and are **not committed**. `output/container-images/` is gitignored.

## How to get the files

### Option A — Manual `docker pull` / `podman pull` (with network)

If you can reach the internet, pull all four images from the registries directly—no zip download. See **`docs/MANUAL_PULL.md`** or run:

```bash
export IMAGE_PREFIX=ghcr.io/yourgithubuser
chmod +x scripts/pull-all-images.sh
./scripts/pull-all-images.sh
```

(Log in to `ghcr.io` first if your app images are private.)

### Option B — GitHub Actions (two artifacts — download **both**)

1. **Actions** → **Export container images** → **Run workflow**.
2. When the run finishes, open it → **Artifacts**. Download **both**:
   - **`recruit-infra-postgres-redis`** — contains **Postgres** and **Redis** `.tar` files plus `README-AIR-GAP.txt`
   - **`recruit-app-backend-frontend`** — contains **backend** and **frontend** `.tar` files, `MANIFEST.txt`, and `README-AIR-GAP.txt`
3. Unzip both into **one** folder (e.g. `output/container-images/`) so all **four** `.tar` files sit together.
4. Run **`./scripts/load-container-images.sh`** on that folder (see below).

If you only download the app artifact, you will **not** have Postgres or Redis — you need **both** artifacts (or a full local export).

### Option C — Generate locally (all four in one folder)

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

Output defaults to **`output/container-images/`** (`OUTPUT_DIR` overrides).

## Load on the air-gapped machine

Put all **four** `.tar` files in one directory, then:

```bash
chmod +x scripts/load-container-images.sh
./scripts/load-container-images.sh /path/to/that/directory
```

Then deploy with Podman/Docker per `docs/DEPLOY_PODMAN.md` and `docker-compose.prod.yml`.
