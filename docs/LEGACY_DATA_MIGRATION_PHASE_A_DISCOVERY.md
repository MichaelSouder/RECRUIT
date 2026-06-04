# Phase A — Legacy discovery & mapping (`arc`, `dvbic_research` → RECRUIT)

**Status:** Complete for **local snapshot** (`recruit_postgres_snapshot`, PostgreSQL 13).  
**Caveat:** Re-run counts, null rates, and column samples on the **production backup** before cutover; numbers below are snapshot-only.

**Related:** [LEGACY_DATA_MIGRATION_PLAN.md](./LEGACY_DATA_MIGRATION_PLAN.md)

---

## 1. RECRUIT target schema (reminder)

| Target table | Purpose |
|--------------|---------|
| `users` | App accounts; `email` unique; `hashed_password`; `role`; optional `piv_certificate_id` |
| `studies` | `name` unique, `description`, dates, `status`, `principal_investigator_id` → `users` |
| `subjects` | `first_name`, `middle_name`, `last_name`, `date_of_birth`, `sex`, `ssn`, `race`, `ethnicity`, … |
| `subject_study` / `user_study` | M2M enrollment / study access |
| `assessment_types` | Catalog of instrument types (`name`, `display_name`, optional `fields` JSON) |
| `assessments` | `subject_id`, optional `study_id`, `assessment_type`, `assessment_date`/`assessment_time`, `total_score`, **`data` JSON** |
| `session_notes` | `subject_id`, optional `study_id`, `session_date`, `notes` |
| `audit_logs` | Migration merges / notes (`user_id` required — use migration system user) |

Planned support table (see main plan): **`legacy_id_map`** — not present on snapshot `recruit_db` in legacy cluster; add via Alembic on RECRUIT before ETL.

---

## 2. Database `arc` — entity model

### 2.1 Primary keys & row counts (snapshot)

| Table | PK | Rows (approx.) | Role |
|-------|-----|----------------|------|
| `study_desc` | `code` (int) | 33 | Study / protocol registry |
| `subj_list` | `grid` (int) | 4,820 | Subject demographics + link to “home” study |
| `study_list` | `index` (int) | 5,383 | Subject–study enrollment (`grid` + `study_code`) |
| `proc_list` | `proc_num` (int) | 24,797 | Visit / procedure instance (ties subject, study, procedure type) |
| `proc_desc` | `code` (int) | 160 | Procedure type dictionary |
| `auth_user` | `id` | 5 | Django users (operators) |

### 2.2 Foreign keys (`arc.public`, all 21)

| From | Column(s) | To | Notes |
|------|------------|-----|------|
| `subj_list` | `index_study` | `study_desc.code` | Optional “index” study for subject |
| `study_list` | `grid` | `subj_list.grid` | Enrollment |
| `study_list` | `study_code` | `study_desc.code` | |
| `proc_list` | `grid` | `subj_list.grid` | Visit → subject |
| `proc_list` | `study_code` | `study_desc.code` | Visit → study |
| `proc_list` | `proc_code` | `proc_desc.code` | Visit → procedure type |
| `studyproc_list` | `study_code`, `proc_code` | `study_desc`, `proc_desc` | Study–procedure matrix |
| `data_svfs`, `faqs`, `drivingdata_roadsigns` | various | `proc_list.proc_num` | Satellite data per visit |
| Django `auth_*`, `django_admin_log` | — | `auth_user`, `auth_group`, `auth_permission`, `django_content_type` | Auth / admin |

**Implication:** **`proc_list`** is the anchor for **time-stamped activity**; instrument tables in `arc` hang off `proc_num` or `grid` depending on table (discovery for each instrument table is Phase C per module).

### 2.3 Natural / business keys (`arc`)

| Entity | Candidate keys | Notes |
|--------|------------------|------|
| Subject | **`grid`** (surrogate PK) | Stable within `arc`. |
| Subject | `mrec_num` (varchar 30) | **Only ~141 / 4,820** non-empty distinct values on snapshot — **weak** for cross-system auto-merge. |
| Subject | `ss_num` (integer) | Present on all rows; semantics unknown (not obviously a full SSN string). |
| Subject | `(f_name, l_name, dob)` | Possible **fuzzy** match only — **not** allowed for pass‑1 auto-merge per plan (Option A + empty allowlist until strict key defined). |
| Study | `study_desc.code` + `descr` | |
| Visit | `proc_list.proc_num` | Date: `proc_date` / `proc_starttime` |

