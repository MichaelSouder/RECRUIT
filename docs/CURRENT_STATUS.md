# Where we are now (RECRUIT + legacy data migration)

**Last updated:** 2026-05-07  
**Audience:** anyone picking up the project after a break or onboarding onto migration work.

This note reflects **work done in-repo through the legacy Postgres snapshot path** (`arc`, `dvbic_*`). Older docs that talk only about **`old/` Rails** and `plans/04-migration-strategy.md` are a **different lineage**—see [MIGRATION_STATUS.md](./MIGRATION_STATUS.md) for that audit; this file is the **current** picture.

---

## 1. Application (RECRUIT)

| Area | State |
|------|--------|
| **Backend** | FastAPI + SQLAlchemy models under `src/backend/app/models/` (core domain + **`LegacyIdMap`** / **`MigrationEvent`** for ETL traceability). |
| **Schema migrations (RECRUIT DB)** | **Alembic:** `570711e1fdf8` (initial) → **`b3e8a1c92d40`** (`legacy_id_map`, `migration_events`, **migration system user**). |
| **Default DB URL (host dev)** | `src/backend/app/config.py` → **`postgresql://postgres:postgres@localhost:15432/recruit_db`** (legacy snapshot on host **15432** — migrated `recruit_db`). |
| **Docker Compose `backend` default** | **`postgresql://postgres:postgres@postgres:5432/recruit_db`** — the **Compose `postgres` service** (own volume on host **25432**), **not** the snapshot. Empty or schema-only until you seed or migrate there. For migrated data in Docker, use **`docker-compose.use-host-snapshot-db.yml`** (see that file). |
| **Host dev (see real migrated rows)** | From repo root: **`./scripts/dev-host-with-snapshot-db.sh`** (API on **127.0.0.1:8000** by default). Second shell: **`cd src/frontend && VITE_DEV_SERVER_PORT=5174 npm run dev`**, open **http://127.0.0.1:5174/** — leave **`VITE_API_URL` unset** so Vite proxies `/api` to the host API. Step-by-step in [README.md](../README.md) (*Local UI against the migrated snapshot DB*). |
| **Migration CLI** | **`migrations_cli`**: imports, **`deploy-check`**, **`prune-duplicate-arc-proc-assessments`**, **`record-migration-audit`**. Operator flow: [MIGRATION_DEPLOY_RUNBOOK.md](./MIGRATION_DEPLOY_RUNBOOK.md). |
| **Legacy → RECRUIT ETL** | **Arc:** users, studies, subjects, `subject_study`, **`user_study`** (from `study_acl` when usernames match `auth_user`), assessments + types + instruments + maps. **DVbic:** studies, subjects, **`subject_study`** (inferred from legacy `(subject_id, study_id)` pairs), **`session_notes`**, instruments + maps. **Not yet:** cross-system subject merge (needs crosswalk / allowlisted key), `audit_logs` from ETL, optional tighter visit links in `data`. |

### Migration system user (RECRUIT DB)

Alembic **`b3e8a1c92d40`** inserts **`migration-system@recruit.internal`** if missing (for `audit_logs.user_id` during ETL). **Placeholder password** is documented in that revision file (`MigrationSystem!DoNotUse0`) — **rotate or disable logins** before any shared environment; prefer non-interactive ETL using this account only as attribution.

**Local UI login:** Use that email and password to sign in against a DB that has run revision `b3e8a1c92d40`. Rows created by **`import-arc-auth-users`** share a bcrypt placeholder whose **plaintext was never stored in-repo**; if you need a known password for an imported address, set one locally (example):

`RECRUIT_NEW_PASSWORD='choose-a-strong-password' python -m migrations_cli set-user-password --email your.name@example.org`

(from `src/backend` with `DATABASE_URL` pointing at your RECRUIT database).

---

## 2. Local legacy PostgreSQL (from zip parts)

