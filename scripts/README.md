# scripts/

Operational tooling for RECRUIT: air-gapped deployment, container image
export, production data migration, and local Docker setup. Application
database-migration one-off scripts (`add_*.py`, `seed_mock_data.py`, etc.)
live under `src/backend/scripts/`, not here — this directory is entirely
deploy/ops tooling, independent of the app itself.

## Air-gapped deployment — `airgap-cli` + `airgap/`

The primary tool for running RECRUIT on a host with no registry/internet
access. Python 3.11+, **standard library only** — nothing to `pip install`,
on the air-gapped host or anywhere else.

```bash
./scripts/airgap-cli --help
```

| Subcommand | Does |
|---|---|
| `update-containers [bundle-dir]` | Load a bundle's images and recreate backend+frontend. Postgres/Redis and their data are never touched. |
| `stack-up [bundle-dir] [--recreate-app]` | Bring up (or reconcile) the full stack — Postgres, Redis, backend, frontend. Safe to re-run: containers that are already running are left alone; only missing or stopped/stale ones are (re)created. |
| `prune-images [bundle-dir]` | Remove old backend/frontend image tags after a successful update, keeping the running one plus `--keep` (default 1) most recent. Refuses to touch postgres/redis images. |
| `cron-update` | Unattended update for a host with a full git clone: fetch, fast-forward-only merge, `git lfs pull`, roll out only if `output/container-images/` changed, health-check, then prune (success) or leave old images in place with rollback instructions (failure). |
| `install-cron` | Idempotently installs the hourly `cron-update` job into crontab. |

Every subcommand takes `--dry-run` (genuinely side-effect-free — makes zero
mutating calls) and `--engine docker|podman` to force an engine instead of
auto-detecting. Full walkthrough: **`docs/AIRGAP_DEPLOY.md`**.

`scripts/airgap/` is a plain, uninstalled package (no `pyproject.toml` —
`airgap-cli` puts `scripts/` on `sys.path` itself). Layout:

| Module | Responsibility |
|---|---|
| `cli.py` | argparse entry point, dispatches to everything below |
| `engine.py` | docker/podman abstraction over subprocess |
| `stack.py` | Bring-up/reconcile logic for all four containers (the biggest module — this is where the "never touch a running Postgres" rule lives) |
| `bundle.py` | Loads image tars from a bundle; combines load + stack recreate for `update-containers` |
| `prune.py` | Old image tag cleanup |
| `autoupdate.py` | The `cron-update` orchestration: git operations, health-check retries, rollback-safe failure handling |
| `cron_install.py` | Crontab install |
| `manifest.py`, `envfile.py` | Parse `MANIFEST.txt` and `recruit-airgap.env` |
| `errors.py`, `logging_utils.py` | Structured exceptions with remediation hints; colored console logging with a `--debug` trace mode |

Tests: `scripts/airgap/tests/` (pytest — dev-only dependency, see
`requirements-dev.txt`; never required at runtime).

```bash
pip install -r scripts/airgap/requirements-dev.txt
python3 -m pytest scripts/airgap/tests
```

## Container images — export and pull

| Script | Use when |
|---|---|
| `export-container-images.sh` | On a connected machine with Docker/Podman: builds/pulls all four images (Postgres, Redis, backend, frontend), writes `.tar` files + `MANIFEST.txt` + a self-contained copy of `airgap-cli`/`airgap/` into `output/container-images/`. This is what produces the bundle `airgap-cli` consumes. |
| `pull-all-images.sh` | Simpler alternative when the target host *does* have network access to the registries — pulls all four images directly, no export/transfer step. |
| `recruit-airgap.env.example` | Template for `recruit-airgap.env` (secrets + config for `airgap-cli stack-up`). Copied into every exported bundle. |

CI: `.github/workflows/export-container-images.yml` runs
`export-container-images.sh` on-demand and uploads the bundle as two GitHub
Actions artifacts.

