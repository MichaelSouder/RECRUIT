# Deploying RECRUIT with Podman (no Compose)

This guide runs the **production** stack using plain **`podman run`** commands—no `podman-compose` or `docker compose`.

Published images from GitHub Actions are built for the app path **`/recruit`**: the UI is at **`http://your-host:18080/recruit/`**, and the browser calls the API at the same origin under **`/recruit/api/`** (proxied by the frontend container to the backend). You normally **do not** set `VITE_API_URL` on the published image.

## What gets started

| Container name (DNS) | Image | Host ports | Purpose |
|---------------------|-------|------------|---------|
| `postgres` | `postgres:15` | `15432` → 5432 | Database |
| `redis` | `redis:7-alpine` | `16379` → 6379 | Cache |
| `backend` | `ghcr.io/…/recruit-backend` | `18000` → 8000 | API |
| `frontend` | `ghcr.io/…/recruit-frontend` | `18080` → 80 | nginx + static UI |

All four containers attach to the **same Podman network** so names like `postgres` and `backend` resolve.

## 1. Install Podman

```bash
# Fedora / RHEL
sudo dnf install -y podman

# Debian / Ubuntu
sudo apt update && sudo apt install -y podman
```

## 2. Log in to GitHub Container Registry (if packages are private)

```bash
echo YOUR_GITHUB_TOKEN | podman login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

Use a token with the **`read:packages`** scope. Skip this step if your images are public.

## 3. Network and volume

Pick a lowercase GHCR owner (your GitHub username or org), e.g. `ghcr.io/michaelsouder`.

```bash
export IMAGE_PREFIX=ghcr.io/michaelsouder   # change to your namespace
export TAG=latest

podman network exists recruit_network || podman network create recruit_network
podman volume create recruit_postgres_data
```

(On Podman versions without `network exists`, run `podman network create recruit_network` once; if the network already exists, the command will fail—use the existing network or choose another name.)

## 4. Pull application images

If you **cannot pull from GHCR** (air-gapped host), load images from the offline bundle first: see **`output/README.md`** and run `./scripts/load-container-images.sh` on the `.tar` files (from a local export or the GitHub Actions artifact **Export container images**).

Otherwise:

```bash
podman pull ${IMAGE_PREFIX}/recruit-backend:${TAG}
podman pull ${IMAGE_PREFIX}/recruit-frontend:${TAG}
podman pull docker.io/library/postgres:15
podman pull docker.io/library/redis:7-alpine
```

## 5. Start Postgres

Container name **`postgres`** must match `DATABASE_URL` (`...@postgres:5432/...`).

```bash
podman run -d \
  --name postgres \
  --network recruit_network \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=recruit_db \
  -p 15432:5432 \
  -v recruit_postgres_data:/var/lib/postgresql/data \
  --restart unless-stopped \
  docker.io/library/postgres:15
```

Wait until Postgres accepts connections:

```bash
until podman exec postgres pg_isready -U postgres; do sleep 1; done
```

## 6. Start Redis

```bash
podman run -d \
  --name redis \
  --network recruit_network \
  -p 16379:6379 \
  --restart unless-stopped \
  docker.io/library/redis:7-alpine
```

## 7. Secrets and environment

Set a strong JWT secret and (for **first boot** with an empty database) an initial admin password. The backend creates **`admin@example.com`** only when **`SEED_INITIAL_ADMIN=true`**, **`INITIAL_ADMIN_PASSWORD`** is non-empty, and there are **no users** yet.

```bash
export SECRET_KEY='replace-with-a-long-random-string'
export INITIAL_ADMIN_PASSWORD='replace-with-a-strong-password'
```

## 8. Start the backend

Container name **`backend`** must match nginx `proxy_pass http://backend:8000` in the frontend image.

The command below matches the startup logic from `docker-compose.prod.yml`: wait for Postgres, create tables, run the small migration script, then **uvicorn**.

