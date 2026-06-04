# Migration progress and resulting structure

**Last updated:** 2026-05-07  
**Companion:** [CURRENT_STATUS.md](./CURRENT_STATUS.md) (where we are), [LEGACY_DATA_MIGRATION_PLAN.md](./LEGACY_DATA_MIGRATION_PLAN.md) (strategy).

This document summarizes **what is wired today** in `migrations_cli`, **recommended import order**, and **which RECRUIT tables** are filled. Row counts depend on your legacy backup; numbers below match a **local snapshot** run.

---

## 1. `migrations_cli` package layout

From `src/backend/`:

```text
migrations_cli/
  __init__.py
  __main__.py          # argparse: global flags then subcommand
  config.py            # DATABASE_URL, LEGACY_*_DATABASE_URL, MIGRATION_BATCH_ID, dry_run
  db.py                # read-only helpers (preflight / validate)
  commands.py          # subcommand wrappers
  etl_arc.py           # arc → RECRUIT (users, studies, subjects, subject_study, user_study, progress_summary)
  etl_arc_proc.py      # arc proc_desc / proc_list → assessment_types, assessments + map
  etl_arc_instruments.py   # arc instrument tables → assessments + map + migration_events (orphans)
  etl_dvbic.py         # dvbic_research → RECRUIT (studies, subjects, subject_study inference, session_notes)
  etl_dvbic_instruments.py # dvbic_research public.subject_id tables → assessments + map + migration_events
```

**Global flags** must appear **before** the subcommand:

```bash
python -m migrations_cli --dry-run import-arc-subjects
python -m migrations_cli --json-logs validate
```

---

## 2. Subcommands

| Command | Writes RECRUIT? | Notes |
|--------|------------------|--------|
| `preflight` | No | `DATABASE_URL` + optional legacy URLs. |
| `validate` | No | Alembic head + `pg_stat_user_tables` for core tables. |
| `legacy-stats` | No | Requires `LEGACY_ARC_DATABASE_URL`; optional DVbic URL. |
| `import-arc-auth-users` | Yes* | `arc.auth_user` → `users` + `legacy_id_map`. |
| `import-arc-studies` | Yes* | `arc.study_desc` → `studies` + `legacy_id_map`. |
| `import-arc-subjects` | Yes* | `arc.subj_list` → `subjects` + `legacy_id_map` (`created_by` = migration system user). |
| `import-arc-subject-study` | Yes* | `arc.study_list` → `subject_study` (needs arc maps for subjects + studies). |
| `import-arc-user-study` | Yes* | `arc.study_acl` → `user_study` (needs `auth_user` + `study_desc` maps; usernames must exist in `arc.auth_user`). |
| `import-arc-assessment-types` | Yes* | `arc.proc_desc` → `assessment_types` (`name` = `arc-proc-{code}`). No `MIGRATION_BATCH_ID` required. |
| `import-arc-proc-list` | Yes* | `arc.proc_list` → `assessments` + `legacy_id_map` (run after types + subject maps). |
| `import-arc-instrument-tables` | Yes* | Arc MMSE, NPIQ, … → **additional** `assessments` (`data.row` = full legacy row) + `legacy_id_map` (`arc` / `{table}` / PK). |
| `import-dvbic-studies` | Yes* | `dvbic_research.studies` → `studies` + `legacy_id_map` (`name` = `dvbic-study-{id}`). |
| `import-dvbic-subjects` | Yes* | `dvbic_research.subjects` → `subjects` + `legacy_id_map` (sex/race from `_sex` / `_race`). |
| `import-dvbic-subject-study` | Yes* | Inferred DVbic enrollments: distinct `(subject_id, study_id)` across legacy tables → `subject_study` (needs DVbic maps). |
| `import-dvbic-session-notes` | Yes* | `dvbic_research.session_notes` → `session_notes` + `legacy_id_map` (`source_table` = `session_notes_recruit` to avoid colliding with instrument maps). |
| `import-dvbic-instrument-tables` | Yes* | Tables with `subject_id` (minus exclusions, including `session_notes`) → `assessments` + map; may be **very large**. |
| `progress-summary` | No | Estimates + last 15 `legacy_id_map` rows. |
| `deploy-check` | No | Runs `validate` plus deploy warnings (duplicate arc `proc_list` assessments estimate). |
| `prune-duplicate-arc-proc-assessments` | Yes* | Deletes extra `arc-proc-*` rows sharing the same `data.proc_num` (default dry-run; use `--apply` after backup). |
| `record-migration-audit` | Yes* | One `audit_logs` row (migration system user) for milestones; pass summary text as args. |

\*Unless `--dry-run` (rolls back RECRUIT). `MIGRATION_BATCH_ID` required for writes that insert into `legacy_id_map` (not required for `import-arc-assessment-types` only). **`record-migration-audit`** does not require `MIGRATION_BATCH_ID` (optional context only).

---

## 3. Recommended import order (fresh RECRUIT DB)