## Production data migration — `migration/`

Scripts for moving a production Postgres dump into a freshly deployed stack
and verifying it landed correctly. Full procedure: **`docs/PROD_CUTOVER_SNAPSHOT.md`**,
**`docs/MIGRATION_FINISH_CHECKLIST.md`**, **`data/backups/README.md`**.

| Script | Does |
|---|---|
| `_common.sh` | Shared shell helpers (paths, defaults) sourced by every other script in this folder — not run directly. |
| `create-cutover-dump.sh` | End-to-end on the source DB: `pg_dump` → split + gzip → checksum → refresh `migration_verify_baseline.json` → update `data/backups/README.md` → commit (not push). |
| `assemble-recruit-dump.sh` | Reassemble a split/gzipped dump back into one `.dump` file, with checksum verification. |
| `migration-verify-baseline.sh` | Snapshot row counts / checksums from a live DB into `data/migration_verify_baseline.json`, the baseline `migration-verify.sh` compares against. |
| `migration-verify.sh` | Post-restore verification against that baseline. Works against `DATABASE_URL` directly or via `docker`/`podman exec` (`CONTAINER_ENGINE=docker\|podman`). |
| `prod-restore-podman.sh` | Assemble + `pg_restore` a dump into a Postgres container, then run `migration-verify.sh`. The main entry point for "put production data into this deploy." |
| `ensure-admin.sh` | Re-create a known-good admin login after `prod-restore-podman.sh --clean` wipes out the seed admin along with the rest of the `users` table. |

## Local Docker dev setup

| Script | Platform | Does |
|---|---|---|
| `docker-setup.sh` / `docker-setup.ps1` | macOS/Linux / Windows | Interactive helper for building/starting/stopping the standard `docker-compose` dev stack. See `DOCKER_SETUP_SUMMARY.md`. |
| `docker-init-db.sh` / `docker-init-db.ps1` | macOS/Linux / Windows | Initializes tables and optionally seeds data inside the compose stack. |
| `dev-host-with-snapshot-db.sh` | macOS/Linux | Runs the backend on the host (not containerized) against the migrated snapshot Postgres container, for faster local iteration. See root `README.md`. |
| `restore-postgres-from-data-parts.sh` | macOS/Linux | One-time: reassembles `data/postgres.zip.part*`, extracts the embedded Postgres 13 cluster, fixes ownership for the official `postgres` image. Feeds `docker-compose.postgres-snapshot.yml`. |

## Diagnostics and one-off fixes

| Script | Use when |
|---|---|
| `list-postgres-databases.sh` | You're not sure which of this repo's several local Postgres instances (or which database within one) you're actually pointed at. See `docs/LIST_POSTGRES_DATABASES.md`. |
| `fix-missing-tables.sh` | A running backend is missing tables (`relation "users" does not exist`) because it was started before a since-fixed model-import bug — creates the missing tables without a rebuild/redeploy. See `docs/FIX_MISSING_TABLES.md`. |
| `start-stack-manual.sh` | `airgap-cli stack-up` fails with "invalid reference format" on a given Podman setup — runs each `podman run` directly so you can see exactly which one fails. |
| `db_snapshot_pdf.py` | Generate a PDF snapshot of a database's public tables (schema + row counts), e.g. for a point-in-time record. `--preset recruit\|arc\|dvbic-research\|all-legacy`. Requires `psycopg2-binary` and `fpdf2` (`pip install` — this one script, unlike the air-gap tooling, isn't meant to run on a host with no network). |

---

Superseded bash implementations of the air-gap tooling above (`airgap-stack-up.sh`,
`load-container-images.sh`, `update-containers.sh`, `prune-old-images.sh`,
`airgap-cron-update.sh`, `install-airgap-cron.sh`) have been removed now that
`airgap-cli` replaces them; `git log -- scripts/archive/` has the history if
you ever need to see the old versions.
