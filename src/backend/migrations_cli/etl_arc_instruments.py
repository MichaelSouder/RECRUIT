"""Phase C2: arc clinical / instrument tables -> RECRUIT assessments (full row JSON, idempotent)."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import date, datetime

import psycopg2

from migrations_cli.config import MigrationConfig
from migrations_cli.etl_arc import _migration_system_user_id, _require_batch
from migrations_cli.etl_migration_events import log_import_orphan
from migrations_cli.etl_row_json import row_to_dict

log = logging.getLogger("migrations_cli")

# (table, pk_column, proc_num / proclist_id column, or None for grid-only rows, grid_column or None if from proc only, extra_date_columns for assessment_date fallback)
ARC_INSTRUMENT_SPECS: list[tuple[str, str, str | None, str | None, list[str]]] = [
    ("mmses", "id", "proc_num", "grid", ["mmsedate"]),
    ("npiqs", "id", "proc_num", "grid", []),
    ("gds15s", "id", "proc_num", "grid", []),
    ("rawscores", "id", "proc_num", "grid", []),
    ("consensusdxes", "id", "proc_num", "grid", []),
    ("preconsensusdxes", "id", "proc_num", "grid", []),
    ("initialdxes", "id", "proc_num", "grid", []),
    ("hxexams", "id", "proc_num", "grid", []),
    ("imagereports", "id", "proc_num", "grid", []),
    ("otevals", "id", "proc_num", "grid", []),
    ("drivingqs", "id", "proc_num", "grid", []),
    ("faqs", "id", "proclist_id", None, []),
    ("study1018_selfreports", "proc_num", "proc_num", "grid", ["proc_date", "proc_starttime"]),
    ("ummc_mmses", "id", "proc_num", "grid", ["mmsedate"]),
    ("ummc_npiqs", "id", "proc_num", "grid", []),
    ("ummc_gds15s", "id", "proc_num", "grid", []),
    ("ummc_hxexams", "id", "proc_num", "grid", []),
    ("ummc_initialdxes", "id", "proc_num", "grid", []),
    ("ummc_preconsensusdxes", "id", "proc_num", "grid", []),
    ("ummc_otevals", "id", "proc_num", "grid", []),
    ("ummc_imagereports", "id", "proc_num", "grid", []),
    ("ummc_drivingqs", "id", "proc_num", "grid", []),
    # Visit-linked (proc_list spine)
    ("data_svfs", "id", "proc_num", "grid", []),
    ("drivingdata_roadsigns", "id", "proclist_id", None, []),
    # Grid-only (subject from subj_list map; study_id left null unless proc_list path used later)
    ("contact", "grid", None, "grid", ["mod_date", "ent_date"]),
    ("icad06dxes", "id", None, "grid", ["created_on", "updated_on"]),
    ("autopsies", "rownames", None, "grid", ["doa", "dod", "toa", "tod"]),
    ("inventories", "id", None, "grid", ["created_on", "updated_on"]),
]


def _load_maps(r_cur) -> tuple[dict[str, int], dict[str, int]]:
    sm = {}
    r_cur.execute(
        """
        SELECT source_pk, target_pk FROM legacy_id_map
        WHERE source_system = %s AND source_table = %s AND target_table = %s
        """,
        ("arc", "subj_list", "subjects"),
    )
    sm = {str(r[0]): int(r[1]) for r in r_cur.fetchall()}
    tm = {}
    r_cur.execute(
        """
        SELECT source_pk, target_pk FROM legacy_id_map
        WHERE source_system = %s AND source_table = %s AND target_table = %s
        """,
        ("arc", "study_desc", "studies"),
    )
    tm = {str(r[0]): int(r[1]) for r in r_cur.fetchall()}
    return sm, tm


def _proc_meta(arc_cur) -> dict[str, tuple[int, int | None, datetime | None, datetime | None]]:
    """proc_num -> (grid, study_code, proc_date, proc_starttime)."""
    arc_cur.execute(
        "SELECT proc_num, grid, study_code, proc_date, proc_starttime FROM proc_list"
    )
    out: dict[str, tuple[int, int | None, datetime | None, datetime | None]] = {}
    for proc_num, grid, study_code, proc_date, proc_starttime in arc_cur.fetchall():
        out[str(proc_num)] = (int(grid), int(study_code) if study_code is not None else None, proc_date, proc_starttime)
    return out


def _pick_date(row_dict: dict, extra_cols: list[str], proc_date, proc_start) -> date:
    for c in extra_cols:
        v = row_dict.get(c)
        if v is None:
            continue
        if isinstance(v, datetime):
            return v.date()
        if isinstance(v, date):
            return v
    if proc_date:
        return proc_date.date() if hasattr(proc_date, "date") else proc_date
    if proc_start:
        return proc_start.date() if hasattr(proc_start, "date") else proc_start
    return date(1970, 1, 1)


def _ensure_assessment_type(r_cur, table: str, cfg: MigrationConfig) -> str:
    name = f"arc-{table.replace('_', '-')}"
    if len(name) > 120:
        name = name[:117] + "..."
    r_cur.execute("SELECT 1 FROM assessment_types WHERE name = %s", (name,))
    if r_cur.fetchone():
        return name
    if cfg.dry_run:
        return name
    r_cur.execute(
        """
        INSERT INTO assessment_types (
            name, display_name, description, min_score, max_score, fields, is_active,
            created_at, updated_at
        ) VALUES (%s, %s, %s, NULL, NULL, NULL, %s, NOW() AT TIME ZONE 'UTC', NOW() AT TIME ZONE 'UTC')
        """,
        (name, f"arc import: {table}", f"Bulk import from arc.{table} (JSON payload).", "true"),
    )
    return name


def import_arc_instrument_tables(cfg: MigrationConfig) -> int:
    """Import configured arc instrument tables into assessments + legacy_id_map."""
    batch = _require_batch(cfg) if not cfg.dry_run else (cfg.migration_batch_id or "dry-run")
    if not cfg.legacy_arc_url:
        raise SystemExit("LEGACY_ARC_DATABASE_URL is required.")

    arc = psycopg2.connect(cfg.legacy_arc_url)
    recruit = psycopg2.connect(cfg.database_url)
    try:
        arc_cur = arc.cursor()
        proc_meta = _proc_meta(arc_cur)

        r_cur = recruit.cursor()
        mig_uid = _migration_system_user_id(r_cur)
        grid_map, study_map = _load_maps(r_cur)

        total_ins = 0
        total_map = 0
        total_skip = 0
        total_evt = 0

        for table, pk_col, proc_col, grid_col, extra_dates in ARC_INSTRUMENT_SPECS:
            arc_cur.execute(f'SELECT * FROM "{table}"')
            desc = arc_cur.description
            rows = arc_cur.fetchall()
            if not rows:
                log.info("import_arc_instruments.skip_empty %s", json.dumps({"table": table}))
                continue

            type_name = _ensure_assessment_type(r_cur, table, cfg)
            ins = 0
            skp = 0
            mp = 0
            ev = 0

            for row in rows:
                d = row_to_dict(desc, row)
                pk_val = d.get(pk_col)
                if pk_val is None:
                    pk_val = d.get(str(pk_col))
                source_pk = str(pk_val) if pk_val is not None else None
                if source_pk is None:
                    source_pk = hashlib.sha256(json.dumps(d, sort_keys=True, default=str).encode()).hexdigest()[:40]

                if proc_col is None:
                    # Grid-only: no proc_list join; map subject via grid on the row.
                    if not grid_col:
                        skp += 1
                        if not cfg.dry_run:
                            log_import_orphan(
                                r_cur,
                                batch_id=batch,
                                event_type="IMPORT_ORPHAN_GRID_ONLY_NO_GRID_COL",
                                summary=f"{table} grid-only spec missing grid_col",
                                detail={"table": table, "row": d},
                                subject_id=None,
                            )
                            ev += 1
                        continue
                    grid_val = d.get(grid_col)
                    try:
                        grid_int = int(grid_val)
                    except (TypeError, ValueError):
                        skp += 1
                        if not cfg.dry_run:
                            log_import_orphan(
                                r_cur,
                                batch_id=batch,
                                event_type="IMPORT_ORPHAN_BAD_GRID",
                                summary=f"{table} bad grid",
                                detail={"table": table, "grid": grid_val, "row": d},
                                subject_id=None,
                            )
                            ev += 1
                        continue
                    subject_id = grid_map.get(str(grid_int))
                    if subject_id is None:
                        skp += 1
                        if not cfg.dry_run:
                            log_import_orphan(
                                r_cur,
                                batch_id=batch,
                                event_type="IMPORT_ORPHAN_NO_SUBJECT_MAP",
                                summary=f"{table} grid {grid_int} not mapped",
                                detail={"table": table, "grid": grid_int, "row": d},
                                subject_id=None,
                            )
                            ev += 1
                        continue
                    study_id = None
                    ad = _pick_date(d, extra_dates, None, None)
                    atime = None
                else:
                    proc_raw = d.get(proc_col)
                    if proc_raw is None:
                        skp += 1
                        if not cfg.dry_run:
                            log_import_orphan(
                                r_cur,
                                batch_id=batch,
                                event_type="IMPORT_ORPHAN_NO_PROC",
                                summary=f"{table} missing {proc_col}",
                                detail={"table": table, "row": d},
                                subject_id=None,
                            )
                            ev += 1
                        continue

                    proc_key = str(int(proc_raw)) if isinstance(proc_raw, (int, float)) else str(proc_raw).strip()
                    meta = proc_meta.get(proc_key)
                    if not meta:
                        skp += 1
                        if not cfg.dry_run:
                            log_import_orphan(
                                r_cur,
                                batch_id=batch,
                                event_type="IMPORT_ORPHAN_PROC_NOT_IN_SPINE",
                                summary=f"{table} proc {proc_key} not in proc_list",
                                detail={"table": table, "proc": proc_key, "row": d},
                                subject_id=None,
                            )
                            ev += 1
                        continue

                    grid_from_proc, study_code, pdate, pstart = meta
                    grid_val = d.get(grid_col) if grid_col else grid_from_proc
                    if grid_val is None:
                        grid_val = grid_from_proc
                    try:
                        grid_int = int(grid_val)
                    except (TypeError, ValueError):
                        skp += 1
                        if not cfg.dry_run:
                            log_import_orphan(
                                r_cur,
                                batch_id=batch,
                                event_type="IMPORT_ORPHAN_BAD_GRID",
                                summary=f"{table} bad grid",
                                detail={"table": table, "grid": grid_val, "row": d},
                                subject_id=None,
                            )
                            ev += 1
                        continue

                    subject_id = grid_map.get(str(grid_int))
                    if subject_id is None:
                        skp += 1
                        if not cfg.dry_run:
                            log_import_orphan(
                                r_cur,
                                batch_id=batch,
                                event_type="IMPORT_ORPHAN_NO_SUBJECT_MAP",
                                summary=f"{table} grid {grid_int} not mapped",
                                detail={"table": table, "grid": grid_int, "row": d},
                                subject_id=None,
                            )
                            ev += 1
                        continue

                    study_id = None
                    if study_code is not None:
                        study_id = study_map.get(str(int(study_code)))

                    ad = _pick_date(d, extra_dates, pdate, pstart)
                    atime = pstart.time() if pstart else None

                payload = {"legacy_table": f"arc.{table}", "legacy_pk": source_pk, "row": d}

                if cfg.dry_run:
                    ins += 1
                    continue

                r_cur.execute(
                    """
                    SELECT 1 FROM legacy_id_map
                    WHERE source_system = %s AND source_table = %s AND source_pk = %s AND target_table = %s
                    """,
                    ("arc", table, source_pk, "assessments"),
                )
                if r_cur.fetchone():
                    skp += 1
                    continue

                r_cur.execute(
                    """
                    INSERT INTO assessments (
                        subject_id, study_id, assessment_type, assessment_date, assessment_time,
                        total_score, notes, data, created_by, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, NULL, NULL, %s, %s,
                        NOW() AT TIME ZONE 'UTC', NOW() AT TIME ZONE 'UTC')
                    RETURNING id
                    """,
                    (
                        subject_id,
                        study_id,
                        type_name,
                        ad,
                        atime,
                        json.dumps(payload, ensure_ascii=False, default=str),
                        mig_uid,
                    ),
                )
                aid = r_cur.fetchone()[0]
                ins += 1

                r_cur.execute(
                    """
                    INSERT INTO legacy_id_map (
                        source_system, source_table, source_pk, target_table, target_pk, batch_id, imported_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, NOW() AT TIME ZONE 'UTC')
                    ON CONFLICT (source_system, source_table, source_pk) DO NOTHING
                    """,
                    ("arc", table, source_pk, "assessments", aid, batch),
                )
                if r_cur.rowcount:
                    mp += 1

            log.info(
                "import_arc_instruments.table_done %s",
                json.dumps({"table": table, "inserted": ins, "skipped": skp, "mapped": mp, "events": ev}),
            )
            total_ins += ins
            total_map += mp
            total_skip += skp
            total_evt += ev

        if cfg.dry_run:
            recruit.rollback()
            log.info(
                "import_arc_instruments.dry_run_done %s",
                json.dumps({"would_insert": total_ins, "skipped": total_skip}),
            )
        else:
            recruit.commit()
            log.info(
                "import_arc_instruments.done %s",
                json.dumps(
                    {
                        "inserted": total_ins,
                        "legacy_map_rows": total_map,
                        "skipped": total_skip,
                        "migration_events": total_evt,
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
