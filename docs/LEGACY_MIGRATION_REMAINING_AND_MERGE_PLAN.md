# Remaining legacy migration + merge model (`arc`, `dvbic_research` → RECRUIT)

**Status:** Planning / execution guide  
**Last updated:** 2026-05-11  
**Related:** [LEGACY_DATA_MIGRATION_PLAN.md](./LEGACY_DATA_MIGRATION_PLAN.md) (strategy, audit, tooling), [LEGACY_DATA_MIGRATION_PHASE_A_DISCOVERY.md](./LEGACY_DATA_MIGRATION_PHASE_A_DISCOVERY.md) (schema, counts, merge-key analysis), [CURRENT_STATUS.md](./CURRENT_STATUS.md) (what is implemented today).

This document answers: **(1) what work remains** after the current CLI imports, and **(2) how `arc` and `dvbic_research` are intended to converge** on the single RECRUIT relational model (`users`, `studies`, `subjects`, `subject_study`, `user_study`, `assessment_types`, `assessments`, `session_notes`, `audit_logs`, `legacy_id_map`, `migration_events`).

---

## 1. Target RECRUIT model (single graph)

Everything from both legacy databases ultimately lands in **one** set of tables. Conceptually:

```text
users ─────────────┐
                   ├── studies (principal_investigator_id optional)
                   │
subjects ──────────┼── subject_study ── studies
      │            │
      ├── assessments ── (optional study_id, assessment_type, data JSON)
      ├── session_notes
      └── (merge/review actions) → audit_logs + migration_events

legacy_id_map: every legacy row you care to trace → target row (one map row per source row; merges = same target_pk, multiple map rows)
```

**Principle:** RECRUIT does **not** keep parallel “arc” vs “dvbic” subject tables. It keeps **one** `subjects` table. Source discrimination is **`legacy_id_map.source_system`** (+ `source_table`, `source_pk`), not duplicate domain tables.

---

## 2. What is already done (baseline)

| Layer | Done in repo / CLI |
|--------|---------------------|
| **Schema** | RECRUIT tables + `legacy_id_map` + `migration_events` + migration system user (Alembic `b3e8a1c92d40`). |
| **`arc`** | `auth_user` → `users`; `study_desc` → `studies`; `subj_list` → `subjects`; `study_list` → `subject_study`; maps for those entities. |
| **`dvbic_research`** | `studies` → `studies` (`dvbic-study-{id}`); `subjects` → `subjects`; maps. |
| **Cross-system** | **No automatic merge** yet: arc subjects and DVbic subjects are **separate** `subjects` rows unless you later apply a crosswalk or in-app merge (by design; see §4). |

---

## 3. Remaining work — **`arc`** (ordered phases)

### Phase C1 — Visits / procedure spine → `assessments` (**implemented in CLI**)

| Source | Rows (order of magnitude, snapshot) | Target |
|--------|--------------------------------------|--------|
| **`proc_list`** | ~25k | **One `assessments` row per `proc_num`** (`import-arc-proc-list`). |
| **`proc_desc`** | ~160 | **`assessment_types`** with `name = arc-proc-{code}` (`import-arc-assessment-types`). |
| **`studyproc_list`** | ~162 | Matrix study↔procedure — **not yet** used for validation (optional next). |

**Implemented transforms:** `grid` → `subjects.id`, `study_code` → `studies.id` (nullable if unmapped) via `legacy_id_map`; `assessment_date` / `assessment_time` from `proc_date` / `proc_starttime`; `notes` ← `comment`; **`data` JSON** holds `proc_num`, codes, status, quality, `proc_endtime`; **`legacy_id_map`**: `arc` / `proc_list` / `{proc_num}` → `assessments`. **`assessment_type`** string = `arc-proc-{proc_code}` (must exist in `assessment_types` — run types import first).

### Phase C2 — Instrument / domain tables (arc)

High-volume examples on snapshot: **`mmses`**, **`npiqs`**, **`gds15s`**, **`faqs`**, **`rawscores`**, **`contact`**, **`consensusdxes`**, imaging/driving tables, etc. (~65 public tables total; many tied to `proc_list` or `grid`).

