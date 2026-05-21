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

### Verify import on production (no legacy DB)

On the **source** DB before `pg_dump`, refresh the baseline (commit or ship with the dump):

```bash
cd src/backend
export DATABASE_URL='postgresql://…/recruit_db'
python -m migrations_cli migration-verify-baseline
# writes data/migration_verify_baseline.json
```

After **`pg_restore`** on prod, with only prod `DATABASE_URL`:

```bash
cd src/backend
export DATABASE_URL='postgresql://…/recruit_db'
python -m migrations_cli migration-verify
python -m migrations_cli deploy-check
```

Exit code **0** from `migration-verify` means counts and Alembic head match the baseline (`--tolerance N` if you allow small drift).

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
