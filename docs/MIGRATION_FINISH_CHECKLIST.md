# Migration finish checklist (snapshot → production)

**Goal:** Close gaps that block a useful RECRUIT prod DB, without boiling the ocean on every legacy table.

Run from `src/backend/` with snapshot URLs (adjust host for your environment):

```bash
export DATABASE_URL='postgresql://postgres:postgres@127.0.0.1:15432/recruit_db'
export LEGACY_ARC_DATABASE_URL='postgresql://postgres:postgres@127.0.0.1:15432/arc'
export LEGACY_DVBIC_RESEARCH_DATABASE_URL='postgresql://postgres:postgres@127.0.0.1:15432/dvbic_research'
export MIGRATION_BATCH_ID='YYYY-MM-DD-finish'
```

Gate before/after each phase:

```bash
python -m migrations_cli migration-completeness
python -m migrations_cli deploy-check
```

---

## Tier 1 — Finish before `pg_dump` (clinical + access spine)

| # | Work | CLI / action | Done when |
|---|------|----------------|-----------|
| 1 | Alembic head on `recruit_db` | `alembic upgrade head` | `validate` shows head |
| 2 | Arc spine | auth-users, studies, subjects, subject-study, assessment-types, proc-list, instrument-tables, **studyproc-list** | `migration-completeness` proc/subj/proc_list gaps ≈ 0 |
| 3 | DVbic spine | studies, subjects, **subjects2**, subject-study, session-notes | session_notes gap ≤ 1 |
| 4 | Arc study access | **`import-arc-study-acl-users`** then **`import-arc-user-study`** | `study_acl` vs `user_study` gap ≈ 0 (duplicates OK) |
| 5 | Deploy gate | `deploy-check` | duplicate arc proc estimate = 0 |
| 6 | Audit | `record-migration-audit "…"` | one row in `audit_logs` |
| 7 | Baseline file | **`migration-verify-baseline`** | `data/migration_verify_baseline.json` for prod verify |

**Prod dump:** see [PROD_CUTOVER_SNAPSHOT.md](./PROD_CUTOVER_SNAPSHOT.md).

**Prod verify (after restore):** `migration-verify` + `deploy-check` — no legacy URLs.

---

## Tier 2 — Improve coverage (same snapshot; optional before dump)

| # | Work | Notes |
|---|------|--------|
| 7 | Re-run **`import-dvbic-instrument-tables`** after subjects2 | Links more assessments; orphans still log `migration_events` |
| 8 | DVbic **`subject_study`** residuals (~200+ pairs) | Legacy `subject_id` / `study_id` not in maps — per-table rules or accept |
| 9 | Set passwords | `set-user-password` for real Arc + ACL stub emails |

---

## Tier 3 — Out of v1 scope (track; do not block cutover)

| Area | Count | Decision |
|------|-------|----------|
| Arc gap tables (`field_desc`, `npdefs`, `users`, …) | 8 | Empty on snapshot; reference ETL or exclude |
| DVbic gap tables (no subject key) | 28 | Per-table design (`procedures`, raw impulsivity, polls, …) |
| Arc ↔ DVbic same person | — | No auto-merge; crosswalk / manual review |
| `migration_events` volume | ~3.4M | Orphan audit trail; optional dedupe later |

---

## Command order (finish pass)

```bash
python -m migrations_cli import-arc-study-acl-users
python -m migrations_cli import-arc-user-study
python -m migrations_cli import-dvbic-subjects2      # if not already run
python -m migrations_cli import-dvbic-subject-study
python -m migrations_cli import-dvbic-session-notes
# optional:
python -m migrations_cli import-dvbic-instrument-tables
python -m migrations_cli migration-completeness
python -m migrations_cli deploy-check
```

---

## Ownership

| Stream | Owner skill | Repo touch |
|--------|-------------|------------|
| Tier 1 CLI | Operator + backend | `migrations_cli` only |
| Tier 2 instruments | Backend / data | `etl_dvbic_instruments.py`, registry |
| Tier 3 gap tables | Product + data | new ETL or exclusions in runbook |
| App deploy | Platform | `DATABASE_URL`, not legacy URLs |