---

## 3. Database `dvbic_research` — classification (169 `public` tables)

Heuristic buckets (tables can be re-tagged in Phase C):

| Bucket | Count | Description |
|--------|------:|-------------|
| `other` | 84 | Demographics, HTN sub-study tables, medications, `dot_counting`, `cogstate`, etc. — many include **`subject_id`** without declaring FK |
| `instrument_raw_scored` | 55 | `*_raw`, `*_scored` pattern |
| `core_candidate` | 10 | `subjects`, `subjects2`, `call_log`, `cenc_*`, `biometrics`, `blinding_questionnaire`, `htn_subjects*`, `subject_binders_inventory` |
| `auth_admin` | 7 | `auth_*`, `admin_users` |
| `noise_framework` | 7 | `django_*`, `schema_migrations`, `ar_internal_metadata`, `active_admin_comments`, … |
| `dimension` | 6 | `_sex`, `_race`, `_education_level`, … |

**FK discipline:** only **16** foreign keys in `dvbic_research.public`; **three** reference `subjects` (`dot_counting`, `unstructured_task`, `verbal_fluency`). Most instrument rows use **`subject_id`** columns **without** FK constraints — ETL must still join on `subjects.id` / `cencsubjectid` logic carefully.

### 3.1 `dvbic_research.subjects` (core)

| Column | Type | Notes for RECRUIT `subjects` |
|--------|------|------------------------------|
| `id` | `bigint` PK | DVbic surrogate; **654 / 657** rows populated (snapshot). |
| `first_name`, `middle_name`, `last_name` | varchar | Direct map |
| `date_of_birth` | `date` | Map to `date_of_birth` |
| `sex`, `race` | `bigint` | Likely FK to `_sex` / `_race` dimension tables — map to RECRUIT strings |
| `ssn` | `varchar(11)` | **654 / 657** non-empty — candidate for **future** strict match to `arc` **if** `arc.ss_num` can be normalized to same format (TBD; not proven on snapshot). |
| `death_date`, `county`, `zip` | | Map directly |
| `created_by` | `varchar(50)` | Not a FK to `auth_user` — may need string→`users.id` mapping or migration user |

### 3.2 `cenc_subject_ids`

Single column **`cencsubjectid`** (PK). Likely the **canonical research ID** linking CENC instrument rows (`subject_id` often `integer` in `cenc_*` tables) — confirm in Phase C when wiring `assessments`.

---

## 4. Cross-system merge key analysis (`arc` ↔ `dvbic_research`)

| Candidate | `arc` | `dvbic_research` | Verdict on snapshot |
|-----------|--------|------------------|----------------------|
| Integer subject PK | `subj_list.grid` | `subjects.id` | **Different namespaces** — no shared surrogate. |
| `mrec_num` vs ? | varchar, sparse | no column with same name on `subjects` | **No direct join.** |
| SSN | `ss_num` **integer**, all rows | `ssn` **varchar**, 654/657 | **Type mismatch**; needs **normalization + policy** before any exact match rule; treat as **TBD**, not auto-enabled. |
| Name + DOB | `f_name`, `l_name`, `dob` | `first_name`, `last_name`, `date_of_birth` | **Fuzzy only** — excluded from pass‑1 auto-merge per plan. |

**Phase A conclusion (strict auto-merge key):** **No safe exact cross-system key identified** from schema and quick null stats alone. Keep **empty allowlist** until production backup analysis or a **delivered crosswalk file** (e.g. CSV of `grid` ↔ `subjects.id`) exists. Document any crosswalk in `audit_logs` + `legacy_id_map`.

---

## 5. Canonical source recommendation (when both systems overlap)

