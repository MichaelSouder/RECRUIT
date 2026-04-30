# Air-gapped deployment (RECRUIT)

This guide is for hosts that **cannot** use Docker Compose, **cannot** pull from container registries, and **cannot** clone Git. You run containers with plain **`docker run`** or **`podman run`**.

**Two layouts:**

| Layout | Postgres | Containers |
|--------|----------|------------|
| **Bundled DB** (default in older steps below) | Postgres **in** a container | Postgres, Redis, backend, frontend (**four**) |
| **Host DB** (typical on RHEL with system PostgreSQL) | Postgres on the **host** | Redis, backend, frontend (**three**) — set **`USE_HOST_POSTGRES=true`** in **`recruit-airgap.env`** and use **`airgap-stack-up.sh`** (see §5c) |

**Production URL layout:** the UI is at **`http://your-host:18080/recruit/`**. The browser talks to the API on the **same origin** under **`/recruit/api/`** (nginx in the frontend container proxies to the backend). You do **not** set `VITE_API_URL` on the shipped frontend image.

## 1. What you must have on the air-gapped host

| File (same directory) | Loaded image |
|----------------------|--------------|
| `postgres-15.tar` | `postgres:15` |
| `redis-7-alpine.tar` | `redis:7-alpine` |
| `recruit-backend.tar` | See **`MANIFEST.txt`** (e.g. `ghcr.io/yourorg/recruit-backend:TAG`) |
| `recruit-frontend.tar` | See **`MANIFEST.txt`** |

Optional helpers in the same folder (if produced by export): **`load-container-images.sh`**, **`airgap-stack-up.sh`** (starts the stack after images are loaded), **`recruit-airgap.env.example`** (copy to **`recruit-airgap.env`** and edit), this file as **`AIRGAP_DEPLOY.md`**.

**Image tars:** For the **bundled** Postgres layout, **all four** `.tar` files are required. For **host Postgres**, you only need **Redis + backend + frontend** tars (you can still load the Postgres tar; it is unused). If you used GitHub Actions, merge **both** artifacts into one folder for a full bundle, or download only what you need plus **`MANIFEST.txt`** and helper scripts.

## 2. How to obtain this bundle (connected machine)

**Option A — Local export (recommended for a controlled tag)**

From a machine with Docker or Podman and network access (repo root):

```bash
export IMAGE_PREFIX=ghcr.io/yourgithubuser   # lowercase; must match MANIFEST after export
export IMAGE_TAG=latest                      # or a release tag, e.g. v1.2.3
chmod +x scripts/export-container-images.sh
./scripts/export-container-images.sh
```

Default output directory: **`output/container-images/`** (override with `OUTPUT_DIR=...`).

**Option B — GitHub Actions**

1. In the repository: **Actions** → **Export container images** → **Run workflow**.
2. When the run finishes, download **both** artifacts and unzip them into **one** folder so all four `.tar` files sit together.

## 3. Transfer to the secure host

Copy the **entire** folder (four `.tar` files plus `MANIFEST.txt` and any bundled `.md` / `.sh` files). Example:

```bash
scp -r output/container-images/ user@secure-host:/opt/recruit-bundle/
```

Use whatever approved transfer your security team allows (encrypted media, etc.).

## 4. Install engine on the air-gapped host

Install **Docker** or **Podman** only. You do **not** need Compose, BuildKit, or registry login on this host.

The commands below use **`docker`**. If you use Podman, replace `docker` with `podman` everywhere. For Podman on RHEL/Fedora, you may use fully qualified image names (e.g. `docker.io/library/postgres:15`) in `run` commands if your policy requires it—the loaded tags from **`MANIFEST.txt`** remain the source of truth for the app images.

## 5. Load images

On the air-gapped host, `cd` to the directory that contains the four `.tar` files.

**Using the bundled script (if present):**

```bash
chmod +x ./load-container-images.sh
./load-container-images.sh .
```

**Or load manually:**

```bash
for f in postgres-15.tar redis-7-alpine.tar recruit-backend.tar recruit-frontend.tar; do
  docker load -i "$f"
done
```

Confirm the image names match **`MANIFEST.txt`**.

### 5b. Start the stack with the helper script (optional)

After **`load-container-images.sh`**, you can bring up Postgres, Redis, backend, and frontend in one step (same behavior as sections 6–13 below).

**Recommended:** put settings in **`recruit-airgap.env`** next to **`MANIFEST.txt`** (copy from **`recruit-airgap.env.example`** and edit). The script loads that file automatically. Variables you already **`export`** in the shell override the file.

```bash
cp recruit-airgap.env.example recruit-airgap.env
# Edit recruit-airgap.env (SECRET_KEY, INITIAL_ADMIN_PASSWORD, CORS_ORIGINS, etc.)

chmod +x ./airgap-stack-up.sh
./airgap-stack-up.sh .
```

