"""Phase C1: ``arc.proc_desc`` / ``arc.proc_list`` -> RECRUIT ``assessment_types`` + ``assessments``."""

from __future__ import annotations

import json
import logging
from datetime import date
from typing import Any

import psycopg2

from migrations_cli.config import MigrationConfig
from migrations_cli.etl_arc import _migration_system_user_id, _require_batch

log = logging.getLogger("migrations_cli")


def _load_target_map(
    r_cur: Any, *, source_table: str, target_table: str
) -> dict[str, int]:
    r_cur.execute(
        """
        SELECT source_pk, target_pk FROM legacy_id_map
        WHERE source_system = %s AND source_table = %s AND target_table = %s
        """,
        ("arc", source_table, target_table),
    )
    return {str(r[0]): int(r[1]) for r in r_cur.fetchall()}


def import_arc_assessment_types(cfg: MigrationConfig) -> int:
    """Upsert ``assessment_types`` rows from ``arc.proc_desc`` (``name`` = ``arc-proc-{code}``)."""
    if not cfg.legacy_arc_url:
        raise SystemExit("LEGACY_ARC_DATABASE_URL is required.")

    arc = psycopg2.connect(cfg.legacy_arc_url)
    recruit = psycopg2.connect(cfg.database_url)
    try:
        arc_cur = arc.cursor()
        arc_cur.execute(
            "SELECT code, descr, note FROM proc_desc ORDER BY code"
        )
        rows = arc_cur.fetchall()
        log.info("import_arc_assessment_types.fetched %s", json.dumps({"count": len(rows)}))

        r_cur = recruit.cursor()
        inserted = 0
        skipped = 0

        for code, descr, note in rows:
            name = f"arc-proc-{code}"
            r_cur.execute("SELECT 1 FROM assessment_types WHERE name = %s", (name,))
            if r_cur.fetchone():
                skipped += 1
                continue
            if cfg.dry_run:
                inserted += 1  # count would-be
                continue
            display = (descr or "").strip() or f"Procedure {code}"
            if len(display) > 500:
                display = display[:497] + "..."
            desc_parts = [p for p in (descr, note) if p]
            description = "\n\n".join(desc_parts) if desc_parts else None
            r_cur.execute(
                """
                INSERT INTO assessment_types (
                    name, display_name, description, min_score, max_score, fields, is_active,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, NULL, NULL, NULL, %s,
                    NOW() AT TIME ZONE 'UTC', NOW() AT TIME ZONE 'UTC'
                )
                """,
                (name, display, description, "true"),
            )
            inserted += 1

        if cfg.dry_run:
            recruit.rollback()
            log.info(
                "import_arc_assessment_types.dry_run_done %s",
                json.dumps({"would_insert": inserted, "already_exist": skipped}),
            )
        else:
            recruit.commit()
            log.info(
                "import_arc_assessment_types.done %s",
                json.dumps({"inserted": inserted, "skipped_existing": skipped}),
            )
        return 0
    except Exception:
        recruit.rollback()
        raise
    finally:
        arc.close()
        recruit.close()