1. `import-arc-auth-users`  
2. `import-arc-studies`  
3. `import-arc-subjects`  
4. `import-arc-subject-study`  
5. **`import-arc-assessment-types`** (from `proc_desc`)  
6. **`import-arc-proc-list`** (`proc_list` → `assessments`; needs types + subject maps)  
7. **`import-arc-instrument-tables`** (instrument rows; uses `proc_list` + subject/study maps)  
8. `import-dvbic-studies`  
9. `import-dvbic-subjects`  
10. **`import-dvbic-subjects2`** (historical DVbic ids used by `session_notes` and many instruments; run after `subjects`)  
11. **`import-dvbic-subject-study`** (DVbic subject↔study links into `subject_study`)  
12. **`import-dvbic-session-notes`** (typed session notes; run **before** instruments on fresh DBs so `session_notes` is not also bulk-imported as JSON `assessments`)  
13. **`import-dvbic-instrument-tables`** (after DVbic subject map exists)  
14. **`import-arc-studyproc-list`** (`arc.studyproc_list` → `study_procedures`; needs `import-arc-studies`)  
15. **`import-arc-study-acl-users`** (stub `users` for `study_acl.usr` not in `auth_user`)  
16. **`import-arc-user-study`** (arc ACL → `user_study`; run after step 15 when ACL usernames ≠ Django users)  

**DVbic after arc spine** avoids `studies.name` collisions. **`import-arc-proc-list`** must run **after** `import-arc-subjects` (and `import-arc-assessment-types`). **`--dry-run import-dvbic-instrument-tables`** only sums `COUNT(*)` per table (upper bound; does not subtract orphans).

**Env (optional):** `MIGRATION_COMMIT_CHUNK` (default `200`), `MIGRATION_STREAM_ROW_THRESHOLD` (default `40000`) for DVbic instrument pass.

**Production:** set `DATABASE_URL` to the **target** RECRUIT instance, take a **`pg_dump` (or managed backup)** before step 1, then run the same order with a batch id per run or per phase.

**Re-runs / resume:** Instrument importers look up `legacy_id_map` **before** inserting an `assessments` row, so repeating `import-dvbic-instrument-tables` does **not** duplicate mapped assessments. Rows that cannot be linked still append **`migration_events`** on each run (same orphan may produce multiple event rows); use a new `MIGRATION_BATCH_ID` when you want a clean audit trail, or plan a dedupe pass if you re-run often.

---

## 4. `legacy_id_map` keys

| source_system | source_table | Meaning |
|---------------|--------------|--------|
| `arc` | `auth_user` | Django user id → `users.id` |
| `arc` | `study_desc` | Study code → `studies.id` |
| `arc` | `subj_list` | Subject `grid` → `subjects.id` |
| `arc` | `proc_list` | Procedure / visit `proc_num` → `assessments.id` |
| `arc` | `{instrument_table}` | e.g. `mmses` PK → `assessments.id` (separate from `proc_list` map) |
| `dvbic_research` | `studies` | DVbic study bigint id → `studies.id` |
| `dvbic_research` | `subjects` | DVbic subject bigint id → `subjects.id` |
| `dvbic_research` | `subjects2` | Historical DVbic subject id → `subjects.id` (same target table; used by `session_notes` and many legacy rows) |
| `dvbic_research` | `{instrument_table}` | Primary key or hash id → `assessments.id` |
| `dvbic_research` | `session_notes_recruit` | Legacy `session_notes.id` → `session_notes.id` (app table; distinct from instrument map on `session_notes` → `assessments`) |

`subject_study` / `user_study` rows are **not** given `legacy_id_map` rows (composite PK only). Re-runs use `ON CONFLICT DO NOTHING`.

**Cross-system merge:** there is **no** automatic merge between arc and DVbic subjects (separate `subjects` rows per Phase A policy until a crosswalk exists).

---

## 5. Tables touched vs still empty

**Populated by current ETL:** `users`, `studies`, `subjects`, `subject_study` (arc `study_list` + inferred DVbic links), **`user_study`** (arc `study_acl` when usernames resolve to imported `auth_user` rows), **`session_notes`** (DVbic `session_notes` via `import-dvbic-session-notes`), **`assessment_types`**, **`assessments`**, **`migration_events`**, `legacy_id_map`.

**Still empty / not migrated:** optional **per-field** `audit_logs` beyond milestone rows from `record-migration-audit`; cross-system **subject** merge (arc↔DVbic) until crosswalk or allowlisted key; tighter links from instrument `assessments` to visits.

---

## 6. Sample snapshot counts (after full order)

Illustrative after a full run including proc spine + instrument passes on the **local snapshot**: ~5 `users`, ~52 `studies`, ~5.5k `subjects`, ~5.4k `subject_study`, **~280 `assessment_types`**, **~350k `assessments`**, **~370k `legacy_id_map`** rows; **`migration_events`** grows with unmapped instrument rows (often 1M+ on a noisy snapshot if many `subject_id` values lack a map). Exact totals depend on backup and how often imports are re-run.

---

## 7. Next engineering

- Link instrument **`assessments`** to parent **`proc_list`** / visits in `data` where it helps reporting.
- Optional dedupe for **`migration_events`** on re-runs; richer **`audit_logs`** for field-level merges when you add crosswalk tooling.
