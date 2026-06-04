# Legacy data migration plan: `arc` and DVbic → RECRUIT

This document describes how to move data from the legacy PostgreSQL backup (same shape as the local snapshot: database **`arc`**, multiple **`dvbic_*`** databases) into the **RECRUIT** application schema. **Roadmap for remaining ETL and merge mechanics:** [LEGACY_MIGRATION_REMAINING_AND_MERGE_PLAN.md](./LEGACY_MIGRATION_REMAINING_AND_MERGE_PLAN.md). It assumes schema changes for RECRUIT itself continue to use **Alembic**; **data** migration is separate ETL delivered as a **versioned command-line tool** you run in staging and production—not ad-hoc SQL, and not Alembic revisions alone.

---

## 1. Goals and constraints

### Goals

- Load legacy **subjects**, **studies**, **memberships**, **users** (as appropriate), and **instrument / assessment** data into RECRUIT.
- Preserve **traceability** from RECRUIT rows back to legacy primary keys (for support, audits, and re-runs).
- Support **repeatable** imports (dry-run, idempotent re-import into a clean DB, or controlled upserts).
- Deliver **versioned, runnable migration scripts** (CLI) suitable for **production execution** on a server or jump host—same code path as staging, configuration via environment only (§4.6, §5 Phase B).
- When the same real-world participant appears in **`arc`** and **DVbic**, represent them as a **single `subjects` row** in RECRUIT, with **audited migration notes** describing merges and other judgment calls.

### Constraints

- Legacy layout is **heterogeneous**: Rails and Django artifacts coexist with custom clinical tables.
- **Multiple databases** on one cluster (`arc`, `dvbic_research`, `dvbic_npdata`, …) may each hold part of the truth; **canonical source per entity** must be decided explicitly.
- **PHI / compliance**: treat all legacy DBs as sensitive; do not mutate the backup; log migration activity.

---

## 2. Source systems (as observed on the snapshot)

### 2.1 Database `arc`

- **Schemas:** `public` only (snapshot).
- **Shape:** ~65 base tables mixing:
  - **Rails:** `schema_migrations`, `ar_internal_metadata`
  - **Django:** `auth_*`, `django_*`, `django_session`, `django_admin_log`, …
  - **Custom spine:** `subj_list`, `study_list`, `study_desc`, `proc_list`, `proc_desc`, `studyproc_list`, `study_acl`, …
  - **Instruments / clinical:** many domain tables (e.g. MMSE, NPIQ, GDS, consensus dx, driving, imaging, etc.) and parallel `ummc_*` tables.
- **Relationships:** Foreign keys in `public` tie `proc_list` to `subj_list`, `study_desc`, `proc_desc`; `study_list` to `subj_list` / `study_desc`; Django auth tables to each other; some satellite tables FK to `proc_list`.

### 2.2 Databases `dvbic_*` (non-exhaustive)

Examples on the snapshot: `dvbic_research`, `dvbic_research2`, `dvbic_research_test`, `dvbic_npdata`, `dvbic_irb`, `dvbic_auth_django`, `dvbic_datashare`, …

- **`dvbic_research`** (largest sample): **~169** `public` tables — Rails/Django plus many **per-instrument** tables (often `*_raw`, `*_scored`, dimension tables like `_sex`, `_race`, …).
- **Smaller DVbic DBs** likely hold **satellite** domains (IRB, NP extracts, auth-only, etc.).

**Implication:** migration is **per database (or per bounded set)**, followed by a **subject identity merge** step when the same person exists in more than one source (see §4.5).

---

## 3. Target RECRUIT schema (load order)

Dependencies dictate **insert order**:

1. **`users`** — real operators and/or synthetic “migration” accounts for `created_by`.
2. **`studies`** — includes `principal_investigator_id` → `users.id`.
3. **`subjects`**
4. **`subject_study`**, **`user_study`** — enrollment and study access.
5. **`assessment_types`** — define each instrument type you will load (`name`, `display_name`, optional `fields` JSON).
6. **`assessments`** — `subject_id`, optional `study_id`, `assessment_type`, dates, `total_score`, **`data` JSON** for legacy column payloads.
7. **`session_notes`** — if legacy free text / visit notes map cleanly.
8. **`audit_logs`** — **required for migration judgment calls** (subject merges, tie-breaks, data fixes); see §4.5. Optional batch-level summaries (row counts) may use the same mechanism or append-only log files under change control.