```bash
podman run -d \
  --name backend \
  --network recruit_network \
  -e DATABASE_URL=postgresql://postgres:postgres@postgres:5432/recruit_db \
  -e REDIS_URL=redis://redis:6379/0 \
  -e SECRET_KEY="${SECRET_KEY}" \
  -e ALGORITHM=HS256 \
  -e ACCESS_TOKEN_EXPIRE_MINUTES=30 \
  -e 'CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:80,http://localhost:18080,http://frontend:80' \
  -e ENVIRONMENT=production \
  -e DEBUG=false \
  -e SEED_INITIAL_ADMIN=true \
  -e INITIAL_ADMIN_EMAIL=admin@example.com \
  -e INITIAL_ADMIN_PASSWORD="${INITIAL_ADMIN_PASSWORD}" \
  -p 18000:8000 \
  --restart unless-stopped \
  --health-cmd "python -c \"import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')\"" \
  --health-interval 30s \
  --health-timeout 10s \
  --health-retries 3 \
  --health-start-period 40s \
  ${IMAGE_PREFIX}/recruit-backend:${TAG} \
  sh -c "
    echo 'Waiting for PostgreSQL...' &&
    until pg_isready -h postgres -U postgres; do sleep 1; done &&
    echo 'PostgreSQL is ready!' &&
    echo 'Initializing database...' &&
    python -c 'from app.database import Base, engine; Base.metadata.create_all(bind=engine)' 2>&1 || true &&
    python scripts/add_assessment_time_to_assessments.py 2>&1 || echo 'Migration may have already run' &&
    echo 'Database initialized!' &&
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
  "
```

**CORS:** For a real hostname, add your site origin (scheme + host + port, **no path**), e.g. `https://recruit.example.com`, to `CORS_ORIGINS` as a comma-separated list. Replace the default `-e CORS_ORIGINS=...` line in the backend `podman run` above with something like:

`-e 'CORS_ORIGINS=https://recruit.example.com,https://recruit.example.com:18080'`

(Include every origin browsers use to load the SPA; omit path segments like `/recruit`.)

**Postgres password:** The example uses the default `postgres` password. For production, change the Postgres container env vars and `DATABASE_URL` to match.

## 9. Start the frontend

Container name **`frontend`** is optional for DNS; nginx talks to **`backend`** by name.

```bash
podman run -d \
  --name frontend \
  --network recruit_network \
  -p 18080:80 \
  --restart unless-stopped \
  --health-cmd "wget -q -O- http://127.0.0.1/recruit/health || exit 1" \
  --health-interval 30s \
  --health-timeout 3s \
  --health-retries 3 \
  --health-start-period 5s \
  ${IMAGE_PREFIX}/recruit-frontend:${TAG}
```

Open the app: **`http://YOUR_SERVER_IP:18080/recruit/`** (trailing slash recommended).

Health: `http://YOUR_SERVER_IP:18080/recruit/health`  
API (direct): `http://YOUR_SERVER_IP:18000/docs` (OpenAPI)

## 10. Firewall

```bash
# firewalld example
sudo firewall-cmd --permanent --add-port=18080/tcp
sudo firewall-cmd --permanent --add-port=18000/tcp   # only if you expose the API
sudo firewall-cmd --reload
```

Prefer terminating **HTTPS** on a reverse proxy and only exposing **443** to the internet.

## 11. Reverse proxy in front of Podman (optional)

If another nginx or Apache terminates TLS for `https://example.com` and you forward to this host:

- Proxy **`/recruit/`** to `http://127.0.0.1:18080/recruit/` (preserve path and `Host` header).
- You usually **do not** need to expose **18000** publicly if all API traffic goes through the frontend container at **`/recruit/api/`**.

## 12. Updates

```bash
podman pull ${IMAGE_PREFIX}/recruit-backend:${TAG}
podman pull ${IMAGE_PREFIX}/recruit-frontend:${TAG}
podman stop backend frontend
podman rm backend frontend
# Re-run the podman run commands for backend and frontend (same env as before).
```

Postgres data persists in the volume `recruit_postgres_data`.

## 13. Pinning an image by Git SHA

CI also tags each image with the **git commit SHA** (see the workflow run or GHCR package tags). Example:

```bash
export TAG=<sha-tag-from-ci>
podman pull ${IMAGE_PREFIX}/recruit-backend:${TAG}
# use ${TAG} in podman run instead of latest
```

## 14. Troubleshooting

| Symptom | What to check |
|--------|----------------|
| `pull` 401/403 | `podman login ghcr.io`; image name and lowercase owner. |
| Blank page or 404 at `/` | App is under **`/recruit/`**, not site root. |
| API errors / CORS | `CORS_ORIGINS` includes your browser origin; API via **`/recruit/api/`** on same host. |
| `backend` exits | `podman logs backend`; Postgres reachable (`postgres` name on `recruit_network`). |
| Login loop | Cookies path / token storage; try hard refresh. |

## 15. Local development vs production image

- **`docker-compose.yml`** (dev) builds the frontend with **`VITE_BASE_PATH=/`** and the API URL **`http://localhost:18000`**.
- **GHCR images** are built with **`VITE_BASE_PATH=/recruit/`** and same-origin API (no `VITE_API_URL`), matching this guide.

---

*Stack matches `docker-compose.prod.yml` behavior; adapt names, ports, and secrets for your environment.*