| Pattern | Approach |
|---------|----------|
| Row keyed by **`proc_num`** | Join to `proc_list`; attach JSON to the **same** assessment row as the visit, **or** create child assessment rows sharing `subject_id`/`study_id`/date with a discriminant in `data`. |
| Row keyed only by **`grid`** | `subject_id` from map; `study_id` nullable or from “index” study on `subj_list` when safe. |
| Wide / sparse legacy table | Prefer **one `assessments` row** + **`data` JSON** mirroring legacy columns (namespaced keys) to avoid dozens of new RECRUIT tables. |

**Deliverable:** versioned CLI commands (e.g. `import-arc-proc-list`, `import-arc-mmses`, …) or a **registry** (YAML/JSON) listing table → join key → assessment_type slug → column allowlist for JSON.

### Phase C3 — Text / notes

| Source | Target |
|--------|--------|
| **`subj_list.note`**, **`proc_list.comment`**, other text blobs | **`session_notes`** and/or **`assessments.notes`**, with PHI policy (date = visit date or import date). |

### Phase C4 — Access control

| Source | Target |
|--------|--------|
| **`study_acl`** (if still relevant) | **`user_study`** after resolving legacy user identity → `users.id`. May require a mapping from arc usernames to RECRUIT `users`. |

### Phase C5 — Django / Rails noise (explicit scope)

| Tables | Likely action |
|--------|----------------|
| `django_session`, `django_admin_log`, `auth_permission`, … | **Do not import** into RECRUIT clinical tables; archive or ignore unless you need admin forensics (separate decision). |
| `schema_migrations`, `ar_internal_metadata` | **No import.** |

### Phase C6 — Code / enum quality

- Map **`study_desc.status`**, **`subj_list` research/race/sex/ethnicity** integers to **controlled strings** in RECRUIT (replace placeholder `arc-race-*` strings when definitions are signed off).
- Resolve **`principal_investigator_id`** from free-text investigator fields where possible.

---

## 4. Remaining work — **`dvbic_research`**

### Phase D1 — Instrument tables → `assessments`

- **~55+** `*_raw` / `*_scored` (and related) tables; many keyed by **`subject_id`** (bigint), some by **`cencsubjectid`**, some with **`study_id`**.
- **Pattern:** for each table (or grouped family), insert **`assessments`** with `subject_id` from `legacy_id_map` (`dvbic_research` / `subjects` / `{id}`), optional `study_id` from map or from row’s `study_id`, `assessment_type` = stable slug (e.g. `dvbic-dot_counting-v1`), `assessment_date` from best available column or `created_at`, **`data`** = row JSON subset.

### Phase D2 — “Other” bucket tables (~84 classified as other in Phase A)

- Per-table decision: **migrate to JSON assessment**, **new normalized RECRUIT tables** (Alembic), or **out of scope** for v1. Track exclusions in runbook.

### Phase D3 — Polish

- Map **`studies.status`** bigint → RECRUIT string.
- Optional: resolve **`investigator`** / **`created_by`** strings to `users`.

---

## 5. How **`arc` and `dvbic_research` merge** into one RECRUIT model

### 5.1 Default today: **parallel subjects, unified tables**

| Concept | Behavior |
|---------|----------|
| **Same person in both systems** | Today they appear as **two `subjects` rows** (one from arc path, one from DVbic path). That matches **Option A** in the main plan: **empty auto-merge allowlist** until a strict key or crosswalk exists ([Phase A §4](./LEGACY_DATA_MIGRATION_PHASE_A_DISCOVERY.md)). |
| **Same concept, different sources** | **`studies`**: arc-backed protocols (`arc-study-{code}`) and DVbic protocols (`dvbic-study-{id}`) **coexist**; `subject_study` only links arc subjects to arc studies today; DVbic enrollments may need **`subject_study`** (or equivalent) when instrument rows imply study membership—**define rule** (e.g. infer from `study_id` on instrument rows). |
| **Traceability** | **`legacy_id_map`**: one row per **legacy source row** → **one** `target_table` + `target_pk`. After a merge, **multiple** map rows may share the **same** `target_pk` (`subjects.id`) but different `(source_system, source_table, source_pk)` — do **not** delete historical map rows without policy. |