| RECRUIT concept | Suggested canonical source | Rationale |
|-----------------|----------------------------|-----------|
| **Study / protocol** | **`arc.study_desc`** for arc-backed work | Explicit study dimension + dates + investigator string. |
| **Study / protocol** (DVbic cohort) | **`dvbic_research.studies`** | **19** rows on snapshot; PK `id` bigint; `irb_number`, `description`, `start_date`/`end_date`, `investigator` varchar; referenced by `dot_counting`, `verbal_fluency`, `unstructured_task` (`study_id`). Map to RECRUIT `studies` with disambiguated `name` (e.g. prefix `dvbic-{id}-`). |
| **Subject (arc path)** | `arc.subj_list` | Rich enrollment via `study_list`; visits via `proc_list`. |
| **Subject (DVbic path)** | `dvbic_research.subjects` | 657-row core table; instruments keyed by `subject_id` / variants. |
| **Visit / encounter (arc)** | `arc.proc_list` | Clear FK spine. |
| **Visit / encounter (DVbic)** | **Per-table** `subject_id` (+ optional date columns) | No unified `proc_list` equivalent; `assessment_date` may come from row timestamps or instrument-specific date fields (per-table Phase C). |

---

## 6. Column mapping — `arc` → RECRUIT (initial)

### 6.1 `auth_user` → `users`

| Legacy (`arc.auth_user`) | RECruit `users` | Transform |
|--------------------------|-----------------|-----------|
| `username` or `email` | `email` | Prefer `email` if populated; else synthesize unique email from `username` |
| `password` | `hashed_password` | Only if hash algorithm compatible; else force reset / placeholder |
| `first_name` + `last_name` | `full_name` | Concatenate |
| — | `role` | Default `researcher` or map from `is_staff` / `is_superuser` |
| `is_active` | `is_active` | |

### 6.2 `arc.study_desc` → `studies`

| Legacy | Recruit | Transform |
|--------|---------|-----------|
| `descr` | `name` | Must satisfy **unique** `studies.name` — prefix with `arc-{code}-` if collision risk |
| `note` | `description` | |
| `startdate`, `enddate` | `start_date`, `end_date` | `timestamp` → `date` truncation |
| `investigator` | `principal_investigator_id` | Match string to migrated `users` or null + manual |
| `status` | `status` | Integer → string enum mapping TBD |

### 6.3 `dvbic_research.studies` → `studies`

| Legacy | Recruit | Transform |
|--------|---------|-----------|
| `id` | — | `legacy_id_map` |
| `irb_number` + `description` / `note` | `name` | Build unique `name` (e.g. `dvbic-study-{id}` or `IRB-{irb_number}` if unique) |
| `note` | `description` | |
| `start_date`, `end_date` | same | |
| `investigator` | `principal_investigator_id` | Resolve varchar → `users` or null |
| `status` | `status` | bigint → string TBD |

### 6.4 `subj_list` → `subjects`

| Legacy | Recruit | Transform |
|--------|---------|-----------|
| `f_name` | `first_name` | |
| — | `middle_name` | Often null in arc |
| `l_name` | `last_name` | |
| `dob` | `date_of_birth` | timestamptz → date (UTC date) |
| `sex` | `sex` | int → `male`/`female`/other via small lookup table TBD |
| `race`, `ethnicity`, `race_preomb` | `race`, `ethnicity` | int codes → FDA string categories TBD |
| `ss_num` | `ssn` | Format as zero-padded string or null if unknown semantics |
| `note` | — | Consider `session_notes` or append to migration audit only (PHI) |
| `grid` | — | Store in **`legacy_id_map`** + optionally inside first assessment `data` |

### 6.5 `study_list` → `subject_study`

| Legacy | Recruit |
|--------|---------|
| `grid` | Resolve to `subjects.id` via map |
| `study_code` | Resolve to `studies.id` via map |
| `study_entry_date` | Not on M2M — could set study `enrollment` notes or extend schema later |

### 6.6 `proc_list` + instrument tables → `assessments`

| Legacy | Recruit | Transform |
|--------|---------|-----------|
| `grid` | `subject_id` | Via map |
| `study_code` | `study_id` | Via map (nullable if orphan) |
| `proc_date` or `proc_starttime` | `assessment_date`, `assessment_time` | |
| `proc_code` + `proc_desc.descr` | `assessment_type` | e.g. slugify `descr`; ensure row exists in `assessment_types` |
| Row from linked instrument table | `data` | JSON column subset or full row JSON |
| `proc_list.comment` | `notes` or `session_notes` | Policy choice |

### 6.7 `dvbic_research.subjects` → `subjects`

Direct column map where types align; resolve `sex`/`race` bigint via `_sex` / `_race` lookup; map `created_by` varchar to `users` or migration user.

### 6.8 Instrument tables (`dvbic_research.*`)

