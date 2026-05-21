"""First-party ETL: `arc` → RECRUIT (psycopg2, transactional)."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import psycopg2

from migrations_cli.config import MigrationConfig

log = logging.getLogger("migrations_cli")

# Placeholder bcrypt for imported Django users. Plaintext is not recorded; use
# ``migrations_cli set-user-password`` or a production password-reset flow.
_IMPORTED_USER_PASSWORD_HASH = (
    "$2b$12$dFv.Fvt7hU3yHMzHZlLkLexx9KQIv1cATPxhbvR4/CKiYQBjk5iqi"
)


_MIGRATION_SYSTEM_EMAIL = "migration-system@recruit.internal"


def _migration_system_user_id(r_cur: Any) -> int:
    r_cur.execute("SELECT id FROM users WHERE email = %s", (_MIGRATION_SYSTEM_EMAIL,))
    row = r_cur.fetchone()
    if not row:
        raise SystemExit(
            f"RECRUIT user {_MIGRATION_SYSTEM_EMAIL!r} is missing. "
            "Run Alembic through revision b3e8a1c92d40 before ETL."
        )
    return int(row[0])


def _arc_sex_label(code: int | None) -> str | None:
    """Heuristic arc `subj_list.sex` (snapshot: 1 dominant, 2 rare)."""
    if code is None:
        return None
    if code == 1:
        return "male"
    if code == 2:
        return "female"
    return f"legacy-sex-{code}"


def _arc_int_field(prefix: str, value: int | None) -> str | None:
    if value is None:
        return None
    return f"{prefix}-{value}"


def _require_batch(cfg: MigrationConfig) -> str:
    if not cfg.migration_batch_id:
        raise SystemExit(
            "MIGRATION_BATCH_ID is required for import commands (unless --dry-run).\n"
            "  export MIGRATION_BATCH_ID=2026-05-07T1200Z-my-run"
        )
    return cfg.migration_batch_id


def import_arc_auth_users(cfg: MigrationConfig) -> int:
    batch = _require_batch(cfg) if not cfg.dry_run else (cfg.migration_batch_id or "dry-run")
    if not cfg.legacy_arc_url:
        raise SystemExit("LEGACY_ARC_DATABASE_URL is required.")

    arc = psycopg2.connect(cfg.legacy_arc_url)
    recruit = psycopg2.connect(cfg.database_url)
    try:
        arc_cur = arc.cursor()
        arc_cur.execute(
            """
            SELECT id, username, email, first_name, last_name, is_staff, is_superuser, is_active,
                   date_joined
            FROM auth_user
            ORDER BY id
            """
        )
        rows = arc_cur.fetchall()
        log.info("import_arc_auth_users.fetched %s", json.dumps({"count": len(rows)}))

        r_cur = recruit.cursor()
        inserted = 0
        skipped = 0
        mapped = 0

        for (
            legacy_id,
            username,
            email,
            first_name,
            last_name,
            is_staff,
            is_superuser,
            is_active,
            date_joined,
        ) in rows:
            email_clean = (email or "").strip() or f"arc-authuser-{legacy_id}@imported.local"
            r_cur.execute("SELECT id FROM users WHERE email = %s", (email_clean,))
            existing = r_cur.fetchone()
            if existing:
                recruit_id = existing[0]
                skipped += 1
            else:
                if cfg.dry_run:
                    log.info(
                        "import_arc_auth_users.would_insert %s",
                        json.dumps({"legacy_id": legacy_id, "email": email_clean}),
                    )
                    recruit_id = None
                else:
                    role = (
                        "admin"
                        if is_superuser
                        else ("researcher" if is_staff else "viewer")
                    )
                    full_name = f"{first_name or ''} {last_name or ''}".strip() or username
                    r_cur.execute(
                        """
                        INSERT INTO users (
                            email, hashed_password, full_name, location, phone, piv_certificate_id,
                            is_active, is_superuser, role, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, NULL, NULL, NULL,
                            %s, %s, %s, COALESCE(%s, NOW() AT TIME ZONE 'UTC'), COALESCE(%s, NOW() AT TIME ZONE 'UTC')
                        )
                        RETURNING id
                        """,
                        (
                            email_clean,
                            _IMPORTED_USER_PASSWORD_HASH,
                            full_name,
                            is_active,
                            is_superuser,
                            role,
                            date_joined,
                            date_joined,
                        ),
                    )
                    recruit_id = r_cur.fetchone()[0]
                    inserted += 1

            if not cfg.dry_run and recruit_id is not None:
                r_cur.execute(
                    """
                    INSERT INTO legacy_id_map (
                        source_system, source_table, source_pk, target_table, target_pk, batch_id, imported_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, NOW() AT TIME ZONE 'UTC')
                    ON CONFLICT (source_system, source_table, source_pk) DO NOTHING
                    """,
                    ("arc", "auth_user", str(legacy_id), "users", recruit_id, batch),
                )
                if r_cur.rowcount:
                    mapped += 1

        if cfg.dry_run:
            recruit.rollback()
            log.info(
                "import_arc_auth_users.dry_run_done %s",
                json.dumps({"would_process": len(rows), "skipped_existing_email": skipped}),
            )
        else:
            recruit.commit()
            log.info(
                "import_arc_auth_users.done %s",
                json.dumps({"inserted": inserted, "skipped": skipped, "legacy_map_rows": mapped}),
            )
        return 0
    except Exception:
        recruit.rollback()
        raise
    finally:
        arc.close()
        recruit.close()


def import_arc_studies(cfg: MigrationConfig) -> int:
    batch = _require_batch(cfg) if not cfg.dry_run else (cfg.migration_batch_id or "dry-run")
    if not cfg.legacy_arc_url:
        raise SystemExit("LEGACY_ARC_DATABASE_URL is required.")

    arc = psycopg2.connect(cfg.legacy_arc_url)
    recruit = psycopg2.connect(cfg.database_url)
    try:
        arc_cur = arc.cursor()
        arc_cur.execute(
            """
            SELECT code, descr, note, startdate, enddate, status
            FROM study_desc
            ORDER BY code
            """
        )
        rows = arc_cur.fetchall()
        log.info("import_arc_studies.fetched %s", json.dumps({"count": len(rows)}))

        r_cur = recruit.cursor()
        inserted = 0
        mapped = 0

        for code, descr, note, startdate, enddate, status in rows:
            name = f"arc-study-{code}"
            description_parts = [p for p in (descr, note) if p]
            description = "\n\n".join(description_parts) if description_parts else None
            start_d = startdate.date() if startdate else None
            end_d = enddate.date() if enddate else None
            # study_desc.status is an opaque legacy code; keep active until mapped in Phase C.
            status_s = "active"

            r_cur.execute("SELECT id FROM studies WHERE name = %s", (name,))
            row = r_cur.fetchone()
            if row:
                study_id = row[0]
            elif cfg.dry_run:
                log.info(
                    "import_arc_studies.would_insert %s",
                    json.dumps({"code": code, "name": name}),
                )
                study_id = None
            else:
                r_cur.execute(
                    """
                    INSERT INTO studies (
                        name, description, start_date, end_date, status,
                        principal_investigator_id, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, NULL, NOW() AT TIME ZONE 'UTC', NOW() AT TIME ZONE 'UTC'
                    )
                    RETURNING id
                    """,
                    (name, description, start_d, end_d, status_s),
                )
                study_id = r_cur.fetchone()[0]
                inserted += 1

            if not cfg.dry_run and study_id is not None:
                r_cur.execute(
                    """
                    INSERT INTO legacy_id_map (
                        source_system, source_table, source_pk, target_table, target_pk, batch_id, imported_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, NOW() AT TIME ZONE 'UTC')
                    ON CONFLICT (source_system, source_table, source_pk) DO NOTHING
                    """,
                    ("arc", "study_desc", str(code), "studies", study_id, batch),
                )
                if r_cur.rowcount:
                    mapped += 1

        if cfg.dry_run:
            recruit.rollback()
            log.info(
                "import_arc_studies.dry_run_done %s",
                json.dumps({"would_process": len(rows)}),
            )
        else:
            recruit.commit()
            log.info(
                "import_arc_studies.done %s",
                json.dumps({"inserted": inserted, "legacy_map_rows": mapped}),
            )
        return 0
    except Exception:
        recruit.rollback()
        raise
    finally:
        arc.close()
        recruit.close()


def import_arc_subjects(cfg: MigrationConfig) -> int:
    """Import ``arc.subj_list`` → ``subjects`` + ``legacy_id_map``."""
    batch = _require_batch(cfg) if not cfg.dry_run else (cfg.migration_batch_id or "dry-run")
    if not cfg.legacy_arc_url:
        raise SystemExit("LEGACY_ARC_DATABASE_URL is required.")

    arc = psycopg2.connect(cfg.legacy_arc_url)
    recruit = psycopg2.connect(cfg.database_url)
    try:
        arc_cur = arc.cursor()
        arc_cur.execute(
            """
            SELECT grid, l_name, f_name, dob, sex, ss_num, research_status, race, ethnicity
            FROM subj_list
            ORDER BY grid
            """
        )
        rows = arc_cur.fetchall()
        log.info("import_arc_subjects.fetched %s", json.dumps({"count": len(rows)}))

        r_cur = recruit.cursor()
        mig_uid = _migration_system_user_id(r_cur)
        inserted = 0
        skipped_mapped = 0
        mapped = 0

        for (
            grid,
            l_name,
            f_name,
            dob,
            sex,
            ss_num,
            research_status,
            race,
            ethnicity,
        ) in rows:
            r_cur.execute(
                """
                SELECT target_pk FROM legacy_id_map
                WHERE source_system = %s AND source_table = %s AND source_pk = %s
                  AND target_table = 'subjects'
                """,
                ("arc", "subj_list", str(grid)),
            )
            existing_map = r_cur.fetchone()
            if existing_map:
                skipped_mapped += 1
                subject_id = existing_map[0]
            elif cfg.dry_run:
                subject_id = None
            else:
                dob_d = dob.date() if dob else None
                ssn_s = str(ss_num) if ss_num is not None else None
                enroll = str(research_status) if research_status is not None else None
                r_cur.execute(
                    """
                    INSERT INTO subjects (
                        first_name, middle_name, last_name, date_of_birth, sex, ssn,
                        race, ethnicity, death_date, county, zip, enrollment_status,
                        created_by, created_at, updated_at
                    ) VALUES (
                        %s, NULL, %s, %s, %s, %s,
                        %s, %s, NULL, NULL, NULL, %s,
                        %s, NOW() AT TIME ZONE 'UTC', NOW() AT TIME ZONE 'UTC'
                    )
                    RETURNING id
                    """,
                    (
                        (f_name or "").strip(),
                        (l_name or "").strip(),
                        dob_d,
                        _arc_sex_label(sex),
                        ssn_s,
                        _arc_int_field("arc-race", race),
                        _arc_int_field("arc-ethnicity", ethnicity),
                        enroll,
                        mig_uid,
                    ),
                )
                subject_id = r_cur.fetchone()[0]
                inserted += 1

            if not cfg.dry_run and subject_id is not None:
                r_cur.execute(
                    """
                    INSERT INTO legacy_id_map (
                        source_system, source_table, source_pk, target_table, target_pk, batch_id, imported_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, NOW() AT TIME ZONE 'UTC')
                    ON CONFLICT (source_system, source_table, source_pk) DO NOTHING
                    """,
                    ("arc", "subj_list", str(grid), "subjects", subject_id, batch),
                )
                if r_cur.rowcount:
                    mapped += 1

        if cfg.dry_run:
            recruit.rollback()
            log.info(
                "import_arc_subjects.dry_run_done %s",
                json.dumps(
                    {
                        "would_process": len(rows),
                        "already_mapped": skipped_mapped,
                        "would_insert": len(rows) - skipped_mapped,
                    }
                ),
            )
        else:
            recruit.commit()
            log.info(
                "import_arc_subjects.done %s",
                json.dumps(
                    {
                        "inserted": inserted,
                        "already_mapped_skipped": skipped_mapped,
                        "legacy_map_rows": mapped,
                    }
                ),
            )
        return 0
    except Exception:
        recruit.rollback()
        raise
    finally:
        arc.close()
        recruit.close()


def import_arc_subject_study(cfg: MigrationConfig) -> int:
    """Import ``arc.study_list`` → ``subject_study`` (requires prior arc subject + study maps)."""
    if not cfg.legacy_arc_url:
        raise SystemExit("LEGACY_ARC_DATABASE_URL is required.")

    arc = psycopg2.connect(cfg.legacy_arc_url)
    recruit = psycopg2.connect(cfg.database_url)
    try:
        arc_cur = arc.cursor()
        arc_cur.execute(
            """
            SELECT "index", grid, study_code
            FROM study_list
            ORDER BY "index"
            """
        )
        rows = arc_cur.fetchall()
        log.info("import_arc_subject_study.fetched %s", json.dumps({"count": len(rows)}))

        r_cur = recruit.cursor()
        inserted = 0
        skipped_exists = 0
        missing_subject = 0
        missing_study = 0
        would_link = 0

        for _idx, grid, study_code in rows:
            r_cur.execute(
                """
                SELECT target_pk FROM legacy_id_map
                WHERE source_system = %s AND source_table = %s AND source_pk = %s
                  AND target_table = 'subjects'
                """,
                ("arc", "subj_list", str(grid)),
            )
            srow = r_cur.fetchone()
            if not srow:
                missing_subject += 1
                continue
            subject_id = srow[0]

            r_cur.execute(
                """
                SELECT target_pk FROM legacy_id_map
                WHERE source_system = %s AND source_table = %s AND source_pk = %s
                  AND target_table = 'studies'
                """,
                ("arc", "study_desc", str(study_code)),
            )
            trow = r_cur.fetchone()
            if not trow:
                missing_study += 1
                continue
            study_id = trow[0]

            if cfg.dry_run:
                would_link += 1
                continue

            r_cur.execute(
                """
                INSERT INTO subject_study (subject_id, study_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
                """,
                (subject_id, study_id),
            )
            if r_cur.rowcount:
                inserted += 1
            else:
                skipped_exists += 1

        if cfg.dry_run:
            recruit.rollback()
            log.info(
                "import_arc_subject_study.dry_run_done %s",
                json.dumps(
                    {
                        "would_process": len(rows),
                        "would_link": would_link,
                        "missing_subject_map": missing_subject,
                        "missing_study_map": missing_study,
                    }
                ),
            )
        else:
            recruit.commit()
            log.info(
                "import_arc_subject_study.done %s",
                json.dumps(
                    {
                        "inserted": inserted,
                        "skipped_duplicate": skipped_exists,
                        "missing_subject_map": missing_subject,
                        "missing_study_map": missing_study,
                    }
                ),
            )
        return 0
    except Exception:
        recruit.rollback()
        raise
    finally:
        arc.close()
        recruit.close()


def import_arc_studyproc_list(cfg: MigrationConfig) -> int:
    """Import ``arc.studyproc_list`` → RECRUIT ``study_procedures`` (study↔procedure matrix, idempotent)."""
    batch = _require_batch(cfg) if not cfg.dry_run else (cfg.migration_batch_id or "dry-run")
    if not cfg.legacy_arc_url:
        raise SystemExit("LEGACY_ARC_DATABASE_URL is required.")

    arc = psycopg2.connect(cfg.legacy_arc_url)
    recruit = psycopg2.connect(cfg.database_url)
    try:
        arc_cur = arc.cursor()
        arc_cur.execute(
            """
            SELECT "index", proc_code, study_code, orderindex, mod_date, mod_person
            FROM studyproc_list
            ORDER BY "index"
            """
        )
        rows = arc_cur.fetchall()
        log.info("import_arc_studyproc_list.fetched %s", json.dumps({"count": len(rows)}))

        r_cur = recruit.cursor()
        r_cur.execute(
            """
            SELECT source_pk, target_pk FROM legacy_id_map
            WHERE source_system = %s AND source_table = %s AND target_table = %s
            """,
            ("arc", "study_desc", "studies"),
        )
        code_to_study = {str(r[0]): int(r[1]) for r in r_cur.fetchall()}

        inserted = 0
        skipped = 0
        missing_study = 0
        map_rows = 0

        for index, proc_code, study_code, orderindex, mod_date, mod_person in rows:
            if study_code is None:
                missing_study += 1
                continue
            study_key = str(int(study_code)) if isinstance(study_code, (int, float)) else str(study_code).strip()
            study_id = code_to_study.get(study_key)
            if not study_id:
                missing_study += 1
                continue
            pc = (
                str(int(proc_code))
                if isinstance(proc_code, (int, float)) and proc_code is not None
                else str(proc_code).strip()
            )
            if not pc:
                skipped += 1
                continue

            payload = {
                "legacy_index": index,
                "proc_code": proc_code,
                "study_code": study_code,
                "orderindex": orderindex,
                "mod_date": str(mod_date) if mod_date is not None else None,
                "mod_person": mod_person,
            }
            source_pk = str(index) if index is not None else None
            if source_pk is None:
                skipped += 1
                continue

            if cfg.dry_run:
                inserted += 1
                continue

            r_cur.execute(
                """
                INSERT INTO study_procedures (
                    study_id, proc_code, sort_order, legacy_index, data, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s::jsonb, NOW() AT TIME ZONE 'UTC', NOW() AT TIME ZONE 'UTC')
                ON CONFLICT (study_id, proc_code) DO NOTHING
                RETURNING id
                """,
                (study_id, pc, orderindex, int(index) if index is not None else None, json.dumps(payload, default=str)),
            )
            ret = r_cur.fetchone()
            if ret:
                sp_id = int(ret[0])
                inserted += 1
            else:
                r_cur.execute(
                    "SELECT id FROM study_procedures WHERE study_id = %s AND proc_code = %s",
                    (study_id, pc),
                )
                r2 = r_cur.fetchone()
                if not r2:
                    skipped += 1
                    continue
                sp_id = int(r2[0])
                skipped += 1

            r_cur.execute(
                """
                INSERT INTO legacy_id_map (
                    source_system, source_table, source_pk, target_table, target_pk, batch_id, imported_at
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW() AT TIME ZONE 'UTC')
                ON CONFLICT (source_system, source_table, source_pk) DO NOTHING
                """,
                ("arc", "studyproc_list", source_pk, "study_procedures", sp_id, batch),
            )
            if r_cur.rowcount:
                map_rows += 1

        if cfg.dry_run:
            recruit.rollback()
            log.info(
                "import_arc_studyproc_list.dry_run_done %s",
                json.dumps(
                    {
                        "would_process": len(rows),
                        "would_insert": inserted,
                        "missing_study_map": missing_study,
                        "skipped": skipped,
                    }
                ),
            )
        else:
            recruit.commit()
            log.info(
                "import_arc_studyproc_list.done %s",
                json.dumps(
                    {
                        "inserted": inserted,
                        "skipped_duplicate_or_conflict": skipped,
                        "missing_study_map": missing_study,
                        "legacy_id_map_rows": map_rows,
                    }
                ),
            )
        return 0
    except Exception:
        recruit.rollback()
        raise
    finally:
        arc.close()
        recruit.close()


_STUDY_ACL_USER_MAP_TABLE = "study_acl_user"


def _study_acl_stub_email(ulc: str) -> str:
    safe = re.sub(r"[^a-z0-9._+-]+", "-", ulc.strip().lower())[:80] or "unknown"
    return f"arc-acl-{safe}@imported.local"


def import_arc_study_acl_users(cfg: MigrationConfig) -> int:
    """Create stub RECRUIT users for ``study_acl.usr`` values not present in ``arc.auth_user``.

    Run before ``import-arc-user-study`` when ACL usernames do not overlap Django users.
    Maps ``arc`` / ``study_acl_user`` / ``{username}`` → ``users``.
    """
    batch = _require_batch(cfg) if not cfg.dry_run else (cfg.migration_batch_id or "dry-run")
    if not cfg.legacy_arc_url:
        raise SystemExit("LEGACY_ARC_DATABASE_URL is required.")

    arc = psycopg2.connect(cfg.legacy_arc_url)
    recruit = psycopg2.connect(cfg.database_url)
    try:
        arc_cur = arc.cursor()
        arc_cur.execute(
            """
            SELECT DISTINCT lower(trim(usr)) AS u
            FROM study_acl
            WHERE usr IS NOT NULL AND trim(usr) <> ''
            """
        )
        acl_names = [str(r[0]) for r in arc_cur.fetchall() if r[0]]
        arc_cur.execute(
            "SELECT lower(trim(username)) FROM auth_user WHERE username IS NOT NULL"
        )
        auth_names = {str(r[0]) for r in arc_cur.fetchall() if r[0]}

        r_cur = recruit.cursor()
        inserted = 0
        mapped = 0
        skipped_auth_overlap = 0
        skipped_existing = 0

        for ulc in sorted(acl_names):
            if ulc in auth_names:
                skipped_auth_overlap += 1
                continue
            email = _study_acl_stub_email(ulc)
            r_cur.execute(
                """
                SELECT target_pk FROM legacy_id_map
                WHERE source_system = %s AND source_table = %s AND source_pk = %s
                  AND target_table = 'users'
                """,
                ("arc", _STUDY_ACL_USER_MAP_TABLE, ulc),
            )
            if r_cur.fetchone():
                skipped_existing += 1
                continue
            r_cur.execute("SELECT id FROM users WHERE lower(email) = lower(%s)", (email,))
            existing = r_cur.fetchone()
            if existing:
                recruit_id = int(existing[0])
            elif cfg.dry_run:
                inserted += 1
                recruit_id = None
            else:
                r_cur.execute(
                    """
                    INSERT INTO users (
                        email, hashed_password, full_name, location, phone, piv_certificate_id,
                        is_active, is_superuser, role, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, NULL, NULL, NULL,
                        false, false, 'viewer',
                        NOW() AT TIME ZONE 'UTC', NOW() AT TIME ZONE 'UTC'
                    )
                    RETURNING id
                    """,
                    (email, _IMPORTED_USER_PASSWORD_HASH, f"Arc ACL {ulc}"),
                )
                recruit_id = int(r_cur.fetchone()[0])
                inserted += 1

            if cfg.dry_run or recruit_id is None:
                continue
            r_cur.execute(
                """
                INSERT INTO legacy_id_map (
                    source_system, source_table, source_pk, target_table, target_pk, batch_id, imported_at
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW() AT TIME ZONE 'UTC')
                ON CONFLICT (source_system, source_table, source_pk) DO NOTHING
                """,
                ("arc", _STUDY_ACL_USER_MAP_TABLE, ulc, "users", recruit_id, batch),
            )
            if r_cur.rowcount:
                mapped += 1

        if cfg.dry_run:
            recruit.rollback()
            log.info(
                "import_arc_study_acl_users.dry_run_done %s",
                json.dumps(
                    {
                        "distinct_acl_usernames": len(acl_names),
                        "would_create_stub_users": inserted,
                        "skipped_overlap_auth_user": skipped_auth_overlap,
                        "skipped_already_mapped": skipped_existing,
                    }
                ),
            )
        else:
            recruit.commit()
            log.info(
                "import_arc_study_acl_users.done %s",
                json.dumps(
                    {
                        "inserted": inserted,
                        "legacy_map_rows": mapped,
                        "skipped_overlap_auth_user": skipped_auth_overlap,
                        "skipped_already_mapped": skipped_existing,
                    }
                ),
            )
        return 0
    except Exception:
        recruit.rollback()
        raise
    finally:
        arc.close()
        recruit.close()


def _resolve_arc_acl_user_id(
    r_cur: Any,
    ulc_s: str,
    *,
    uname_to_django_pk: dict[str, str],
    django_to_user: dict[str, int],
    acl_user_map: dict[str, int],
) -> int | None:
    django_pk = uname_to_django_pk.get(ulc_s)
    if django_pk is not None:
        uid = django_to_user.get(django_pk)
        if uid is not None:
            return uid
    uid = acl_user_map.get(ulc_s)
    if uid is not None:
        return uid
    r_cur.execute(
        "SELECT id FROM users WHERE lower(email) IN (lower(%s), lower(%s))",
        (f"{ulc_s}@umn.edu", _study_acl_stub_email(ulc_s)),
    )
    row = r_cur.fetchone()
    return int(row[0]) if row else None


def import_arc_user_study(cfg: MigrationConfig) -> int:
    """Import ``arc.study_acl`` → ``user_study``.

    Resolves ``usr`` via ``auth_user``, ``study_acl_user`` stub map (see ``import-arc-study-acl-users``),
    or ``{usr}@umn.edu`` / stub email on ``users``.
    """
    if not cfg.legacy_arc_url:
        raise SystemExit("LEGACY_ARC_DATABASE_URL is required.")

    arc = psycopg2.connect(cfg.legacy_arc_url)
    recruit = psycopg2.connect(cfg.database_url)
    try:
        arc_cur = arc.cursor()
        arc_cur.execute("SELECT id, lower(username) FROM auth_user WHERE username IS NOT NULL")
        uname_to_django_pk = {str(r[1]).strip(): str(r[0]) for r in arc_cur.fetchall() if r[1]}

        r_cur = recruit.cursor()
        r_cur.execute(
            """
            SELECT source_pk, target_pk FROM legacy_id_map
            WHERE source_system = %s AND source_table = %s AND target_table = %s
            """,
            ("arc", "auth_user", "users"),
        )
        django_to_user = {str(r[0]): int(r[1]) for r in r_cur.fetchall()}
        r_cur.execute(
            """
            SELECT source_pk, target_pk FROM legacy_id_map
            WHERE source_system = %s AND source_table = %s AND target_table = %s
            """,
            ("arc", _STUDY_ACL_USER_MAP_TABLE, "users"),
        )
        acl_user_map = {str(r[0]): int(r[1]) for r in r_cur.fetchall()}
        r_cur.execute(
            """
            SELECT source_pk, target_pk FROM legacy_id_map
            WHERE source_system = %s AND source_table = %s AND target_table = %s
            """,
            ("arc", "study_desc", "studies"),
        )
        code_to_study = {str(r[0]): int(r[1]) for r in r_cur.fetchall()}

        arc_cur.execute("SELECT entry, study, lower(usr) FROM study_acl WHERE usr IS NOT NULL")
        rows = arc_cur.fetchall()
        log.info("import_arc_user_study.fetched %s", json.dumps({"count": len(rows)}))

        inserted = 0
        skipped_dup = 0
        missing_user = 0
        missing_study = 0
        would_link = 0

        for _entry, study_code, ulc in rows:
            if not ulc:
                missing_user += 1
                continue
            ulc_s = str(ulc).strip()
            uid = _resolve_arc_acl_user_id(
                r_cur,
                ulc_s,
                uname_to_django_pk=uname_to_django_pk,
                django_to_user=django_to_user,
                acl_user_map=acl_user_map,
            )
            if uid is None:
                missing_user += 1
                continue
            sid = code_to_study.get(str(study_code))
            if sid is None:
                missing_study += 1
                continue
            if cfg.dry_run:
                would_link += 1
                continue
            r_cur.execute(
                """
                INSERT INTO user_study (user_id, study_id, study_role)
                VALUES (%s, %s, 'viewer')
                ON CONFLICT DO NOTHING
                """,
                (uid, sid),
            )
            if r_cur.rowcount:
                inserted += 1
            else:
                skipped_dup += 1

        if cfg.dry_run:
            recruit.rollback()
            log.info(
                "import_arc_user_study.dry_run_done %s",
                json.dumps(
                    {
                        "would_process": len(rows),
                        "would_link": would_link,
                        "missing_user_resolution": missing_user,
                        "missing_study_map": missing_study,
                    }
                ),
            )
        else:
            recruit.commit()
            log.info(
                "import_arc_user_study.done %s",
                json.dumps(
                    {
                        "inserted": inserted,
                        "skipped_duplicate": skipped_dup,
                        "missing_user_resolution": missing_user,
                        "missing_study_map": missing_study,
                    }
                ),
            )
        return 0
    except Exception:
        recruit.rollback()
        raise
    finally:
        arc.close()
        recruit.close()


def progress_summary(cfg: MigrationConfig) -> int:
    """Show RECRUIT row counts and latest legacy_id_map rows."""
    recruit = psycopg2.connect(cfg.database_url)
    try:
        cur = recruit.cursor()
        cur.execute(
            """
            SELECT relname, n_live_tup::bigint
            FROM pg_stat_user_tables
            WHERE schemaname = 'public'
              AND relname IN (
                'users','studies','subjects','assessments','assessment_types','subject_study',
                'user_study','session_notes',
                'legacy_id_map','migration_events'
              )
            ORDER BY relname
            """
        )
        print("=== RECRUIT table row estimates (pg_stat_user_tables) ===")
        for name, n in cur.fetchall():
            print(f"  {name:20} {int(n)}")

        cur.execute(
            """
            SELECT source_system, source_table, source_pk, target_table, target_pk, batch_id
            FROM legacy_id_map
            ORDER BY id DESC
            LIMIT 15
            """
        )
        print("\n=== Latest legacy_id_map (up to 15) ===")
        for r in cur.fetchall():
            print(f"  {r[0]:8} {r[1]:16} pk={r[2]:8} -> {r[3]:10} id={r[4]} batch={r[5]}")
        return 0
    finally:
        recruit.close()