def import_arc_proc_list(cfg: MigrationConfig) -> int:
    """Import ``arc.proc_list`` into ``assessments`` + ``legacy_id_map`` (requires subject maps)."""
    batch = _require_batch(cfg) if not cfg.dry_run else (cfg.migration_batch_id or "dry-run")
    if not cfg.legacy_arc_url:
        raise SystemExit("LEGACY_ARC_DATABASE_URL is required.")

    arc = psycopg2.connect(cfg.legacy_arc_url)
    recruit = psycopg2.connect(cfg.database_url)
    try:
        r_cur = recruit.cursor()
        mig_uid = _migration_system_user_id(r_cur)
        grid_map = _load_target_map(r_cur, source_table="subj_list", target_table="subjects")
        study_map = _load_target_map(r_cur, source_table="study_desc", target_table="studies")

        arc_cur = arc.cursor()
        arc_cur.execute(
            """
            SELECT proc_num, grid, proc_code, study_code, proc_date, proc_starttime, proc_endtime,
                   proc_status, proc_quality, comment
            FROM proc_list
            ORDER BY proc_num
            """
        )
        rows = arc_cur.fetchall()
        log.info("import_arc_proc_list.fetched %s", json.dumps({"count": len(rows)}))

        inserted = 0
        mapped = 0
        missing_subject = 0
        missing_type = 0
        would_import = 0
        skipped_already_mapped = 0

        for (
            proc_num,
            grid,
            proc_code,
            study_code,
            proc_date,
            proc_starttime,
            proc_endtime,
            proc_status,
            proc_quality,
            comment,
        ) in rows:
            sid = grid_map.get(str(grid))
            if sid is None:
                missing_subject += 1
                continue

            type_name = f"arc-proc-{proc_code}"
            r_cur.execute("SELECT 1 FROM assessment_types WHERE name = %s", (type_name,))
            if not r_cur.fetchone():
                missing_type += 1
                continue

            r_cur.execute(
                """
                SELECT 1 FROM legacy_id_map
                WHERE source_system = %s AND source_table = %s AND source_pk = %s AND target_table = %s
                """,
                ("arc", "proc_list", str(proc_num), "assessments"),
            )
            if r_cur.fetchone():
                skipped_already_mapped += 1
                continue

            if cfg.dry_run:
                would_import += 1
                continue

            study_id = study_map.get(str(study_code)) if study_code is not None else None

            if proc_date:
                ad = proc_date.date()
            else:
                ad = proc_starttime.date() if proc_starttime else date(1970, 1, 1)

            atime = None
            if proc_starttime:
                atime = proc_starttime.time()

            notes = (comment or "").strip() or None
            if notes and len(notes) > 10000:
                notes = notes[:9997] + "..."

            payload = {
                "legacy": "arc.proc_list",
                "proc_num": proc_num,
                "proc_code": proc_code,
                "study_code": study_code,
                "proc_status": proc_status,
                "proc_quality": proc_quality,
                "proc_endtime": proc_endtime.isoformat() if proc_endtime else None,
            }

            r_cur.execute(
                """
                INSERT INTO assessments (
                    subject_id, study_id, assessment_type, assessment_date, assessment_time,
                    total_score, notes, data, created_by, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, NULL, %s, %s, %s,
                    NOW() AT TIME ZONE 'UTC', NOW() AT TIME ZONE 'UTC'
                )
                RETURNING id
                """,
                (
                    sid,
                    study_id,
                    type_name,
                    ad,
                    atime,
                    notes,
                    json.dumps(payload),
                    mig_uid,
                ),
            )
            aid = r_cur.fetchone()[0]
            inserted += 1

            r_cur.execute(
                """
                INSERT INTO legacy_id_map (
                    source_system, source_table, source_pk, target_table, target_pk, batch_id, imported_at
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW() AT TIME ZONE 'UTC')
                ON CONFLICT (source_system, source_table, source_pk) DO NOTHING
                """,
                ("arc", "proc_list", str(proc_num), "assessments", aid, batch),
            )
            if r_cur.rowcount:
                mapped += 1

        if cfg.dry_run:
            recruit.rollback()
            log.info(
                "import_arc_proc_list.dry_run_done %s",
                json.dumps(
                    {
                        "would_process": len(rows),
                        "would_import": would_import,
                        "already_mapped_skipped": skipped_already_mapped,
                        "missing_subject_map": missing_subject,
                        "missing_assessment_type": missing_type,
                    }
                ),
            )
        else:
            recruit.commit()
            log.info(
                "import_arc_proc_list.done %s",
                json.dumps(
                    {
                        "inserted": inserted,
                        "legacy_map_rows": mapped,
                        "already_mapped_skipped": skipped_already_mapped,
                        "missing_subject_map": missing_subject,
                        "missing_assessment_type": missing_type,
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


def prune_duplicate_arc_proc_assessments(cfg: MigrationConfig, *, apply: bool) -> int:
    """Remove duplicate ``arc-proc-*`` visit rows (same ``data.proc_num``), keeping the ``legacy_id_map`` target when possible.

    Safe default: **dry-run** (counts only). Pass ``apply=True`` and omit global ``--dry-run`` to delete extras
    and repoint ``legacy_id_map`` when the map pointed at a duplicate that will be removed.
    """
    from collections import defaultdict

    recruit = psycopg2.connect(cfg.database_url)
    try:
        r_cur = recruit.cursor()
        r_cur.execute(
            """
            SELECT source_pk, target_pk FROM legacy_id_map
            WHERE source_system = %s AND source_table = %s AND target_table = %s
            """,
            ("arc", "proc_list", "assessments"),
        )
        proc_to_canonical = {str(a): int(b) for a, b in r_cur.fetchall()}

        r_cur.execute(
            """
            SELECT id, data->>'proc_num' AS pn
            FROM assessments
            WHERE assessment_type LIKE 'arc-proc-%%'
              AND (data::jsonb) ? 'proc_num'
              AND data->>'proc_num' ~ '^[0-9]+$'
            """
        )
        by_pn: dict[str, list[int]] = defaultdict(list)
        for aid, pn in r_cur.fetchall():
            if pn:
                by_pn[str(pn)].append(int(aid))

        to_delete: list[int] = []
        map_fixes: list[tuple[str, int]] = []

        for pn, ids in by_pn.items():
            uniq = sorted(set(ids))
            if len(uniq) <= 1:
                continue
            canonical = proc_to_canonical.get(pn)
            if canonical is not None and canonical in uniq:
                keeper = canonical
            else:
                keeper = min(uniq)
                if canonical is not None and canonical not in uniq:
                    map_fixes.append((pn, keeper))

            for i in uniq:
                if i != keeper:
                    to_delete.append(i)

        log.info(
            "prune_duplicate_arc_proc.summary %s",
            json.dumps(
                {
                    "duplicate_assessment_ids": len(to_delete),
                    "legacy_map_repoints": len(map_fixes),
                    "apply": bool(apply and not cfg.dry_run),
                }
            ),
        )

        if cfg.dry_run or not apply:
            recruit.rollback()
            log.info(
                "prune_duplicate_arc_proc.dry_run_done %s",
                json.dumps({"would_delete": len(to_delete), "would_repoint_map": len(map_fixes)}),
            )
            return 0

        for pn, new_target in map_fixes:
            r_cur.execute(
                """
                UPDATE legacy_id_map SET target_pk = %s, imported_at = NOW() AT TIME ZONE 'UTC'
                WHERE source_system = %s AND source_table = %s AND source_pk = %s AND target_table = %s
                """,
                (new_target, "arc", "proc_list", pn, "assessments"),
            )

        if to_delete:
            r_cur.execute(
                "DELETE FROM assessments WHERE id = ANY(%s)",
                (to_delete,),
            )

        recruit.commit()
        log.info(
            "prune_duplicate_arc_proc.done %s",
            json.dumps({"deleted": len(to_delete), "map_rows_updated": len(map_fixes)}),
        )
        return 0
    except Exception:
        recruit.rollback()
        raise
    finally:
        recruit.close()
