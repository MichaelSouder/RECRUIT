# Fix: 500 on login, "relation \"users\" does not exist"

## Symptom

Logging in returns a 500 error. The backend logs show a Postgres error like:

```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedTable) relation "users" does not exist
```

This means the database has no tables at all (not just a schema mismatch).

## Root cause

Every deploy path (`docker-compose.yml`, `docker-compose.prod.yml`, the airgap
scripts, `docker-init-db.sh`/`.ps1`) initialized the database with:

```bash
python -c 'from app.database import Base, engine; Base.metadata.create_all(bind=engine)'
```

This imports `Base` from `app.database`, but never imports any of the model
modules (`app.models.user`, `app.models.study`, etc.). SQLAlchemy only
registers a model's table on `Base.metadata` when that model's module has
actually been imported somewhere in the process. Since nothing here imports
`app.models`, `Base.metadata` is empty and `create_all()` silently creates
**zero tables** — no error, because the command is also wrapped in
`2>&1 || true`.

Alembic's `alembic/env.py` already has the correct pattern
(`import app.models  # noqa: F401 — register models on Base.metadata`), but
that fix had never been applied to the other init commands.

## Fix applied to the repo

All affected files now import `app.models` before calling `create_all()`:

```bash
python -c 'import app.models; from app.database import Base, engine; Base.metadata.create_all(bind=engine)'
```

Fixed in: `docker-compose.yml`, `docker-compose.prod.yml`,
`scripts/airgap-stack-up.sh`, `scripts/start-stack-manual.sh`,
`scripts/docker-init-db.sh` / `.ps1`, `scripts/docker-setup.sh` / `.ps1`,
`container-images/airgap-stack-up.sh`, `container-images/AIRGAP_DEPLOY.md`,
`docs/AIRGAP_DEPLOY.md`, and the `output/container-images/` copies.

New deployments (or any deployment recreated with `--recreate-app` /
a fresh backend container) will create tables correctly from here on.

## Fixing an already-deployed server (no rebuild/redeploy needed)

If you already have a running stack hitting this bug, you don't need to
rebuild images or redeploy — just create the missing tables in the
existing backend container against the existing database.

On the server:

```bash
git pull
./scripts/fix-missing-tables.sh
```

The script:
1. Auto-detects `docker` or `podman` (override with `DOCKER_CMD=podman`).
2. Finds the running backend container (`backend` or `recruit_backend`; pass
   a name explicitly as the first argument if yours differs, e.g.
   `./scripts/fix-missing-tables.sh my_backend`).
3. Runs `create_all()` inside it, correctly importing `app.models` first.
4. Prints the resulting list of tables.

It's safe to re-run — `create_all()` only creates tables that don't already
exist and never touches existing data.

## After running the script

Try logging in again.

- If it now works, you're done.
- If it now fails with "Incorrect email or password" instead of a 500, the
  schema was the only problem, but no admin user exists yet (nothing to seed
  it if `SEED_INITIAL_ADMIN` wasn't set when the backend container was first
  created). Check:
  ```bash
  docker logs backend | grep -i seed
  ```
  and confirm `SEED_INITIAL_ADMIN=true`, `INITIAL_ADMIN_EMAIL`, and
  `INITIAL_ADMIN_PASSWORD` were set on that container. If not, recreate the
  backend container with those variables set (see `docs/AIRGAP_DEPLOY.md`
  section 11), or register a user via `POST /api/v1/auth/register` and then
  promote it to admin directly in the database.
