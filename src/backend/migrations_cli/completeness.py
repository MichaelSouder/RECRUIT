"""Read-only migration completeness summary for cutover gates."""

from __future__ import annotations

import json
import logging
from typing import Any

from migrations_cli.config import MigrationConfig
from migrations_cli.db import run_query, run_scalar
from migrations_cli.gap_report import build_gap_report

log = logging.getLogger("migrations_cli")


def _count_pair(
    cfg: MigrationConfig,
    *,
    legacy_sql: str,
    recruit_sql: str,
    legacy_url: str | None = None,
) -> tuple[int | None, int | None]:
    url = legacy_url or cfg.database_url
    try:
        legacy_n = int(run_scalar(url, legacy_sql) or 0)
    except Exception:
        legacy_n = None
    try:
        recruit_n = int(run_scalar(cfg.database_url, recruit_sql) or 0)
    except Exception:
        recruit_n = None
    return legacy_n, recruit_n


def build_completeness_report(cfg: MigrationConfig) -> dict[str, Any]:
    report: dict[str, Any] = {"database_url_masked": cfg.database_url.split("@")[-1] if "@" in cfg.database_url else ""}

    spine: list[dict[str, Any]] = []

    if cfg.legacy_arc_url:
        pairs = [
            ("arc.auth_user → users", "SELECT COUNT(*) FROM auth_user", "SELECT COUNT(*) FROM legacy_id_map WHERE source_system='arc' AND source_table='auth_user'"),
            ("arc.subj_list → subjects", "SELECT COUNT(*) FROM subj_list", "SELECT COUNT(*) FROM legacy_id_map WHERE source_system='arc' AND source_table='subj_list'"),
            ("arc.proc_list → assessments", "SELECT COUNT(*) FROM proc_list", "SELECT COUNT(*) FROM legacy_id_map WHERE source_system='arc' AND source_table='proc_list'"),
            ("arc.studyproc_list → study_procedures", "SELECT COUNT(*) FROM studyproc_list", "SELECT COUNT(*) FROM study_procedures"),
            ("arc.study_acl → user_study", "SELECT COUNT(*) FROM study_acl WHERE usr IS NOT NULL", "SELECT COUNT(*) FROM user_study"),
        ]
        for label, leg, rec in pairs:
            ln, rn = _count_pair(cfg, legacy_sql=leg, recruit_sql=rec, legacy_url=cfg.legacy_arc_url)
            spine.append(
                {
                    "check": label,
                    "legacy_count": ln,
                    "recruit_count": rn,
                    "gap": (ln - rn) if ln is not None and rn is not None else None,
                }
            )
        acl_stub = int(
            run_scalar(
                cfg.database_url,
                "SELECT COUNT(*) FROM legacy_id_map WHERE source_system='arc' AND source_table='study_acl_user'",
            )
            or 0
        )
        spine.append({"check": "arc.study_acl_user stub maps", "recruit_count": acl_stub})

    if cfg.legacy_dvbic_research_url:
        pairs_d = [
            ("dvbic.subjects → map", "SELECT COUNT(*) FROM subjects", "SELECT COUNT(*) FROM legacy_id_map WHERE source_system='dvbic_research' AND source_table='subjects'"),
            ("dvbic.subjects2 → map", "SELECT COUNT(*) FROM subjects2", "SELECT COUNT(*) FROM legacy_id_map WHERE source_system='dvbic_research' AND source_table='subjects2'"),
            (
                "dvbic.session_notes → session_notes",
                "SELECT COUNT(*) FROM session_notes",
                "SELECT COUNT(*) FROM legacy_id_map WHERE source_system='dvbic_research' AND source_table='session_notes_recruit'",
            ),
        ]
        for label, leg, rec in pairs_d:
            ln, rn = _count_pair(cfg, legacy_sql=leg, recruit_sql=rec, legacy_url=cfg.legacy_dvbic_research_url)
            spine.append(
                {
                    "check": label,
                    "legacy_count": ln,
                    "recruit_count": rn,
                    "gap": (ln - rn) if ln is not None and rn is not None else None,
                }
            )

    report["spine_checks"] = spine

    try:
        gap = build_gap_report(cfg, with_stats=False)
        report["arc_gap_tables"] = len((gap.get("arc") or {}).get("gap_not_covered") or [])
        dvb = gap.get("dvbic_research") or {}
        report["dvbic_gap_tables"] = len(dvb.get("gap_no_subject_id_or_nonstandard") or [])
    except Exception as e:
        report["gap_report_error"] = str(e)

    me = int(run_scalar(cfg.database_url, "SELECT COUNT(*) FROM migration_events") or 0)
    report["migration_events_rows"] = me

    report["next_commands"] = [
        "import-arc-study-acl-users  # if study_acl → user_study gap > 0",
        "import-arc-user-study",
        "import-dvbic-subjects2  # if session_notes gap > 0",
        "import-dvbic-session-notes",
        "legacy-gap-report --with-stats",
        "deploy-check",
    ]
    return report


def format_completeness_text(data: dict[str, Any]) -> str:
    lines = ["=== Migration completeness (read-only) ===", ""]
    for row in data.get("spine_checks") or []:
        check = row.get("check", "?")
        leg = row.get("legacy_count")
        rec = row.get("recruit_count")
        gap = row.get("gap")
        if leg is not None and rec is not None:
            flag = " OK" if gap == 0 else f" GAP={gap}"
            lines.append(f"  {check}: legacy={leg} recruit={rec}{flag}")
        else:
            lines.append(f"  {check}: recruit={rec}")
    lines.append("")
    lines.append(
        f"  Arc tables without ETL: {data.get('arc_gap_tables', '?')} | "
        f"DVbic tables without subject-key pass: {data.get('dvbic_gap_tables', '?')}"
    )
    lines.append(f"  migration_events rows: {data.get('migration_events_rows', '?')}")
    lines.append("")
    lines.append("Suggested next CLI commands:")
    for cmd in data.get("next_commands") or []:
        lines.append(f"  python -m migrations_cli {cmd}")
    return "\n".join(lines)


def run_completeness(cfg: MigrationConfig, *, output_format: str) -> int:
    data = build_completeness_report(cfg)
    if output_format == "json":
        print(json.dumps(data, indent=2, default=str))
    else:
        print(format_completeness_text(data))
    log.info("migration_completeness.done %s", json.dumps({"format": output_format}))
    return 0
