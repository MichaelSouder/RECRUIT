"""ETL: ``dvbic_research`` → RECRUIT (psycopg2, transactional)."""

from __future__ import annotations

import json
import logging
from datetime import date, datetime
from typing import Any

import psycopg2
from psycopg2 import sql

from migrations_cli.config import MigrationConfig
from migrations_cli.etl_arc import _migration_system_user_id, _require_batch

log = logging.getLogger("migrations_cli")

_DVBIC_SOURCE = "dvbic_research"


def import_dvbic_studies(cfg: MigrationConfig) -> int:
    batch = _require_batch(cfg) if not cfg.dry_run else (cfg.migration_batch_id or "dry-run")
    if not cfg.legacy_dvbic_research_url:
        raise SystemExit("LEGACY_DVBIC_RESEARCH_DATABASE_URL is required.")

    dvb = psycopg2.connect(cfg.legacy_dvbic_research_url)
    recruit = psycopg2.connect(cfg.database_url)
    try:
        d_cur = dvb.cursor()
        d_cur.execute(
            """
            SELECT id, irb_number, description, note, investigator, status, start_date, end_date
            FROM studies
            ORDER BY id
            """
        )
        rows = d_cur.fetchall()
        log.info("import_dvbic_studies.fetched %s", json.dumps({"count": len(rows)}))

        r_cur = recruit.cursor()
        inserted = 0
        mapped = 0

        for sid, irb, descr, note, investigator, _status, start_d, end_d in rows:
            name = f"dvbic-study-{sid}"
            parts = [p for p in (irb and f"IRB: {irb}", descr, note, investigator) if p]
            description = "\n\n".join(parts) if parts else None

            r_cur.execute("SELECT id FROM studies WHERE name = %s", (name,))
            row = r_cur.fetchone()
            if row:
                study_id = row[0]
            elif cfg.dry_run:
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
                    (name, description, start_d, end_d, "active"),
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
                    (_DVBIC_SOURCE, "studies", str(sid), "studies", study_id, batch),
                )
                if r_cur.rowcount:
                    mapped += 1

        if cfg.dry_run:
            recruit.rollback()
            log.info(
                "import_dvbic_studies.dry_run_done %s",
                json.dumps({"would_process": len(rows)}),
            )
        else:
            recruit.commit()
            log.info(
                "import_dvbic_studies.done %s",
                json.dumps({"inserted": inserted, "legacy_map_rows": mapped}),
            )
        return 0
    except Exception:
        recruit.rollback()
        raise
    finally:
        dvb.close()
        recruit.close()