For each table with `subject_id` / `cencsubjectid`:

| Legacy | Recruit |
|--------|---------|
| `subject_id` | `subject_id` via map from `subjects.id` |
| date column (varies) | `assessment_date` |
| remaining columns | `assessment_type` = table name (or mapped label); `data` = JSON |

---

## 7. Entity resolution rules (draft for ETL)

1. **Users:** Migrate Django `auth_user` from each DB separately with disambiguated `email` if usernames collide across `arc` vs `dvbic_research`.
2. **Studies:** Migrate **`arc.study_desc`** and **`dvbic_research.studies`** (separate name-spacing to avoid unique collisions on `studies.name`). Link DVbic instruments that have `study_id` FK to the migrated DVbic study rows.
3. **Subjects — pass 1:** Insert **one RECRUIT `subjects` row per legacy row** (`subj_list` row, `dvbic.subjects` row) with `legacy_id_map` entries; **no cross-system auto-merge** until strict key or crosswalk exists.
4. **Subject merge (explicit):** When operator supplies crosswalk or in-app merge, collapse rows, rewrite `legacy_id_map`, re-point `assessments.subject_id`, write **`audit_logs`**.
5. **Assessments:** Prefer **`proc_list`**-driven order for `arc`; for DVbic, per instrument table batches ordered by subject and date column if present.
6. **Session notes:** Map free-text fields (`proc_list.comment`, `subj_list.note`, `study_list.note`, DVbic `call_log` if applicable) to `session_notes` with `session_date` from parent row or import date (document choice in audit).

---

## 8. Deliverables checklist (Phase A)

| Deliverable | Location / status |
|-------------|-------------------|
| Legacy table → RECRUIT mapping | **§6** (this doc); expand per instrument in Phase C |
| Entity resolution rules | **§7** |
| PK / natural keys | **§2.3**, **§3** |
| `dvbic_research` table classification | **§3** (+ SQL heuristic; refine “`other`” in Phase C) |
| FK lists | **`arc` §2.2**; **`dvbic` Appendix A** (16 FKs) — sparse graph; most `subject_id` links are **not** enforced by FK |
| Strict merge key | **§4** — **none enabled** until production analysis or crosswalk |
| Canonical DB per entity | **§5** |

---

## 9. Recommended next steps (Phase B / C)

1. Add Alembic migration for **`legacy_id_map`** (+ optional **`migration_events`**) on RECRUIT.
2. Implement **`subjects` pass‑1** import from `arc.subj_list` and `dvbic_research.subjects` with maps only.
3. Pick **one vertical slice** (e.g. one `study_desc.code` + one DVbic cohort) for end-to-end `assessments` JSON proof.
4. Re-run **§4** null/overlap statistics on **production backup**.

---

## Appendix A — `dvbic_research.public` foreign keys (all 16)

| from_table | from_col | to_table | to_col |
|------------|----------|----------|--------|
| `auth_group_permissions` | `permission_id` | `auth_permission` | `id` |
| `auth_group_permissions` | `group_id` | `auth_group` | `id` |
| `auth_permission` | `content_type_id` | `django_content_type` | `id` |
| `auth_user_groups` | `group_id` | `auth_group` | `id` |
| `auth_user_groups` | `user_id` | `auth_user` | `id` |
| `auth_user_user_permissions` | `permission_id` | `auth_permission` | `id` |
| `auth_user_user_permissions` | `user_id` | `auth_user` | `id` |
| `django_admin_log` | `content_type_id` | `django_content_type` | `id` |
| `django_admin_log` | `user_id` | `auth_user` | `id` |
| `dot_counting` | `study_id` | **`studies`** | `id` |
| `dot_counting` | `subject_id` | **`subjects`** | `id` |
| `polls_choice` | `question_id` | `polls_question` | `id` |
| `unstructured_task` | `study_id` | **`studies`** | `id` |
| `unstructured_task` | `subject_id` | **`subjects`** | `id` |
| `verbal_fluency` | `study_id` | **`studies`** | `id` |
| `verbal_fluency` | `subject_id` | **`subjects`** | `id` |

---

## 10. Revision history

| Date | Notes |
|------|--------|
| 2026-05-07 | Initial Phase A discovery from `recruit_postgres_snapshot` (`arc`, `dvbic_research`). |
