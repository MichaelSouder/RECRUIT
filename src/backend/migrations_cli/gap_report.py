"""Inventory legacy public tables vs. current migrations_cli coverage (read-only)."""

from __future__ import annotations

import json
import logging
from typing import Any

from migrations_cli.config import MigrationConfig
from migrations_cli.db import run_query
from migrations_cli.etl_arc_instruments import ARC_INSTRUMENT_SPECS
from migrations_cli.etl_dvbic_instruments import DVBIC_EXCLUDE_TABLES

log = logging.getLogger("migrations_cli")

ARC_CORE_TABLES = frozenset(
    {
        "auth_user",
        "study_desc",
        "subj_list",
        "study_list",
        "study_acl",
        "proc_desc",
        "proc_list",
    }
)

ARC_OTHER_ETL_TABLES = frozenset(
    {
        "studyproc_list",
    }
)

ARC_INSTRUMENT_TABLES = frozenset(spec[0] for spec in ARC_INSTRUMENT_SPECS)

# Infrastructure / framework tables: not imported per product decision (see docs).
_INFRA_EXACT = frozenset(
    {
        "schema_migrations",
        "ar_internal_metadata",
        "sessions",
        "admin_users",
    }
)
_INFRA_PREFIXES = (
    "django_",
    "active_storage_",
    "active_admin_",
    "solid_queue_",
    "action_mailbox_",
    "action_text_",
    "pga_",
)


def _is_infra_table(name: str) -> bool:
    n = (name or "").strip().lower()
    if n in _INFRA_EXACT:
        return True
    for p in _INFRA_PREFIXES:
        if n.startswith(p):
            return True
    # Arc/DVbic Rails-style auth tables except the one we import (auth_user).
    if n.startswith("auth_") and n != "auth_user":
        return True
    return False