**Recommended pattern for instruments:** one legacy **instrument row** → one **`assessments`** row with **`data`** holding the normalized or raw column subset, plus **`assessment_types`** describing the type. This avoids exploding RECRUIT’s relational model for every legacy table.

---

## 4. Cross-cutting design

### 4.1 Legacy ID map (strongly recommended)

Add a dedicated table in **`recruit_db`** (or equivalent), e.g. `legacy_id_map`, with columns such as:

- `source_system` (e.g. `arc`, `dvbic_research`)
- `source_table`
- `source_pk` (text or bigint)
- `target_table` (`subjects`, `studies`, `assessments`, …)
- `target_pk` (integer id in RECRUIT)
- `batch_id` / `imported_at` (for reruns and audits)

Use this for **idempotent** imports and **support** (“which legacy row became this assessment?”).

**Multiple legacy rows → one RECRUIT subject:** store **one map row per source row**, all with the same `target_table = 'subjects'` and the same `target_pk` (the merged `subjects.id`). Example: `arc` / `subj_list` / PK `123` and `dvbic_research` / `some_participant` / PK `456` both map to `subjects.id = 42`. Never delete the fact that two sources fed one subject—only add superseding map rows if you intentionally remap.

### 4.2 Subject merge policy and migration audit trail

**Policy (decided):** when the same real-world participant is **confirmed** across `arc` and DVbic (or duplicate legacy records), they must resolve to **one `subjects` row**. When identity is **not** confirmed by the **strict first-line rule** (see **§4.2.1**), import as **separate `subjects` rows** until someone **explicitly** links or merges them in RECRUIT (or a controlled migration/review step)—never a silent fuzzy merge.

### 4.2.1 First-line merge rule (“precision over recall”)

**Decided (option A — remainder stays separate):**

1. **Auto-merge only** when a **single, shared, stable identifier** matches **exactly** between sources. **Which identifier that is remains TBD**—to be chosen in **Phase A** after inspecting the **production backup** (column overlap, data quality, and whether any shared key actually exists between `arc` and `dvbic_research`). **Until it is locked:** treat the auto-merge allowlist as **empty** (i.e. **no** pass‑1 cross-system merges; all cross-system pairs stay **separate subjects** per §4.2.1 until explicit merge). When locked, document the rule in the mapping spec and in code/config. Write **`audit_logs`** + **`legacy_id_map`** for every auto-merge.
2. **Everything else:** create **one `subjects` row per legacy participant row** (each with `legacy_id_map`). Do **not** auto-merge on fuzzy or heuristic matches. **Later:** explicit human-approved merge (or in-app link) collapses to one subject; that action must also write **`audit_logs`** (and update maps / re-point FKs per your ETL design).

This keeps early loads **safe and auditable**; duplicate-looking people remain visible as duplicates until intentionally resolved.

**Migration notes / audit log (decided):** every non-trivial migration decision that a reviewer would care about later—especially **subject merges**, conflicting demographics, chosen canonical field values, and “inferred” links—must leave a **durable audit record**.

**Recommended implementation (fits current RECRUIT schema):**

1. **System user for migration** — Create a dedicated **`users`** row used only for imports (e.g. `migration@system.internal`). ETL runs attribute `audit_logs.user_id` / `user_email` to this account (the `audit_logs` model requires a non-null `user_id`).
2. **`audit_logs` rows** — For each merged subject (and for other judgment calls), insert at least one row with:
   - `action`: e.g. **`MIGRATION_MERGE`** or **`MIGRATION_NOTE`** (extend allowed values in application validation if you currently whitelist `CREATE` / `UPDATE` only).
   - `entity_type`: **`subject`** (or **`migration`** if you prefer not to attach to a subject id for batch events).
   - `entity_id`: the RECRUIT **`subjects.id`** after merge (for subject-scoped notes).
   - `change_summary`: short human-readable sentence (what was merged, by what rule).
   - `additional_context`: JSON string with structured detail, e.g. `{ "batch_id": "...", "sources": [...], "resolved_fields": {"dob": {"chosen": "...", "from": "arc", "rejected": "..."}}, "match_rule": "MRN+DOB", "rationale": "free text" }`. Use **`resolved_fields` / `rationale`** to capture **as-you-go** decisions when there is no fixed global precedence between sources.
