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
   **This only creates empty table structures — it loads no data.**
4. Checks whether the `users` table is empty. If it is, restarts the backend
   container so the initial-admin seed step (`app/startup_seed.py`, which
   only runs once at container startup) runs again — it already ran and
   silently failed the first time, before the tables existed.
5. Confirms a user now exists after the restart.

It's safe to re-run — `create_all()` only creates tables that don't already
exist and never touches existing data, and the seed step only creates an
admin user when the `users` table is empty.

## After running the script

Try logging in again.

- If the script reported an admin user was seeded (or that users already
  existed), login should work now with the credentials from
  `INITIAL_ADMIN_EMAIL` / `INITIAL_ADMIN_PASSWORD`.
- If it reported "Still no users after restart", `SEED_INITIAL_ADMIN` or
  `INITIAL_ADMIN_PASSWORD` likely weren't set when the backend container was
  created. Check:
  ```bash
  docker logs backend | grep -i seed
  ```
  Recreate the backend container with those variables set (see
  `docs/AIRGAP_DEPLOY.md` section 11), or register a user via
  `POST /api/v1/auth/register` and then promote it to admin directly in the
  database.