def import_dvbic_subjects(cfg: MigrationConfig) -> int:
    batch = _require_batch(cfg) if not cfg.dry_run else (cfg.migration_batch_id or "dry-run")
    if not cfg.legacy_dvbic_research_url:
        raise SystemExit("LEGACY_DVBIC_RESEARCH_DATABASE_URL is required.")

    dvb = psycopg2.connect(cfg.legacy_dvbic_research_url)
    recruit = psycopg2.connect(cfg.database_url)
    try:
        d_cur = dvb.cursor()
        d_cur.execute(
            """
            SELECT s.id, s.first_name, s.middle_name, s.last_name, s.date_of_birth,
                   sx.name AS sex_label, s.ssn, r.name AS race_label,
                   s.death_date, s.county, s.zip
            FROM subjects s
            LEFT JOIN _sex sx ON s.sex = sx.id
            LEFT JOIN _race r ON s.race = r.id
            ORDER BY s.id
            """
        )
        rows = d_cur.fetchall()
        log.info("import_dvbic_subjects.fetched %s", json.dumps({"count": len(rows)}))

        r_cur = recruit.cursor()
        mig_uid = _migration_system_user_id(r_cur)
        inserted = 0
        skipped_mapped = 0
        mapped = 0

        for (
            sid,
            first_name,
            middle_name,
            last_name,
            dob,
            sex_label,
            ssn,
            race_label,
            death_date,
            county,
            zip_v,
        ) in rows:
            subject_id = _dvbic_lookup_subject_target(r_cur, str(sid))
            if subject_id is not None:
                skipped_mapped += 1
            elif cfg.dry_run:
                subject_id = None
            else:
                subject_id = _dvbic_subject_row_insert(
                    r_cur,
                    mig_uid,
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    dob=dob,
                    sex_label=sex_label,
                    ssn=ssn,
                    race_label=race_label,
                    death_date=death_date,
                    county=county,
                    zip_v=zip_v,
                )
                inserted += 1

            if not cfg.dry_run and subject_id is not None:
                r_cur.execute(
                    """
                    INSERT INTO legacy_id_map (
                        source_system, source_table, source_pk, target_table, target_pk, batch_id, imported_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, NOW() AT TIME ZONE 'UTC')
                    ON CONFLICT (source_system, source_table, source_pk) DO NOTHING
                    """,
                    (_DVBIC_SOURCE, "subjects", str(sid), "subjects", subject_id, batch),
                )
                if r_cur.rowcount:
                    mapped += 1

        if cfg.dry_run:
            recruit.rollback()
            log.info(
                "import_dvbic_subjects.dry_run_done %s",
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
                "import_dvbic_subjects.done %s",
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
        dvb.close()
        recruit.close()


def import_dvbic_subjects2(cfg: MigrationConfig) -> int:
    """Import ``dvbic_research.subjects2`` → RECRUIT ``subjects`` + ``legacy_id_map`` (``subjects2`` keys).

    Many DVbic rows (e.g. ``session_notes``) reference ids present only in ``subjects2``.
    When the same id exists in ``subjects``, reuses that map target and adds a ``subjects2`` alias row.
    """
    batch = _require_batch(cfg) if not cfg.dry_run else (cfg.migration_batch_id or "dry-run")
    if not cfg.legacy_dvbic_research_url:
        raise SystemExit("LEGACY_DVBIC_RESEARCH_DATABASE_URL is required.")

    dvb = psycopg2.connect(cfg.legacy_dvbic_research_url)
    recruit = psycopg2.connect(cfg.database_url)
    try:
        d_cur = dvb.cursor()
        d_cur.execute(
            """
            SELECT s.id, s.first_name, s.middle_name, s.last_name, s.date_of_birth,
                   sx.name AS sex_label, s.ssn, r.name AS race_label,
                   s.death_date, s.county, s.zip
            FROM subjects2 s
            LEFT JOIN _sex sx ON s.sex = sx.id
            LEFT JOIN _race r ON s.race = r.id
            ORDER BY s.id
            """
        )
        rows = d_cur.fetchall()
        log.info("import_dvbic_subjects2.fetched %s", json.dumps({"count": len(rows)}))

        r_cur = recruit.cursor()
        mig_uid = _migration_system_user_id(r_cur)
        inserted = 0
        alias_maps = 0
        skipped_mapped = 0

        for (
            sid,
            first_name,
            middle_name,
            last_name,
            dob,
            sex_label,
            ssn,
            race_label,
            death_date,
            county,
            zip_v,
        ) in rows:
            key = str(sid)
            subject_id = _dvbic_lookup_subject_target(r_cur, key)
            if subject_id is not None:
                skipped_mapped += 1
            elif cfg.dry_run:
                subject_id = None
                inserted += 1
            else:
                subject_id = _dvbic_subject_row_insert(
                    r_cur,
                    mig_uid,
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    dob=dob,
                    sex_label=sex_label,
                    ssn=ssn,
                    race_label=race_label,
                    death_date=death_date,
                    county=county,
                    zip_v=zip_v,
                )
                inserted += 1

            if cfg.dry_run or subject_id is None:
                continue

            r_cur.execute(
                """
                INSERT INTO legacy_id_map (
                    source_system, source_table, source_pk, target_table, target_pk, batch_id, imported_at
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW() AT TIME ZONE 'UTC')
                ON CONFLICT (source_system, source_table, source_pk) DO NOTHING
                """,
                (_DVBIC_SOURCE, "subjects2", key, "subjects", subject_id, batch),
            )
            if r_cur.rowcount:
                alias_maps += 1

        if cfg.dry_run:
            recruit.rollback()
            log.info(
                "import_dvbic_subjects2.dry_run_done %s",
                json.dumps(
                    {
                        "would_process": len(rows),
                        "would_insert_new_subjects": inserted,
                        "already_resolved_via_subjects_or_subjects2": skipped_mapped,
                    }
                ),
            )
        else:
            recruit.commit()
            log.info(
                "import_dvbic_subjects2.done %s",
                json.dumps(
                    {
                        "inserted": inserted,
                        "already_resolved_skipped": skipped_mapped,
                        "legacy_id_map_subjects2_rows": alias_maps,
                    }
                ),
            )
        return 0
    except Exception:
        recruit.rollback()
        raise
    finally:
        dvb.close()
        recruit.close()


def _load_dvbic_subject_map(r_cur: Any) -> dict[str, int]:
    """Resolve legacy DVbic subject id via ``subjects`` and/or ``subjects2`` maps."""
    r_cur.execute(
        """
        SELECT source_pk, target_pk FROM legacy_id_map
        WHERE source_system = %s
          AND source_table IN ('subjects', 'subjects2')
          AND target_table = 'subjects'
        """,
        (_DVBIC_SOURCE,),
    )
    return {str(r[0]): int(r[1]) for r in r_cur.fetchall()}


def _dvbic_subject_row_insert(
    r_cur: Any,
    mig_uid: int,
    *,
    first_name,
    middle_name,
    last_name,
    dob,
    sex_label,
    ssn,
    race_label,
    death_date,
    county,
    zip_v,
) -> int:
    zip_s = str(zip_v) if zip_v is not None else None
    sex_s = (sex_label or "").strip().lower().replace(" ", "_") if sex_label else None
    r_cur.execute(
        """
        INSERT INTO subjects (
            first_name, middle_name, last_name, date_of_birth, sex, ssn,
            race, ethnicity, death_date, county, zip, enrollment_status,
            created_by, created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, NULL, %s, %s, %s, NULL,
            %s, NOW() AT TIME ZONE 'UTC', NOW() AT TIME ZONE 'UTC'
        )
        RETURNING id
        """,
        (
            (first_name or "").strip() or "Unknown",
            (middle_name or "").strip() or None,
            (last_name or "").strip() or "Unknown",
            dob,
            sex_s,
            (ssn or "").strip() or None,
            (race_label or "").strip() or None,
            death_date,
            (county or "").strip() or None,
            zip_s,
            mig_uid,
        ),
    )
    return int(r_cur.fetchone()[0])


def _dvbic_lookup_subject_target(r_cur: Any, legacy_sid: str) -> int | None:
    r_cur.execute(
        """
        SELECT target_pk FROM legacy_id_map
        WHERE source_system = %s
          AND source_table IN ('subjects', 'subjects2')
          AND source_pk = %s
          AND target_table = 'subjects'
        ORDER BY CASE source_table WHEN 'subjects' THEN 0 ELSE 1 END
        LIMIT 1
        """,
        (_DVBIC_SOURCE, legacy_sid),
    )
    row = r_cur.fetchone()
    return int(row[0]) if row else None


def _load_dvbic_study_map(r_cur: Any) -> dict[str, int]:
    r_cur.execute(
        """
        SELECT source_pk, target_pk FROM legacy_id_map
        WHERE source_system = %s AND source_table = %s AND target_table = %s
        """,
        (_DVBIC_SOURCE, "studies", "studies"),
    )
    return {str(r[0]): int(r[1]) for r in r_cur.fetchall()}


def _dvbic_tables_with_subject_and_study(d_cur: Any) -> list[str]:
    d_cur.execute(
        """
        SELECT c1.table_name
        FROM information_schema.columns c1
        WHERE c1.table_schema = 'public' AND c1.column_name = 'subject_id'
          AND EXISTS (
              SELECT 1 FROM information_schema.columns c2
              WHERE c2.table_schema = 'public' AND c2.table_name = c1.table_name
                AND c2.column_name = 'study_id'
          )
          AND c1.table_name NOT IN ('subjects', 'subjects2')
          AND c1.table_name NOT LIKE 'django\\_%%' ESCAPE '\\'
        ORDER BY c1.table_name
        """
    )
    return [r[0] for r in d_cur.fetchall()]


def _dvbic_distinct_subject_study_pairs(d_cur: Any) -> set[tuple[int, int]]:
    pairs: set[tuple[int, int]] = set()
    for table in _dvbic_tables_with_subject_and_study(d_cur):
        try:
            d_cur.execute(
                sql.SQL(
                    "SELECT DISTINCT subject_id, study_id FROM {} "
                    "WHERE subject_id IS NOT NULL AND study_id IS NOT NULL"
                ).format(sql.Identifier(table))
            )
            for sid, stid in d_cur.fetchall():
                pairs.add((int(sid), int(stid)))
        except Exception as e:
            log.warning(
                "import_dvbic_subject_study.pair_scan_skip %s",
                json.dumps({"table": table, "error": str(e)}),
            )
    return pairs


def import_dvbic_subject_study(cfg: MigrationConfig) -> int:
    """Infer DVbic enrollments: distinct (subject_id, study_id) across legacy tables → ``subject_study``."""
    if not cfg.legacy_dvbic_research_url:
        raise SystemExit("LEGACY_DVBIC_RESEARCH_DATABASE_URL is required.")

    dvb = psycopg2.connect(cfg.legacy_dvbic_research_url)
    recruit = psycopg2.connect(cfg.database_url)
    try:
        d_cur = dvb.cursor()
        pairs = _dvbic_distinct_subject_study_pairs(d_cur)
        log.info("import_dvbic_subject_study.pairs %s", json.dumps({"distinct_pairs": len(pairs)}))

        r_cur = recruit.cursor()
        subj_map = _load_dvbic_subject_map(r_cur)
        study_map = _load_dvbic_study_map(r_cur)

        inserted = 0
        skipped_dup = 0
        missing_subject = 0
        missing_study = 0
        would_link = 0

        for legacy_sid, legacy_stid in sorted(pairs):
            rid = subj_map.get(str(legacy_sid))
            if rid is None:
                missing_subject += 1
                continue
            r_study_id = study_map.get(str(legacy_stid))
            if r_study_id is None:
                missing_study += 1
                continue
            if cfg.dry_run:
                would_link += 1
                continue
            r_cur.execute(
                """
                INSERT INTO subject_study (subject_id, study_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
                """,
                (rid, r_study_id),
            )
            if r_cur.rowcount:
                inserted += 1
            else:
                skipped_dup += 1

        if cfg.dry_run:
            recruit.rollback()
            log.info(
                "import_dvbic_subject_study.dry_run_done %s",
                json.dumps(
                    {
                        "distinct_pairs": len(pairs),
                        "would_link": would_link,
                        "missing_subject_map": missing_subject,
                        "missing_study_map": missing_study,
                    }
                ),
            )
        else:
            recruit.commit()
            log.info(
                "import_dvbic_subject_study.done %s",
                json.dumps(
                    {
                        "inserted": inserted,
                        "skipped_duplicate": skipped_dup,
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
        dvb.close()
        recruit.close()


_SESSION_NOTES_MAP_TABLE = "session_notes_recruit"


def import_dvbic_session_notes(cfg: MigrationConfig) -> int:
    """Copy ``dvbic_research.session_notes`` → RECRUIT ``session_notes`` + ``legacy_id_map`` (idempotent).

    ``legacy_id_map`` uses ``source_table`` = ``session_notes_recruit`` so rows do not collide with
    ``import-dvbic-instrument-tables`` (which maps the same legacy PK to ``assessments``).
    """
    batch = _require_batch(cfg) if not cfg.dry_run else (cfg.migration_batch_id or "dry-run")
    if not cfg.legacy_dvbic_research_url:
        raise SystemExit("LEGACY_DVBIC_RESEARCH_DATABASE_URL is required.")

    dvb = psycopg2.connect(cfg.legacy_dvbic_research_url)
    recruit = psycopg2.connect(cfg.database_url)
    try:
        d_cur = dvb.cursor()
        d_cur.execute(
            """
            SELECT id, subject_id, visit_num, date, study_id, notes, administrator, verified_by
            FROM session_notes
            ORDER BY id
            """
        )
        rows = d_cur.fetchall()
        log.info("import_dvbic_session_notes.fetched %s", json.dumps({"count": len(rows)}))

        r_cur = recruit.cursor()
        mig_uid = _migration_system_user_id(r_cur)
        subj_map = _load_dvbic_subject_map(r_cur)
        study_map = _load_dvbic_study_map(r_cur)

        inserted = 0
        mapped = 0
        skipped_mapped = 0
        missing_subject = 0

        for (
            legacy_id,
            legacy_subj,
            visit_num,
            sess_date,
            legacy_study,
            notes,
            administrator,
            verified_by,
        ) in rows:
            r_cur.execute(
                """
                SELECT 1 FROM legacy_id_map
                WHERE source_system = %s AND source_table = %s AND source_pk = %s
                  AND target_table = 'session_notes'
                """,
                (_DVBIC_SOURCE, _SESSION_NOTES_MAP_TABLE, str(legacy_id)),
            )
            if r_cur.fetchone():
                skipped_mapped += 1
                continue

            try:
                sid_key = str(int(legacy_subj))
            except (TypeError, ValueError):
                missing_subject += 1
                continue
            subject_id = subj_map.get(sid_key)
            if subject_id is None:
                missing_subject += 1
                continue

            study_id = None
            if legacy_study is not None:
                try:
                    study_id = study_map.get(str(int(legacy_study)))
                except (TypeError, ValueError):
                    study_id = None

            if sess_date is None:
                sd = date.today()
            elif isinstance(sess_date, datetime):
                sd = sess_date.date()
            else:
                sd = sess_date

            meta_bits = []
            if visit_num is not None:
                meta_bits.append(f"visit_num={visit_num}")
            if administrator:
                meta_bits.append(f"administrator={administrator}")
            if verified_by:
                meta_bits.append(f"verified_by={verified_by}")
            body = (notes or "").strip() or None
            if meta_bits:
                suffix = "\n[legacy session_notes: " + "; ".join(meta_bits) + "]"
                body = (body or "") + suffix

            if cfg.dry_run:
                inserted += 1
                continue

            r_cur.execute(
                """
                INSERT INTO session_notes (
                    subject_id, study_id, session_date, notes, created_by, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, NOW() AT TIME ZONE 'UTC', NOW() AT TIME ZONE 'UTC')
                RETURNING id
                """,
                (subject_id, study_id, sd, body, mig_uid),
            )
            new_id = r_cur.fetchone()[0]
            inserted += 1

            r_cur.execute(
                """
                INSERT INTO legacy_id_map (
                    source_system, source_table, source_pk, target_table, target_pk, batch_id, imported_at
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW() AT TIME ZONE 'UTC')
                ON CONFLICT (source_system, source_table, source_pk) DO NOTHING
                """,
                (_DVBIC_SOURCE, _SESSION_NOTES_MAP_TABLE, str(legacy_id), "session_notes", new_id, batch),
            )
            if r_cur.rowcount:
                mapped += 1

        if cfg.dry_run:
            recruit.rollback()
            log.info(
                "import_dvbic_session_notes.dry_run_done %s",
                json.dumps(
                    {
                        "would_insert": inserted,
                        "already_mapped_skipped": skipped_mapped,
                        "missing_subject_map": missing_subject,
                    }
                ),
            )
        else:
            recruit.commit()
            log.info(
                "import_dvbic_session_notes.done %s",
                json.dumps(
                    {
                        "inserted": inserted,
                        "legacy_map_rows": mapped,
                        "already_mapped_skipped": skipped_mapped,
                        "missing_subject_map": missing_subject,
                    }
                ),
            )
        return 0
    except Exception:
        recruit.rollback()
        raise
    finally:
        dvb.close()
        recruit.close()