3. **Optional companion table** — If JSON in `audit_logs` is too constrained for querying, add a small **`migration_subject_merge`** (or generic **`migration_events`**) table via Alembic and still write a matching **`audit_logs`** row for Part 11–style user/time/action visibility. The plan’s minimum bar is **auditable narrative + structured context** in `audit_logs`.

**When to write a migration audit row (non-exhaustive):**

- Collapsing two+ legacy participant records into one `subjects` row.
- Choosing one source over another for DOB, name spelling, sex/race/ethnicity, or identifiers.
- Creating a subject with **no** prior legacy row (manual correction) during import.
- Skipping or quarantining a legacy row (store note referencing legacy PK and reason).

### 4.3 Tooling

| Approach | When to use |
|----------|----------------|
| **Python ETL** (SQLAlchemy, two engines: read legacy, write RECRUIT) | Complex transforms, JSON assembly, validation — **preferred default**. |
| **Plain SQL** (`psql`, views, `INSERT … SELECT`) | Simple 1:1 copies; harder for 100+ instrument tables and JSON. |

**Alembic:** use only for **RECRUIT schema** evolution (e.g. adding `legacy_id_map`). Do not use Alembic as the primary vehicle for **bulk legacy data** loads.

### 4.4 Environments

- **Read-only** access to the backup (or restore copy).
- **Staging `recruit_db`** for repeated full imports until counts match.
- **No writes** to legacy databases during migration development unless explicitly required.

### 4.5 Authentication

- Prefer **not** migrating password hashes unless algorithms align and policy allows.
- Plan for **password reset**, **OIDC**, or **new credentials** for real users post-cutover.

### 4.6 Production execution (how this plan supports robust server runs)

The plan is intentionally built around **Phase B’s production-grade CLI** (§5) and **Phase C** modules—not one-off manual SQL on prod.

**On the production server you should:**

1. Deploy a **specific git tag / release artifact** that contains the migration code (same commit tested in staging).
2. Set **secrets and URLs** only via the host environment or your secret manager (never commit).
3. Take a **fresh `pg_dump` of RECRUIT** (or snapshot) immediately before `run-all` or the first destructive phase.
4. Run **`--dry-run` first** against prod URLs if your policy allows read-only legacy access from prod network; otherwise dry-run only from a host that can reach both DBs.
5. Run **`run-all`** (or phased subcommands) with a **new `MIGRATION_BATCH_ID`**; archive **stdout logs** with the change ticket.
6. Run packaged **`validate`** (Phase D queries) and sign off.

**Rollback:** the plan assumes **restore from pre-migration dump** for catastrophic failure; row-level “undo” is optional and expensive—design idempotency instead.

---

## 5. Phased execution

### Phase A — Discovery and mapping

**Status:** Initial discovery for **`arc`** + **`dvbic_research`** completed on the local snapshot — see **[LEGACY_DATA_MIGRATION_PHASE_A_DISCOVERY.md](./LEGACY_DATA_MIGRATION_PHASE_A_DISCOVERY.md)**. Re-run counts, null rates, and merge-key analysis on the **production backup** before cutover.

**Deliverables**

- Spreadsheet or structured doc: **legacy table.column → RECRUIT table.column** or **`assessments.data` JSON path**.
- **Entity resolution rules:** how a legacy person becomes a `subjects` row; how studies map; how visits (`proc_list` etc.) map to `assessments.assessment_date` / `study_id`.

**Tasks**