### 5.2 Future: **one RECRUIT subject for one real person**

Triggered only when identity is **confirmed** (never silent fuzzy match for bulk load):

| Mechanism | Role |
|-----------|------|
| **Strict shared key** (if validated on production backup) | e.g. normalized SSN match, or institutional MRN, **only** after type alignment (`arc.ss_num` vs `dvbic.ssn`) and legal/compliance sign-off. Document in config as **allowlisted auto-merge rule**. |
| **Crosswalk file** | CSV / controlled table: `arc_grid` ↔ `dvbic_subjects_id` (or equivalent). ETL or review tool updates **`subjects`** (keep one row, nullify or redirect the duplicate per FK strategy) and writes **`audit_logs`** + **`migration_events`**. |
| **In-app merge** (post-load) | Users merge duplicates; app writes **`audit_logs`**, updates FKs on `assessments` / `subject_study` / etc., and extends **`legacy_id_map`** so both legacy IDs point at the **surviving** `subjects.id`. |

### 5.3 Field-level conflicts when merging

When collapsing two `subjects` rows, the plan’s **“resolve as you go”** rule applies:

1. Choose canonical values for `first_name`, `dob`, `sex`, … with a documented **precedence** (e.g. “DVbic demographics for CENC cohort, arc for VA cohort”) **or** case-by-case in review.
2. Record every non-obvious choice in **`audit_logs.additional_context`** (JSON) and optionally **`migration_events`**.

### 5.4 Studies spanning both systems

- There is **no** automatic “same study” link between `arc.study_desc.code` and `dvbic_research.studies.id`.
- If a real-world protocol truly spans both: **manual** `studies` consolidation or a **`study_crosswalk`** (new table or map extension) is required; out of scope for pass‑1 ETL unless you add schema.

### 5.5 Assessments from two sources for one merged subject

After merge, **all** `assessments` rows should reference the **single** surviving `subject_id`. Pre-merge rows may need a **one-time SQL update** or ETL “repoint” step; must be **idempotent** and **audited**.

---

## 6. Suggested execution order (next milestones)

1. **`import-arc-assessment-types`** then **`import-arc-proc-list`** — **done** in CLI (`etl_arc_proc.py`).
2. **Extend `assessment_types`** per instrument as you add MMSE/NPIQ/… table imports.
3. **Top-N arc instrument tables** by row count / business priority — attach JSON to visit-linked assessments or standalone `assessments` rows.
4. **DVbic instrument pass** — same pattern, `assessment_type` prefixed (`dvbic-…`).
5. **`session_notes` / `user_study`** as needed for app parity.
6. **Production backup analysis** — re-run merge-key stats; decide **allowlist** vs **crosswalk-only**.
7. **Merge tooling** — CLI or admin workflow: apply crosswalk, write `audit_logs`, repoint FKs.

---

## 7. Engineering checklist (non-functional)

- [ ] **Dry-run + batch id** on every write command; **idempotent** reruns.  
- [ ] **Performance**: batch inserts, indexes on `legacy_id_map (source_system, source_table, source_pk)`.  
- [ ] **Quarantine** table or file for rows that fail validation (optional).  
- [ ] **Runbook**: `pg_dump` before production import; order of CLI commands; rollback = restore dump (or forward-fix scripts).  
- [ ] **PHI**: restrict PDF/snapshot tools on production; redact in logs.

---

## 8. Summary

| Question | Answer |
|----------|--------|
| Is “missing” arc data lost? | **No** in legacy DB; **proc_list spine is now in RECRUIT**; instrument tables (**C2**) and DVbic (**D1**) still pending. |
| How do arc + DVbic “merge”? | **Into the same RECRUIT tables**, not separate silos; **subjects** duplicates stay until **strict key, crosswalk, or manual merge** + **audit**. |
| What carries provenance? | **`legacy_id_map`** (+ **`audit_logs`** / **`migration_events`** for merges and judgment calls). |

For narrative strategy and audit detail, the **[LEGACY_DATA_MIGRATION_PLAN.md](./LEGACY_DATA_MIGRATION_PLAN.md)** remains authoritative; this file is the **roadmap for remaining ETL and the convergence story** aligned with current implementation.