def _list_public_tables(legacy_url: str) -> list[str]:
    rows = run_query(
        legacy_url,
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """,
    )
    return [r[0] for r in rows]


def _pg_stat_estimates(legacy_url: str) -> dict[str, int]:
    """Best-effort live row estimates (may be stale)."""
    try:
        rows = run_query(
            legacy_url,
            """
            SELECT relname, COALESCE(n_live_tup, 0)::bigint
            FROM pg_stat_user_tables
            WHERE schemaname = 'public'
            """,
        )
    except Exception as e:
        log.warning("gap_report.pg_stat_unavailable %s", json.dumps({"error": str(e)}))
        return {}
    return {str(r[0]): int(r[1]) for r in rows}


def _classify_arc(
    tables: list[str], *, with_stats: bool, stats: dict[str, int]
) -> dict[str, Any]:
    core: list[dict[str, Any]] = []
    instruments: list[dict[str, Any]] = []
    infra: list[dict[str, Any]] = []
    misc: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []

    for t in tables:
        row: dict[str, Any] = {"table": t}
        if with_stats and t in stats:
            row["rows_est"] = stats[t]
        if t in ARC_CORE_TABLES:
            core.append(row)
        elif t in ARC_OTHER_ETL_TABLES:
            misc.append(row)
        elif t in ARC_INSTRUMENT_TABLES:
            instruments.append(row)
        elif _is_infra_table(t):
            infra.append(row)
        else:
            gaps.append(row)

    return {
        "summary": {
            "public_tables": len(tables),
            "covered_core": len(core),
            "covered_other_etl": len(misc),
            "covered_instrument_specs": len(instruments),
            "excluded_infrastructure": len(infra),
            "gap_not_covered": len(gaps),
        },
        "covered_core": sorted(core, key=lambda x: x["table"]),
        "covered_other_etl": sorted(misc, key=lambda x: x["table"]),
        "covered_instrument_specs": sorted(instruments, key=lambda x: x["table"]),
        "excluded_infrastructure": sorted(infra, key=lambda x: x["table"]),
        "gap_not_covered": sorted(gaps, key=lambda x: x["table"]),
    }


def _classify_dvbic(
    tables: list[str],
    *,
    with_stats: bool,
    stats: dict[str, int],
    subject_id_tables: set[str],
) -> dict[str, Any]:
    explicit = {"studies", "subjects", "session_notes"}
    explicit_rows: list[dict[str, Any]] = []
    instrument_auto: list[dict[str, Any]] = []
    excluded_explicit: list[dict[str, Any]] = []
    infra: list[dict[str, Any]] = []
    reference: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []

    for t in tables:
        row: dict[str, Any] = {"table": t}
        if with_stats and t in stats:
            row["rows_est"] = stats[t]

        if t in explicit:
            explicit_rows.append(row)
        elif t in DVBIC_EXCLUDE_TABLES:
            excluded_explicit.append(row)
        elif _is_infra_table(t):
            infra.append(row)
        elif t.startswith("_"):
            reference.append(row)
        elif t in subject_id_tables:
            # Same rule as import-dvbic-instrument-tables _candidate_tables (minus excludes handled above).
            instrument_auto.append(row)
        else:
            gaps.append(row)

    return {
        "summary": {
            "public_tables": len(tables),
            "covered_explicit_etl": len(explicit_rows),
            "covered_subject_id_instruments": len(instrument_auto),
            "excluded_explicit_list": len(excluded_explicit),
            "excluded_infrastructure": len(infra),
            "reference_lookups": len(reference),
            "gap_no_subject_id_or_nonstandard": len(gaps),
        },
        "covered_explicit_etl": sorted(explicit_rows, key=lambda x: x["table"]),
        "covered_subject_id_instruments": sorted(instrument_auto, key=lambda x: x["table"]),
        "excluded_explicit_list": sorted(excluded_explicit, key=lambda x: x["table"]),
        "excluded_infrastructure": sorted(infra, key=lambda x: x["table"]),
        "reference_lookups": sorted(reference, key=lambda x: x["table"]),
        "gap_no_subject_id_or_nonstandard": sorted(gaps, key=lambda x: x["table"]),
    }


def build_gap_report(cfg: MigrationConfig, *, with_stats: bool) -> dict[str, Any]:
    if not cfg.legacy_arc_url:
        raise SystemExit(
            "legacy-gap-report requires LEGACY_ARC_DATABASE_URL "
            "(read-only inventory against the arc database)."
        )

    stats_arc: dict[str, int] = {}
    stats_dvbic: dict[str, int] = {}
    if with_stats:
        stats_arc = _pg_stat_estimates(cfg.legacy_arc_url)

    arc_tables = _list_public_tables(cfg.legacy_arc_url)
    arc_report = _classify_arc(arc_tables, with_stats=with_stats, stats=stats_arc)

    dvbic_report: dict[str, Any] | None = None
    if cfg.legacy_dvbic_research_url:
        if with_stats:
            stats_dvbic = _pg_stat_estimates(cfg.legacy_dvbic_research_url)
        dvb_tables = _list_public_tables(cfg.legacy_dvbic_research_url)
        rows_u = run_query(
            cfg.legacy_dvbic_research_url,
            """
            SELECT DISTINCT c.table_name
            FROM information_schema.columns c
            WHERE c.table_schema = 'public'
              AND c.column_name IN ('subject_id', 'subjectid', 'clientid')
              AND c.table_name NOT LIKE 'django\\_%%' ESCAPE '\\'
              AND c.table_name NOT LIKE '\\_%%' ESCAPE '\\'
            """,
        )
        candidate_subject = {r[0] for r in rows_u}
        dvbic_report = _classify_dvbic(
            dvb_tables,
            with_stats=with_stats,
            stats=stats_dvbic,
            subject_id_tables=candidate_subject,
        )
    else:
        log.warning(
            "gap_report.dvbic_skipped — set LEGACY_DVBIC_RESEARCH_DATABASE_URL for dvbic_research inventory"
        )

    return {
        "arc": arc_report,
        "dvbic_research": dvbic_report,
        "notes": [
            "Rows_est comes from pg_stat_user_tables.n_live_tup when --with-stats is set (approximate).",
            "Arc gap_not_covered = public tables not in core ETL, not in ARC_INSTRUMENT_SPECS, and not classified as infrastructure.",
            "DVbic instrument pass includes tables with subject_id, subjectid, or clientid (MMPI / RF patterns).",
        ],
    }


def render_report(data: dict[str, Any], *, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(data, indent=2, default=str)

    lines: list[str] = []
    lines.append("=== Legacy gap report (read-only) ===\n")

    arc = data.get("arc") or {}
    s = arc.get("summary") or {}
    lines.append("--- ARC ---")
    lines.append(
        f"public_tables={s.get('public_tables')} | "
        f"covered_core={s.get('covered_core')} | "
        f"covered_other_etl={s.get('covered_other_etl')} | "
        f"covered_instrument_specs={s.get('covered_instrument_specs')} | "
        f"excluded_infrastructure={s.get('excluded_infrastructure')} | "
        f"GAP_not_covered={s.get('gap_not_covered')}"
    )
    gaps = arc.get("gap_not_covered") or []
    if gaps:
        lines.append("\nArc tables NOT covered by current CLI (review / add to ARC_INSTRUMENT_SPECS or new ETL):")
        for g in gaps:
            suf = f"  (~{g['rows_est']} rows est)" if "rows_est" in g else ""
            lines.append(f"  - {g['table']}{suf}")
    else:
        lines.append("\n(no Arc gap tables — unusual; verify legacy URL points at expected database)")

    dvb = data.get("dvbic_research")
    lines.append("")
    if not dvb:
        lines.append("--- dvbic_research ---\n(skipped: LEGACY_DVBIC_RESEARCH_DATABASE_URL not set)")
    else:
        s2 = dvb.get("summary") or {}
        lines.append("--- dvbic_research ---")
        lines.append(
            f"public_tables={s2.get('public_tables')} | "
            f"covered_explicit_etl={s2.get('covered_explicit_etl')} | "
            f"covered_subject_id_instruments={s2.get('covered_subject_id_instruments')} | "
            f"excluded_explicit_list={s2.get('excluded_explicit_list')} | "
            f"excluded_infrastructure={s2.get('excluded_infrastructure')} | "
            f"reference_lookups={s2.get('reference_lookups')} | "
            f"GAP_no_subject_id={s2.get('gap_no_subject_id_or_nonstandard')}"
        )
        gaps2 = dvb.get("gap_no_subject_id_or_nonstandard") or []
        if gaps2:
            lines.append(
                "\nDVbic tables NOT covered by explicit ETL or subject-key instrument pass "
                "(review / add registry join keys):"
            )
            for g in gaps2:
                suf = f"  (~{g['rows_est']} rows est)" if "rows_est" in g else ""
                lines.append(f"  - {g['table']}{suf}")
        else:
            lines.append("\n(no DVbic gap tables by this definition)")

    lines.append("")
    for n in data.get("notes") or []:
        lines.append(f"# {n}")
    return "\n".join(lines) + "\n"