- Document **primary keys** and **natural keys** for: subjects, studies, visits/procedures, users.
- For **`dvbic_research`**, classify tables: **core** (participants, studies, visits), **dimension** (`_*` enums), **instrument** (`*_raw` / `*_scored`), **noise** (sessions, pgAdmin, unused).
- Export **FK lists** per database (`pg_constraint` where `contype = 'f'`).
- **Strict auto-merge key (`arc` ↔ DVbic`):** inventory candidate columns (shared study subject id, MRN, etc.), assess non-null overlap and normalization needs, **select one exact-match rule** or confirm **none** (then all cross-system merges stay manual/explicit only).
- Decide **canonical database per RECRUIT entity** when both `arc` and DVbic hold overlapping domains (subjects aside, where merge rules above apply).

### Phase B — Staging and **production-grade migration CLI**

**Goal:** ship **the same versioned scripts** you use in dev/staging so you can run them on the **production server** (or from a controlled jump host) with only **configuration** and **secrets** changing—not ad-hoc SQL.

**Deliverables**

- Runnable **CLI or script package** (implemented as **`migrations_cli`** under `src/backend/`; run `python -m migrations_cli …` from `src/backend`) with:
  - **Subcommands or phases** aligned to §5 / dependency order (e.g. `users`, `studies`, `subjects`, `memberships`, `assessment-types`, `assessments`, `session-notes`, `validate`, **`run-all`**).
  - **Configuration via environment variables** (and optional `.env` **not** committed): `DATABASE_URL` (RECRUIT), `LEGACY_DATABASE_URL` or multiple URLs (`ARC_DATABASE_URL`, `DVBIC_RESEARCH_DATABASE_URL`, …), **`MIGRATION_BATCH_ID`** (required for every prod run), `LOG_LEVEL`, paths to mapping YAML/JSON if used.
  - **`--dry-run`**: no commits, or single rolled-back transaction; log intended row counts and sample keys.
  - **`--resume` / idempotency**: use **`legacy_id_map`** (and/or unique business keys) so a failed mid-run re-execution does not duplicate rows.
  - **Structured logging** (timestamps, batch id, phase, duration, rows read/written, errors) to **stdout and/or a log file** suitable for archiving with the change record.
  - **Non-zero exit codes** on failure; clear error messages.
  - **Pre-flight checks** before mutating prod: connectivity to legacy + RECRUIT, RECRUIT **Alembic schema at expected revision**, existence of migration system user, disk/quota sanity if writing large logs.
- **Pinned runtime:** document **`requirements.txt`** slice or **Dockerfile** for the migration runner so prod uses the **same Python + dependency versions** as CI/staging.
- **Operator runbook** (short markdown in-repo or internal wiki): backup (`pg_dump` RECRUIT), order of commands, rollback (**restore dump** or documented truncate scope), who signs off, where logs go.

**Tasks**

- Implement skeleton CLI in Phase B; flesh out modules in Phase C.

### Phase C — Incremental module delivery

Implement and validate in **dependency order**, each with **row-count checks**:

| Module | Legacy inputs (examples) | RECRUIT outputs |
|--------|---------------------------|-----------------|
| Users | `auth_user`, `admin_users`, DVbic equivalents | `users` + map |
| Studies | `study_desc`, `study_list`, DVbic study tables | `studies` + map |
| Subjects | `subj_list`, DVbic participant tables | **Pass 1:** one `subjects` row per legacy row + `legacy_id_map`. **Auto-merge** only on strict exact shared ID (§4.2.1); **`audit_logs`** per merge. **Remainder:** separate subjects until explicit link/merge + audit. |
| Memberships | joins implied by `study_list`, `user_study` / ACL patterns | `subject_study`, `user_study` |
| Assessment types | agreed instrument list | `assessment_types` |
| Assessments | per-instrument tables | `assessments` + JSON `data` |
| Session notes | if mapped | `session_notes` |

### Phase D — Validation

- **Per-table counts** (legacy vs. migrated).
- **FK integrity** on RECRUIT side (no orphan assessments).
- **Sample cohort review** (fixed list of legacy IDs) compared side-by-side.
- **Re-import test:** empty RECRUIT data tables, full pipeline, identical results.

### Phase E — Cutover

- Freeze or **delta** strategy for legacy writes.
- Execute the **same migration CLI** (§5 Phase B) against production config; follow the **operator runbook** (backup, dry-run policy, logging, sign-off).
- Final import, smoke tests, enable production traffic.

---

## 6. Source-specific notes

### 6.1 `arc`

- Treat **`proc_list`** as the central **visit/procedure** hub linked to **`subj_list`** and **`study_desc`** / **`study_list`**.
- Map each **instrument table** row to **`assessments`** (type + `data`).
- Skip obvious **non-business** tables unless required (`django_session`, `pga_*`, … unless you rely on them).

### 6.2 DVbic

- Start from **`dvbic_research`** (or whichever DB stakeholders name as **system of record** for participants and visits).
- Use **`dvbic_auth_django`** (or similar) **only if** canonical users are not already in the main research DB.
- Pull from **`dvbic_irb`**, **`dvbic_npdata`**, etc., only when RECRUIT features require that data (may map to notes, custom JSON, or future tables).

---

## 7. Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Overlapping identities across `arc` and DVbic | **Strict auto-merge only**; otherwise **separate `subjects`** until explicit merge (§4.2.1). **`legacy_id_map`** + **`audit_logs`** for every merge. |
| Schema drift on live server vs. snapshot | Re-run discovery on **production backup** before final cutover. |
| Huge surface area (100+ tables) | **Vertical slice** first (one study / small cohort), then generalize. |
| Ad-hoc SQL on production | **Forbidden default:** all writes go through the **versioned migration CLI**; emergency SQL documented separately in the runbook. |
| Audit / FDA expectations | Document import in **`audit_logs`** or a dedicated **import_audit** table; retain source PK in map or JSON. |

---

## 8. Decisions and open questions

### 8.1 Resolved

| Topic | Decision |
|--------|----------|
| **Subject merge policy** | **Merge** to a **single `subjects` row** when identity is **confirmed**. **Option A (remainder):** if not confirmed by the **strict exact-ID** rule, keep **separate `subjects` rows** until an **explicit** link/merge in RECRUIT or a migration review step (with **`audit_logs`**). No silent fuzzy merges on bulk import. |
| **Audit of merge / judgment calls** | Record **migration notes** in **`audit_logs`** (plus structured JSON in `additional_context`); use a dedicated **migration system `users` row** for `user_id`. Optional extra **`migration_events`** table if query/reporting needs outgrow `audit_logs`. |
| **Strict auto-merge key (`arc` ↔ DVbic`)** | **TBD in Phase A** on the real backup. Until chosen and implemented, **no** automatic cross-system merges (empty allowlist); separate subjects + explicit merge later remains valid. |
| **Conflicting field values (`arc` vs DVbic`)** | **No global precedence rule required up front.** Resolve **as you go** (per subject, per cohort, or per field when implementing a slice). Each resolution must be **recorded** in **`audit_logs.additional_context`** (e.g. `resolved_fields`, `chosen_value`, `rejected_value`, short `rationale`) so later reviewers see what was decided and why—not only the final `subjects` row. |
| **Production migration delivery** | **Versioned scripts (CLI)** with env-based config, **`--dry-run`**, idempotency via **`legacy_id_map`**, structured logs, pre-flight checks, and an **operator runbook** (§4.6, §5 Phase B, §5 Phase E). Same code path for staging and prod. |

### 8.2 Still open (refine with stakeholders)

1. **Cutover style:** One-time bulk load only, or **ongoing delta sync**?
2. **User accounts:** Migrate real logins vs. synthetic users only for `created_by` / audit?

---

## 9. Related repo artifacts

- **Phase A discovery (snapshot):** [LEGACY_DATA_MIGRATION_PHASE_A_DISCOVERY.md](./LEGACY_DATA_MIGRATION_PHASE_A_DISCOVERY.md) — re-validate on production backup.
- **Migration CLI & runbook** (Phase B / §4.6): versioned entry point, env config, dry-run, idempotency, prod checklist—implemented alongside ETL modules.

---

## 10. Revision history

| Date | Author | Notes |
|------|--------|--------|
| 2026-05-07 | Engineering (draft) | Initial plan from codebase + snapshot inspection. |
| 2026-05-07 | Engineering (draft) | Resolved: single-subject merge across sources; migration notes via `audit_logs` (+ optional `migration_events`). |
| 2026-05-07 | Engineering (draft) | Field conflicts: resolve as-you-go; document each choice in `audit_logs` JSON (no upfront global precedence required). |
| 2026-05-07 | Stakeholder | Merge remainder: **Option A** — separate subjects until explicit merge; strict auto-merge only for exact shared ID once defined (§4.2.1). |
| 2026-05-07 | Stakeholder | Strict auto-merge key: **TBD Phase A**; until then, no cross-system auto-merge (empty allowlist). |
| 2026-05-07 | Engineering | **Phase A** initial discovery doc: [LEGACY_DATA_MIGRATION_PHASE_A_DISCOVERY.md](./LEGACY_DATA_MIGRATION_PHASE_A_DISCOVERY.md) (`arc` + `dvbic_research` on snapshot). |
