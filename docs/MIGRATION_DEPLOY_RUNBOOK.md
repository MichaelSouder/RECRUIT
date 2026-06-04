# Legacy migration — production deploy runbook

**Audience:** operators running `migrations_cli` against a **target** RECRUIT PostgreSQL database (staging or production).  
**Companion:** [CURRENT_STATUS.md](./CURRENT_STATUS.md), [MIGRATION_PROGRESS_AND_STRUCTURE.md](./MIGRATION_PROGRESS_AND_STRUCTURE.md).

---

## 1. Preconditions

- **RECRUIT app schema** is at Alembic head (includes `legacy_id_map`, `migration_events`, migration system user): `alembic upgrade head` from `src/backend/`.
- **Network** from the operator host to **target** `DATABASE_URL` and, for ETL, read access to legacy URLs (`LEGACY_ARC_DATABASE_URL`, `LEGACY_DVBIC_RESEARCH_DATABASE_URL`) if you run imports from that host.
- **Python** environment with `src/backend/requirements.txt` installed (includes `psycopg2-binary`).

---

## 2. Backup (mandatory before writes)

Take a logical dump of the **target** RECRUIT database (adjust URL and path):

```bash
pg_dump "$DATABASE_URL" --format=custom --file="recruit_pre_migration_$(date -u +%Y%m%dT%H%MZ).dump"
```

Store the file in your org’s backup location. **No bulk import without a restore-tested backup.**

---

## 3. Environment

```bash
export DATABASE_URL='postgresql://USER:PASS@HOST:5432/recruit_db'
export LEGACY_ARC_DATABASE_URL='postgresql://.../arc'
export LEGACY_DVBIC_RESEARCH_DATABASE_URL='postgresql://.../dvbic_research'
export MIGRATION_BATCH_ID='2026-05-07T1400Z-prod-cutover'   # change per run / phase
cd src/backend
```

---

## 4. Gates (read-only)

```bash
python -m migrations_cli preflight
python -m migrations_cli validate
python -m migrations_cli deploy-check
```

`deploy-check` runs `validate` and prints **warnings**, including an estimate of **duplicate `arc-proc-*` visit rows** (same `data.proc_num`) if any exist from older importer runs.

---

## 5. Import order (fresh target DB)

Follow **§3** of [MIGRATION_PROGRESS_AND_STRUCTURE.md](./MIGRATION_PROGRESS_AND_STRUCTURE.md) exactly. Short version:

1. Arc: auth users → studies → subjects → subject-study → assessment types → proc list → arc instruments → **studyproc list**  
2. DVbic: studies → subjects → **subjects2** → **subject-study inference** → **session notes** → **instrument tables**  
3. Optional: `import-arc-user-study` (only if `arc.study_acl.usr` values exist in `arc.auth_user`; snapshot often has **no** overlap)

Use `--dry-run` on a disposable clone first if desired:

```bash
python -m migrations_cli --dry-run import-arc-auth-users
```

---

## 6. Post-load cleanup (if `deploy-check` reported duplicate arc visits)

After backup, on the **target** DB:

```bash
python -m migrations_cli prune-duplicate-arc-proc-assessments   # dry-run: counts only
python -m migrations_cli prune-duplicate-arc-proc-assessments --apply
python -m migrations_cli deploy-check   # duplicate estimate should be 0
```

The pruner keeps the assessment id that **`legacy_id_map`** already points to for `arc` / `proc_list` / `{proc_num}` when possible; otherwise it keeps the lowest id and updates the map.

---

## 7. Audit trail (go-live / phase sign-off)

Append a single **`audit_logs`** row attributed to the migration system user:

```bash
python -m migrations_cli record-migration-audit "Phase N complete: arc + dvbic bulk load applied."
```

Use a meaningful sentence; optional context includes `MIGRATION_BATCH_ID` from the environment.

---

## 8. What this runbook does **not** cover

- **Cross-system subject merge** (arc vs DVbic same person): requires business rules, crosswalk, and usually manual or reviewed tooling — **not** automatic in `migrations_cli`.
- **Application deploy** (Docker/K8s/env secrets, TLS, app `DATABASE_URL`): use [DEPLOY_PODMAN.md](./DEPLOY_PODMAN.md) / [AIRGAP_DEPLOY.md](./AIRGAP_DEPLOY.md) / your platform docs.
- **Rotating** the migration system user password (see Alembic `b3e8a1c92d40` docstring) before any shared environment.

---

## 9. Revision

| Date | Change |
|------|--------|
| 2026-05-07 | Initial runbook: backup, env, `deploy-check`, import order pointer, prune + audit commands. |
