# Offline container images (air-gapped deploy)

This folder is where **`scripts/export-container-images.sh`** writes **`.tar`** archives. A full deployment needs **four** images — **PostgreSQL**, **Redis**, **recruit-backend**, and **recruit-frontend**.

**Primary guide:** **`docs/AIRGAP_DEPLOY.md`** (end-to-end: bundle, transfer, load, `docker run` / `podman run`, verification). Each export also copies **`AIRGAP_DEPLOY.md`**, **`airgap-cli`** (+ its **`airgap/`** package — Python 3 standard library only, no `pip install` needed), and **`recruit-airgap.env.example`** (copy to **`recruit-airgap.env`** for local secrets) into **`output/container-images/`** so the transfer folder is self-contained.

**If you clone this repository:** the `*.tar` files under `output/container-images/` are stored with **Git LFS**. Install [Git LFS](https://git-lfs.com/), run `git lfs install` once, then `git lfs pull` (or clone with a client that supports LFS) so the archives are real files, not tiny pointer stubs.

## What is included (all four are required)

| # | File | Image | Source |
|---|------|--------|--------|
| 1 | `postgres-15.tar` | `postgres:15` | Docker Hub |
| 2 | `redis-7-alpine.tar` | `redis:7-alpine` | Docker Hub |
| 3 | `recruit-backend.tar` | `ghcr.io/your-user/recruit-backend:latest` | Built from this repo |
| 4 | `recruit-frontend.tar` | `ghcr.io/your-user/recruit-frontend:latest` | Built from this repo |

**Note:** GitHub Container Registry (Packages) only shows the **two RECRUIT app** images. **Postgres and Redis are not published to GHCR** — they only appear in this offline export (or in the CI artifacts below).

## Why the tarballs *are* committed here

Unlike most build output, the four `.tar` files under `output/container-images/` **are committed**, via **Git LFS** (see `.gitattributes`: `output/container-images/*.tar filter=lfs`). That is deliberate — it is what lets an air-gapped host with a deploy clone run **`scripts/airgap-cli cron-update`**, which rolls out an update only when this folder changes between commits. If these were gitignored, unattended updates could not work at all.

Consequence: **a new bundle only reaches the air-gapped host once it is committed and pushed.** Re-running the export locally is not enough.

Note the root-level **`container-images/`** folder *is* gitignored — that is the export script's default output location, which is why you must pass `OUTPUT_DIR` when refreshing the committed bundle (see Option C below).

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
4. Run **`./scripts/airgap-cli update-containers`** on that folder (see below).

If you only download the app artifact, you will **not** have Postgres or Redis — you need **both** artifacts (or a full local export).

### Option C — Generate locally (all four in one folder)

```bash
chmod +x scripts/export-container-images.sh
./scripts/export-container-images.sh
```

Optional:

**Important:** the script's output directory defaults to **`container-images/`** at the repo root, which is **gitignored**. To refresh the *committed* LFS bundle that air-gapped hosts pull, you must point `OUTPUT_DIR` at `output/container-images/`:

```bash
export IMAGE_PREFIX=ghcr.io/michaelsouder
export IMAGE_TAG=latest
export OUTPUT_DIR="$PWD/output/container-images"
./scripts/export-container-images.sh

git add output/container-images && git commit -m "deploy: refresh air-gap bundle" && git push
```

## Load on the air-gapped machine

Put all **four** `.tar` files in one directory, then:

```bash
chmod +x scripts/airgap-cli
./scripts/airgap-cli update-containers /path/to/that/directory
```

Then deploy with Podman/Docker per `docs/DEPLOY_PODMAN.md` and `docker-compose.prod.yml`.