Alternatively you can keep using plain environment variables instead of a file:

```bash
export SECRET_KEY='your-long-random-secret'
export INITIAL_ADMIN_PASSWORD='your-first-admin-password'
export CORS_ORIGINS='http://your-server:18080'   # comma-separated: scheme + host + port, no path
./airgap-stack-up.sh .
```

Use **`./airgap-stack-up.sh --help`** for **`--env-file`**, ports, image overrides (`POSTGRES_IMAGE` if Podman shows `docker.io/library/postgres:15`), **`--dry-run`**, and **`--recreate-app`** (removes only **backend** and **frontend** containers, then recreates them).

### 5c. Host PostgreSQL (three containers)

Use this when PostgreSQL already runs on the machine (not in Docker/Podman). The script starts **Redis**, **backend**, and **frontend** only.

1. Ensure PostgreSQL accepts **TCP** connections from the host and from containers (`listen_addresses`, `pg_hba.conf`). Create the app database and user if needed.
2. Copy **`recruit-airgap.env.example`** → **`recruit-airgap.env`** and set at least:
   - **`USE_HOST_POSTGRES=true`**
   - **`DATABASE_URL`** — must use a hostname the **backend container** can resolve (same as **`POSTGRES_SERVICE_HOST`**). Examples:
     - **Podman:** `postgresql://USER:PASSWORD@host.containers.internal:5432/DBNAME`
     - **Docker Desktop:** use **`host.docker.internal`** in both **`DATABASE_URL`** and **`POSTGRES_SERVICE_HOST`**
     - **Docker on Linux:** `host.docker.internal` is supported if you use **`airgap-stack-up.sh`** (it adds **`--add-host=host.docker.internal:host-gateway`** for the backend), or put the host’s bridge IP in **`DATABASE_URL`**
   - **`POSTGRES_SERVICE_HOST`** — same host part as in **`DATABASE_URL`**
   - **`SECRET_KEY`**, **`INITIAL_ADMIN_PASSWORD`**, **`CORS_ORIGINS`**
3. **`POSTGRES_WAIT_HOST`** / **`POSTGRES_WAIT_PORT`** — where the **script** checks readiness from the host (defaults **`127.0.0.1`** and **`5432`**). If your server listens only on another address, set these to match.

**Why the old flow “stuck waiting for Postgres”:** the helper used **`docker exec postgres pg_isready`**, which only works when a **`postgres`** container exists and is healthy. With host PostgreSQL there is no such container — use **`USE_HOST_POSTGRES=true`** so the script waits on the host socket instead.

## 6. Set image variables

Read **`MANIFEST.txt`** and export the same prefix and tag the bundle was built with:

```bash
export IMAGE_PREFIX=ghcr.io/yourgithubuser   # must match MANIFEST.txt
export TAG=latest                            # must match MANIFEST.txt
```

## 7. Network and volume (once per host)

```bash
docker network inspect recruit_network >/dev/null 2>&1 || docker network create recruit_network
docker volume create recruit_postgres_data 2>/dev/null || true
```

If `docker volume create` reports the volume already exists, that is fine.

## 8. Start Postgres

Container name **`postgres`** must match `DATABASE_URL` (`...@postgres:5432/...`).

```bash
docker run -d \
  --name postgres \
  --network recruit_network \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=recruit_db \
  -p 15432:5432 \
  -v recruit_postgres_data:/var/lib/postgresql/data \
  --restart unless-stopped \
  postgres:15
```

Wait until Postgres accepts connections:

```bash
until docker exec postgres pg_isready -U postgres; do sleep 1; done
```

For production, change **`POSTGRES_PASSWORD`** and **`DATABASE_URL`** in the backend step to match.

## 9. Start Redis

```bash
docker run -d \
  --name redis \
  --network recruit_network \
  -p 16379:6379 \
  --restart unless-stopped \
  redis:7-alpine
```

## 10. Secrets (before backend)

```bash
export SECRET_KEY='use-a-long-random-string'
export INITIAL_ADMIN_PASSWORD='strong-password-for-first-boot-only'
```

On **first boot** with an **empty** database, the backend can create **`admin@example.com`** when **`SEED_INITIAL_ADMIN=true`**, **`INITIAL_ADMIN_PASSWORD`** is non-empty, and there are no users yet. After the first admin exists, you can rotate env vars and redeploy without relying on `INITIAL_ADMIN_PASSWORD`.

## 11. Start backend

Container name **`backend`** must match nginx `proxy_pass http://backend:8000` inside the frontend image.

Replace **`CORS_ORIGINS`** with every browser origin you use (scheme + host + port, **no path**), comma-separated. Example for HTTPS:

