"""Phase D1: dvbic_research instrument tables -> RECRUIT assessments (full row JSON, batched, idempotent)."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from datetime import date, datetime
from typing import Any

import psycopg2
from psycopg2 import sql

from migrations_cli.config import MigrationConfig
from migrations_cli.etl_arc import _migration_system_user_id, _require_batch
from migrations_cli.etl_dvbic import _load_dvbic_subject_map
from migrations_cli.etl_migration_events import log_import_orphan
from migrations_cli.etl_row_json import row_to_dict

log = logging.getLogger("migrations_cli")

DVBIC_EXCLUDE_TABLES = frozenset(
    {
        "subjects",
        "subjects2",
        "session_notes",  # use import-dvbic-session-notes → RECRUIT session_notes + legacy_id_map
        "schema_migrations",
        "ar_internal_metadata",
        "active_storage_blobs",
        "active_storage_attachments",
        "active_storage_variant_records",
    }
)

DATE_FALLBACK_COLS = (
    "created_at",
    "updated_at",
    "assessment_date",
    "visit_date",
    "session_date",
    "test_date",
    "exam_date",
    "date",
    "admindate",
    "birthdate",
)


def _sanitize_type_name(table: str) -> str:
    x = re.sub(r"[^a-zA-Z0-9_-]+", "-", table.strip())[:110]
    return f"dvbic-{x}" if x else "dvbic-unknown"


def _load_dvbic_study_map(r_cur) -> dict[str, int]:
    r_cur.execute(
        """
        SELECT source_pk, target_pk FROM legacy_id_map
        WHERE source_system = %s AND source_table = %s AND target_table = %s
        """,
        ("dvbic_research", "studies", "studies"),
    )
    return {str(r[0]): int(r[1]) for r in r_cur.fetchall()}


def _pk_columns(d_cur, table: str) -> list[str]:
    d_cur.execute(
        """
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        WHERE tc.table_schema = 'public'
          AND tc.table_name = %s
          AND tc.constraint_type = 'PRIMARY KEY'
        ORDER BY kcu.ordinal_position
        """,
        (table,),
    )
    return [r[0] for r in d_cur.fetchall()]


def _column_description(d_cur, table: str):
    """Column metadata for ``table`` (server-side cursors may leave ``.description`` unset)."""
    d_cur.execute(sql.SQL("SELECT * FROM {} WHERE FALSE").format(sql.Identifier(table)))
    return d_cur.description


def _candidate_tables(d_cur) -> list[str]:
    d_cur.execute(
        """
        SELECT DISTINCT c.table_name
        FROM information_schema.columns c
        WHERE c.table_schema = 'public'
          AND c.column_name IN ('subject_id', 'subjectid', 'clientid')
          AND c.table_name NOT LIKE 'django\\_%%' ESCAPE '\\'
          AND c.table_name NOT LIKE '\\_%%' ESCAPE '\\'
        ORDER BY c.table_name
        """
    )
    return [t for (t,) in d_cur.fetchall() if t not in DVBIC_EXCLUDE_TABLES]


def _legacy_subject_link(d: dict[str, Any]) -> tuple[str | None, str | None]:
    """Resolve legacy subject key for DVbic rows (``subject_id``, ``subjectid``, or ``clientid``)."""
    for col in ("subject_id", "subjectid", "clientid"):
        if col not in d:
            continue
        raw = d.get(col)
        if raw is None:
            continue
        try:
            return col, str(int(raw))
        except (TypeError, ValueError):
            continue
    return None, None


def _pick_assessment_date(d: dict[str, Any]) -> date:
    for col in DATE_FALLBACK_COLS:
        v = d.get(col)
        if v is None:
            continue
        if isinstance(v, datetime):
            return v.date()
        if isinstance(v, date):
            return v
    return date.today()


def _ensure_type(r_cur, type_name: str, table: str, cfg: MigrationConfig) -> None:
    r_cur.execute("SELECT 1 FROM assessment_types WHERE name = %s", (type_name,))
    if r_cur.fetchone():
        return
    if cfg.dry_run:
        return
    r_cur.execute(
        """
        INSERT INTO assessment_types (
            name, display_name, description, min_score, max_score, fields, is_active,
            created_at, updated_at
        ) VALUES (%s, %s, %s, NULL, NULL, NULL, %s, NOW() AT TIME ZONE 'UTC', NOW() AT TIME ZONE 'UTC')
        """,
        (type_name, f"dvbic import: {table}", f"Bulk import from dvbic_research.{table} (JSON payload).", "true"),
    )


def _source_pk_from_row(d: dict[str, Any], pk_cols: list[str], table: str) -> str:
    if pk_cols:
        parts = [str(d.get(c)) for c in pk_cols]
        if all(p != "None" and p for p in parts):
            return "|".join(parts)
    blob = json.dumps(d, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()[:48]


def _process_dvbic_row(
    cfg: MigrationConfig,
    r_cur: Any,
    recruit: Any,
    table: str,
    type_name: str,
    pk_cols: list[str],
    desc: tuple,
    row: tuple,
    subj_map: dict[str, int],
    study_map: dict[str, int],
    mig_uid: int,
    batch: str,
    chunk: int,
    since_commit: list[int],
) -> tuple[int, int, int, int]:
    """Returns (insert_delta, map_delta, skip_delta, event_delta)."""
    d = row_to_dict(desc, row)
    col_used, sid_key = _legacy_subject_link(d)
    if sid_key is None:
        if not cfg.dry_run:
            log_import_orphan(
                r_cur,
                batch_id=batch,
                event_type="IMPORT_ORPHAN_NO_SUBJECT_KEY",
                summary=f"{table} missing subject_id/subjectid/clientid",
                detail={"table": table, "row": d},
                subject_id=None,
            )
        return (0, 0, 1, 1 if not cfg.dry_run else 0)

    subject_id = subj_map.get(sid_key)
    if subject_id is None:
        if not cfg.dry_run:
            log_import_orphan(
                r_cur,
                batch_id=batch,
                event_type="IMPORT_ORPHAN_NO_SUBJECT_MAP",
                summary=f"{table} {col_used} {sid_key} not in legacy_id_map",
                detail={"table": table, "column": col_used, "legacy_key": sid_key, "row": d},
                subject_id=None,
            )
        return (0, 0, 1, 1 if not cfg.dry_run else 0)

    study_id = None
    if "study_id" in d and d["study_id"] is not None:
        try:
            study_id = study_map.get(str(int(d["study_id"])))
        except (TypeError, ValueError):
            study_id = None

    ad = _pick_assessment_date(d)
    source_pk = _source_pk_from_row(d, pk_cols, table)
    payload = {"legacy_table": f"dvbic_research.{table}", "legacy_pk": source_pk, "row": d}

    if cfg.dry_run:
        return (1, 0, 0, 0)

    r_cur.execute(
        """
        SELECT 1 FROM legacy_id_map
        WHERE source_system = %s AND source_table = %s AND source_pk = %s AND target_table = %s
        """,
        ("dvbic_research", table, source_pk, "assessments"),
    )
    if r_cur.fetchone():
        return (0, 0, 1, 0)

    r_cur.execute(
        """
        INSERT INTO assessments (
            subject_id, study_id, assessment_type, assessment_date, assessment_time,
            total_score, notes, data, created_by, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, NULL, NULL, NULL, %s, %s,
            NOW() AT TIME ZONE 'UTC', NOW() AT TIME ZONE 'UTC')
        RETURNING id
        """,
        (
            subject_id,
            study_id,
            type_name,
            ad,
            json.dumps(payload, ensure_ascii=False, default=str),
            mig_uid,
        ),
    )
    aid = r_cur.fetchone()[0]

    r_cur.execute(
        """
        INSERT INTO legacy_id_map (
            source_system, source_table, source_pk, target_table, target_pk, batch_id, imported_at
        ) VALUES (%s, %s, %s, %s, %s, %s, NOW() AT TIME ZONE 'UTC')
        ON CONFLICT (source_system, source_table, source_pk) DO NOTHING
        """,
        ("dvbic_research", table, source_pk, "assessments", aid, batch),
    )
    mapped = 1 if r_cur.rowcount else 0

    since_commit[0] += 1
    if since_commit[0] >= chunk:
        recruit.commit()
        since_commit[0] = 0

    return (1, mapped, 0, 0)


def import_dvbic_instrument_tables(cfg: MigrationConfig) -> int:
    """Import public tables with ``subject_id`` into assessments (full row JSON)."""
    batch = _require_batch(cfg) if not cfg.dry_run else (cfg.migration_batch_id or "dry-run")
    if not cfg.legacy_dvbic_research_url:
        raise SystemExit("LEGACY_DVBIC_RESEARCH_DATABASE_URL is required.")

    chunk = int(os.environ.get("MIGRATION_COMMIT_CHUNK", "200"))
    stream_threshold = int(os.environ.get("MIGRATION_STREAM_ROW_THRESHOLD", "40000"))

    dvb = psycopg2.connect(cfg.legacy_dvbic_research_url)
    recruit = psycopg2.connect(cfg.database_url)
    try:
        d_cur = dvb.cursor()
        r_cur = recruit.cursor()
        mig_uid = _migration_system_user_id(r_cur)
        subj_map = _load_dvbic_subject_map(r_cur)
        study_map = _load_dvbic_study_map(r_cur)

        tables = _candidate_tables(d_cur)
        log.info("import_dvbic_instruments.discovered %s", json.dumps({"tables": len(tables)}))

        tot_ins = tot_map = tot_skip = tot_evt = 0
        since_commit = [0]

        for table in tables:
            try:
                d_cur.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table)))
                n = d_cur.fetchone()[0]
            except Exception as e:
                log.warning("import_dvbic_instruments.skip_count %s", json.dumps({"table": table, "error": str(e)}))
                continue
            if not n:
                continue

            if cfg.dry_run:
                log.info(
                    "import_dvbic_instruments.table_dry_run %s",
                    json.dumps({"table": table, "row_upper_bound": n}),
                )
                tot_ins += n
                continue

            pk_cols = _pk_columns(d_cur, table)
            type_name = _sanitize_type_name(table)
            _ensure_type(r_cur, type_name, table, cfg)

            tins = tmap = tskp = tev = 0
            q = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table))

            if n > stream_threshold:
                sc = dvb.cursor(name=f"dvb_{abs(hash(table)) % 10_000_000}")
                sc.itersize = 500
                sc.execute(q)
                desc = sc.description or _column_description(d_cur, table)
                if desc is None:
                    raise RuntimeError(f"no column metadata for {table!r}")
                try:
                    for row in sc:
                        di, dm, ds, de = _process_dvbic_row(
                            cfg,
                            r_cur,
                            recruit,
                            table,
                            type_name,
                            pk_cols,
                            desc,
                            row,
                            subj_map,
                            study_map,
                            mig_uid,
                            batch,
                            chunk,
                            since_commit,
                        )
                        tins += di
                        tmap += dm
                        tskp += ds
                        tev += de
                finally:
                    sc.close()
            else:
                d_cur.execute(q)
                desc = d_cur.description
                for row in d_cur.fetchall():
                    di, dm, ds, de = _process_dvbic_row(
                        cfg,
                        r_cur,
                        recruit,
                        table,
                        type_name,
                        pk_cols,
                        desc,
                        row,
                        subj_map,
                        study_map,
                        mig_uid,
                        batch,
                        chunk,
                        since_commit,
                    )
                    tins += di
                    tmap += dm
                    tskp += ds
                    tev += de

            log.info(
                "import_dvbic_instruments.table_done %s",
                json.dumps({"table": table, "inserted": tins, "skipped": tskp, "mapped": tmap, "events": tev}),
            )
            tot_ins += tins
            tot_map += tmap
            tot_skip += tskp
            tot_evt += tev

        if cfg.dry_run:
            recruit.rollback()
            log.info(
                "import_dvbic_instruments.dry_run_done %s",
                json.dumps(
                    {
                        "row_count_upper_bound": tot_ins,
                        "note": "dry_run sums COUNT(*) per table; orphans not subtracted",
                    }
                ),
            )
        else:
            recruit.commit()
            log.info(
                "import_dvbic_instruments.done %s",
                json.dumps(
                    {
                        "inserted": tot_ins,
                        "legacy_map_rows": tot_map,
                        "skipped": tot_skip,
                        "migration_events": tot_evt,
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