| Artifact | Purpose |
|----------|---------|
| `data/postgres.zip.part00` … `part09` | Split zip of a **full PG 13 data directory** (RHEL-style `var/lib/pgsql/data`). |
| `scripts/restore-postgres-from-data-parts.sh` | Concatenates parts, extracts cluster to `data/.postgres-restore/pgdata`, fixes ownership for the official `postgres` image. |
| `docker-compose.postgres-snapshot.yml` | Runs **`postgres:13`** as `recruit_postgres_snapshot` on **`localhost:15432`** (compose project name isolated from main `docker-compose.yml`). |

**Important:** That cluster is **not** the small empty `recruit_db` only—it contains **many legacy databases** (`arc`, `dvbic_research`, …). A dedicated **`recruit_db`** was **created on the snapshot** for RECRUIT dev; Alembic is applied there for local work.

---

## 3. Migration planning & discovery (current track)

| Document | What it is |
|----------|------------|
| [LEGACY_DATA_MIGRATION_PLAN.md](./LEGACY_DATA_MIGRATION_PLAN.md) | End-to-end **strategy**: phases, `legacy_id_map`, merge policy (**Option A**: no fuzzy auto-merge; strict key **TBD**), **`audit_logs`** for migration notes, **production-grade CLI** expectations, runbook outline. |
| [LEGACY_DATA_MIGRATION_PHASE_A_DISCOVERY.md](./LEGACY_DATA_MIGRATION_PHASE_A_DISCOVERY.md) | **Phase A done** on the **local snapshot** for **`arc`** + **`dvbic_research`**: PKs/FKs, row counts, table classification, column → RECRUIT mappings (draft), merge-key analysis (**no safe exact arc↔dvbic key** without further work/crosswalk), DVbic **`studies`** table found (19 rows). |
| [MIGRATION_DEPLOY_RUNBOOK.md](./MIGRATION_DEPLOY_RUNBOOK.md) | **Production / staging operator steps:** backup, `deploy-check`, import order, optional duplicate arc-proc prune, `record-migration-audit`. |

**Phase A on production:** still required—re-run discovery counts and merge-key stats on the **real server backup** before trusting numbers.

---

## 4. Decisions already captured in the plan

- Single subject when **identity is confirmed**; otherwise **separate rows** until explicit merge.
- **No silent fuzzy merge** on bulk import; **audit** merges and judgment calls (`audit_logs` + JSON context).
- Conflicting field values: resolve **as you go**, each choice logged.
- **Strict auto-merge key** between `arc` and DVbic: **TBD**; until defined, treat allowlist as **empty**.
- Production execution: **versioned CLI**, env config, dry-run, idempotency, pre-flight, **`pg_dump` rollback** story—not hand-run SQL.

---

## 5. What is **not** done yet (next engineering)

1. **Richer `audit_logs`** (field-level) when merging or resolving conflicts beyond milestone rows from `record-migration-audit`.
2. **Cross-system subject merge** (arc↔DVbic): crosswalk file or allowlisted key only — not bulk-fuzzy merge.
3. **Linking** instrument `assessments` to parent **`proc_list`** rows where useful (`data` metadata).
4. **Operator runbook:** [MIGRATION_DEPLOY_RUNBOOK.md](./MIGRATION_DEPLOY_RUNBOOK.md) (backup, gates, import order, prune, audit).
5. **Reconcile docs:** [MIGRATION_STATUS.md](./MIGRATION_STATUS.md) / [MIGRATION_STATUS_SUMMARY.md](./MIGRATION_STATUS_SUMMARY.md) remain **Rails-centric**; banners point here.

---

## 6. Quick commands (local)