`-e 'CORS_ORIGINS=https://recruit.example.com'`

```bash
docker run -d \
  --name backend \
  --network recruit_network \
  -e DATABASE_URL=postgresql://postgres:postgres@postgres:5432/recruit_db \
  -e PGHOST=postgres \
  -e PGPORT=5432 \
  -e REDIS_URL=redis://redis:6379/0 \
  -e SECRET_KEY="${SECRET_KEY}" \
  -e ALGORITHM=HS256 \
  -e ACCESS_TOKEN_EXPIRE_MINUTES=30 \
  -e 'CORS_ORIGINS=https://your-frontend-origin.example.com' \
  -e ENVIRONMENT=production \
  -e DEBUG=false \
  -e SEED_INITIAL_ADMIN=true \
  -e INITIAL_ADMIN_EMAIL=admin@example.com \
  -e INITIAL_ADMIN_PASSWORD="${INITIAL_ADMIN_PASSWORD}" \
  -p 18000:8000 \
  --restart unless-stopped \
  "${IMAGE_PREFIX}/recruit-backend:${TAG}" \
  sh -c "
    echo 'Waiting for PostgreSQL...' &&
    until pg_isready -h \"\${PGHOST:-postgres}\" -p \"\${PGPORT:-5432}\" -U postgres; do sleep 1; done &&
    echo 'PostgreSQL is ready!' &&
    echo 'Initializing database...' &&
    python -c 'from app.database import Base, engine; Base.metadata.create_all(bind=engine)' 2>&1 || true &&
    python scripts/add_assessment_time_to_assessments.py 2>&1 || echo 'Migration may have already run' &&
    echo 'Database initialized!' &&
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
  "
```

## 12. Start frontend

```bash
docker run -d \
  --name frontend \
  --network recruit_network \
  -p 18080:80 \
  --restart unless-stopped \
  "${IMAGE_PREFIX}/recruit-frontend:${TAG}"
```

## 13. Verification

```bash
docker exec postgres pg_isready -U postgres
docker ps
curl -sf "http://127.0.0.1:18000/health"
curl -sf "http://127.0.0.1:18080/recruit/health"
```

Open in a browser: **`http://YOUR_SERVER:18080/recruit/`** (trailing slash recommended).

## 14. Firewall and TLS

- Open **18080/tcp** for the UI (or only **443** if a reverse proxy fronts the app).
- Expose **18000** only if clients must hit the API directly; otherwise prefer **`/recruit/api/`** through the frontend.

## 15. Updates (still air-gapped)

1. On a connected machine, run **`scripts/export-container-images.sh`** again (or download new CI artifacts) with the new **`IMAGE_TAG`**.
2. Transfer the new `.tar` files.
3. On the server: **`docker load -i`** for each changed archive.
4. **`docker stop`** / **`docker rm`** **`backend`** and **`frontend`** (and Postgres/Redis only if you intentionally upgrade those images—Postgres data stays in the volume).
5. Re-run the **`docker run`** commands from this guide with the same **`IMAGE_PREFIX`** and new **`TAG`**.

## 16. Troubleshooting

| Symptom | What to check |
|--------|----------------|
| `docker load` fails | All four `.tar` files present; enough disk space. |
| Blank page at `/` | App lives under **`/recruit/`**. |
| API or CORS errors | **`CORS_ORIGINS`** includes the exact browser origin; use API via **`/recruit/api/`** on the same host as the UI when possible. |
| Backend exits | **`docker logs backend`**; DB reachable (container mode: hostname **`postgres`**; host mode: **`DATABASE_URL`** / **`POSTGRES_SERVICE_HOST`**). |
| **`airgap-stack-up.sh` stuck on Postgres** | With **host** Postgres, set **`USE_HOST_POSTGRES=true`** and **`POSTGRES_WAIT_*`** so the script does not **`exec`** a missing **`postgres`** container. With **bundled** Postgres, check **`docker logs postgres`**. |
| Missing images after **`docker load`** | Load and run with the **same** engine (**`DOCKER_CMD=podman`** or **`docker`**). **`airgap-stack-up.sh`** picks the engine that already has the backend image when both are installed. |
| Name already in use | Remove old container: **`docker rm -f postgres`** (only if you intend to recreate)—**warning:** recreating Postgres without the volume loses DB data unless you know what you are doing. |

## 17. Related documentation

- **`docs/DEPLOY_PODMAN.md`** — same stack with more Podman-centric notes and optional reverse-proxy detail.
- **`output/README.md`** — short pointer for offline image layout and CI artifacts.

---

*Stack behavior matches **`docker-compose.prod.yml`** (production paths and admin seeding). Adapt ports, passwords, and origins for your environment.*
