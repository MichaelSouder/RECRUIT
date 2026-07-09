# Production cutover — snapshot `recruit_db` (operator checklist)

Use this when promoting the **migrated** database from local snapshot Postgres (`127.0.0.1:15432/recruit_db` or your restore) to **production** RECRUIT Postgres **today**.

## A. Finish ETL on the snapshot (before `pg_dump`)

From `src/backend/` with legacy URLs pointing at the **same** snapshot host:

```bash
export DATABASE_URL='postgresql://postgres:postgres@127.0.0.1:15432/recruit_db'
export LEGACY_ARC_DATABASE_URL='postgresql://postgres:postgres@127.0.0.1:15432/arc'
export LEGACY_DVBIC_RESEARCH_DATABASE_URL='postgresql://postgres:postgres@127.0.0.1:15432/dvbic_research'
export MIGRATION_BATCH_ID='YYYY-MM-DD-prod-cutover'

python -m migrations_cli preflight
python -m migrations_cli validate
python -m migrations_cli deploy-check

# If not already at head:
alembic upgrade head

# Idempotent spine (safe to re-run); see MIGRATION_PROGRESS_AND_STRUCTURE.md §3
python -m migrations_cli import-dvbic-subjects2    # ~51k historical DVbic subjects
python -m migrations_cli import-dvbic-subject-study
python -m migrations_cli import-dvbic-session-notes
python -m migrations_cli import-arc-study-acl-users   # stub users for study_acl.usr
python -m migrations_cli import-arc-user-study
python -m migrations_cli migration-completeness
```

**Gates before dump:**

```bash
python -m migrations_cli deploy-check   # duplicate arc proc estimate should be 0
python -m migrations_cli record-migration-audit "Snapshot ready for prod pg_dump."
```

## B. Logical dump of `recruit_db` only

Dump **RECRUIT** (`recruit_db`), not the whole snapshot cluster (arc / dvbic stay read-only legacy elsewhere):

```bash
pg_dump "$DATABASE_URL" --format=custom --no-owner --no-acl \
  --file="recruit_prod_cutover_$(date -u +%Y%m%dT%H%MZ).dump"
```

Verify restore on a scratch DB before touching production.

## C. Restore on production Postgres

```bash
# create empty recruit_db, then:
pg_restore --dbname="$PROD_DATABASE_URL" --no-owner --no-acl --verbose recruit_prod_cutover_*.dump
```

On the **app host** (or migration job), confirm schema:

```bash
export DATABASE_URL="$PROD_DATABASE_URL"
cd src/backend && alembic current   # should show head d1e4f9a02b11 (or newer)
python -m migrations_cli validate
python -m migrations_cli deploy-check
```

### Verify import on production (bash; no legacy DB, no Python)

**Podman one-shot** (assemble parts → copy into container → `pg_restore` → verify):

Defaults already match this checklist (`PODMAN_CONTAINER=postgres`,
`PGDATABASE=recruit_db`, `PGPASSWORD=postgres`), and the scripts are tracked
executable in git, so after `git pull` this is the whole command:

```bash
./scripts/migration/prod-restore-podman.sh
```

Only export `PODMAN_CONTAINER` / `PGDATABASE` / `PGPASSWORD` if your target
differs from the above (check the actual name with `podman ps`). `pg_restore`
now runs with `--clean --if-exists`, so it's safe to run even if the target
already has an empty schema or a seeded admin user from a fresh deploy.

**Step by step:**

```bash
./scripts/migration/assemble-recruit-dump.sh
./scripts/migration/prod-restore-podman.sh --container postgres
./scripts/migration/migration-verify.sh --tolerance 0
```

Refresh baseline on the source DB before a new dump:

```bash
export DATABASE_URL='postgresql://…/recruit_db'
./scripts/migration/migration-verify-baseline.sh
```

Exit code **0** from `migration-verify.sh` means counts and Alembic head match `data/migration_verify_baseline.json`.

Optional: `python -m migrations_cli migration-verify` still works if Python deps are installed.

Point the **RECRUIT application** `DATABASE_URL` at this instance. Legacy URLs are **not** required at runtime unless you run further ETL on prod.

## D. Known limits after cutover (document for product)

| Item | Status |
|------|--------|
| Arc clinical spine (`subj_list`, `proc_list`, instrument specs, `studyproc_list`) | Migrated on snapshot |
| DVbic `subjects` + **`subjects2`** + session notes tied to those ids | Run `import-dvbic-subjects2` + session-notes before dump |
| Arc `study_acl` → `user_study` | Migrated via stub users (`import-arc-study-acl-users` + `import-arc-user-study`) |
| DVbic instrument auto-pass | Many rows remain orphans (`migration_events`); re-run does not duplicate **mapped** assessments |
| 28 DVbic + 8 Arc “gap” tables | No ETL yet (reference / raw tables without subject key) |
| Arc ↔ DVbic same person | **No** automatic merge (separate `subjects` rows by design) |

## E. Post-go-live passwords

Imported Arc users use a placeholder bcrypt hash. Set real passwords before users log in:

```bash
export RECRUIT_NEW_PASSWORD='…'
python -m migrations_cli set-user-password --email kolim@umn.edu
```

See Alembic migration `b3e8a1c92d40` for the migration system account.