```bash
# Legacy snapshot Postgres (PG 13)
docker compose -f docker-compose.postgres-snapshot.yml up -d

# Rebuild extracted data from parts (large disk, ~minutes)
./scripts/restore-postgres-from-data-parts.sh

# Alembic (from src/backend, with venv + deps)
export DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:15432/recruit_db
alembic upgrade head

# Migration CLI (global flags before subcommand: --dry-run, --json-logs)
export LEGACY_ARC_DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:15432/arc
export LEGACY_DVBIC_RESEARCH_DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:15432/dvbic_research
cd src/backend && python -m migrations_cli --dry-run preflight
python -m migrations_cli validate
python -m migrations_cli deploy-check
python -m migrations_cli legacy-stats

# First-party imports (respect order on a fresh DB; set MIGRATION_BATCH_ID per step or reuse)
export MIGRATION_BATCH_ID=2026-05-11T1200Z-my-run
python -m migrations_cli --dry-run import-arc-auth-users
python -m migrations_cli import-arc-auth-users
python -m migrations_cli import-arc-studies
python -m migrations_cli import-arc-subjects
python -m migrations_cli import-arc-subject-study
python -m migrations_cli import-arc-assessment-types
python -m migrations_cli import-arc-proc-list
python -m migrations_cli import-arc-instrument-tables   # MMSE, NPIQ, … → assessments (after proc_list + maps)
python -m migrations_cli import-dvbic-studies
python -m migrations_cli import-dvbic-subjects
python -m migrations_cli import-dvbic-subject-study
python -m migrations_cli import-dvbic-session-notes   # before instruments on fresh DBs (see MIGRATION_PROGRESS)
python -m migrations_cli import-dvbic-instrument-tables
python -m migrations_cli import-arc-user-study          # optional; needs study_acl usernames in arc.auth_user
python -m migrations_cli progress-summary

# After load, if deploy-check shows duplicate arc visit rows (see runbook):
# python -m migrations_cli prune-duplicate-arc-proc-assessments --apply

# Go-live audit line (audit_logs):
# python -m migrations_cli record-migration-audit "Describe what was released."

# PDF snapshots (requires: pip install -r src/backend/requirements.txt)
python scripts/db_snapshot_pdf.py --preset recruit -o output/recruit-db-snapshot.pdf
python scripts/db_snapshot_pdf.py --preset all-legacy --limit 8   # output/arc-db-snapshot.pdf + dvbic-research-db-snapshot.pdf
```

---

## 7. Open questions (from the plan)

- **Cutover:** one-time bulk load vs ongoing delta sync.
- **User accounts:** migrate real credentials vs synthetic migration user only.
- **Canonical overlap:** when both `arc` and DVbic own overlapping *non-subject* domains, which DB wins for import order (subjects already governed by merge rules above).

---

## 8. Revision history

| Date | Change |
|------|--------|
| 2026-05-07 | Initial **CURRENT_STATUS** consolidating snapshot tooling, Alembic baseline, Phase A discovery doc, and plan vs implementation gaps. |
| 2026-05-07 | **Schema:** `legacy_id_map`, `migration_events`, migration system user (`b3e8a1c92d40`). **CLI:** `migrations_cli` (`preflight`, `validate`, `legacy-stats`, `progress-summary`, `import-arc-auth-users`, `import-arc-studies`). Doc: [MIGRATION_PROGRESS_AND_STRUCTURE.md](./MIGRATION_PROGRESS_AND_STRUCTURE.md). |
| 2026-05-11 | **ETL:** `import-arc-subjects`, `import-arc-subject-study`, `import-dvbic-studies`, `import-dvbic-subjects`; `etl_dvbic.py`. Production: set `DATABASE_URL` to target RECRUIT, **`pg_dump` backup first**, run imports in §6 order. |
| 2026-05-11 | **Phase C1:** `import-arc-assessment-types` (`proc_desc` → `assessment_types`), `import-arc-proc-list` (`proc_list` → `assessments` + `legacy_id_map`); `etl_arc_proc.py`. |
| 2026-05-11 | **Phase C2 / D1:** `import-arc-instrument-tables`, `import-dvbic-instrument-tables` (`etl_arc_instruments.py`, `etl_dvbic_instruments.py`); dry-run for DVbic instruments sums `COUNT(*)` per table (upper bound). Unmapped rows → `migration_events`. |
| 2026-05-07 | **Deploy tooling:** `deploy-check`, `prune-duplicate-arc-proc-assessments`, `record-migration-audit`; [MIGRATION_DEPLOY_RUNBOOK.md](./MIGRATION_DEPLOY_RUNBOOK.md). |
