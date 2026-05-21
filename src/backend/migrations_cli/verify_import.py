"""Post-restore verification: compare RECRUIT DB to a saved baseline (no legacy DB required)."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from migrations_cli.config import MigrationConfig
from migrations_cli.db import run_query, run_scalar

log = logging.getLogger("migrations_cli")

# Default baseline path (repo root / data / …) when run from src/backend
_DEFAULT_BASELINE = (
    Path(__file__).resolve().parents[3] / "data" / "migration_verify_baseline.json"
)

# (key, SQL, minimum for pass — used when comparing without exact baseline field)
_MINIMUM_CHECKS: list[tuple[str, str, int]] = [
    ("subjects", "SELECT COUNT(*)::bigint FROM subjects", 55_000),
    ("studies", "SELECT COUNT(*)::bigint FROM studies", 50),
    ("assessments", "SELECT COUNT(*)::bigint FROM assessments", 370_000),
    ("legacy_id_map", "SELECT COUNT(*)::bigint FROM legacy_id_map", 430_000),
    ("session_notes", "SELECT COUNT(*)::bigint FROM session_notes", 4_350),
    ("study_procedures", "SELECT COUNT(*)::bigint FROM study_procedures", 160),
    ("user_study", "SELECT COUNT(*)::bigint FROM user_study", 100),
    ("users", "SELECT COUNT(*)::bigint FROM users", 30),
    ("subject_study", "SELECT COUNT(*)::bigint FROM subject_study", 5_800),
]


def _alembic_head(cfg: MigrationConfig) -> str | None:
    try:
        row = run_query(
            cfg.database_url,
            "SELECT version_num FROM alembic_version LIMIT 1",
        )
        return str(row[0][0]) if row else None
    except Exception:
        return None


def _duplicate_arc_proc_extras(cfg: MigrationConfig) -> int:
    return int(
        run_scalar(
            cfg.database_url,
            """
            WITH x AS (
              SELECT data->>'proc_num' AS pn, COUNT(*)::bigint AS c
              FROM assessments
              WHERE assessment_type LIKE 'arc-proc-%%' AND (data::jsonb) ? 'proc_num'
              GROUP BY 1
            )
            SELECT COALESCE(SUM(c - 1), 0)::bigint FROM x WHERE c > 1
            """,
        )
        or 0
    )


def _legacy_map_by_source(cfg: MigrationConfig) -> dict[str, int]:
    rows = run_query(
        cfg.database_url,
        """
        SELECT source_system || '/' || source_table, COUNT(*)::bigint
        FROM legacy_id_map
        GROUP BY 1
        ORDER BY 1
        """,
    )
    return {str(r[0]): int(r[1]) for r in rows}


def _cutover_audit_present(cfg: MigrationConfig) -> bool:
    n = int(
        run_scalar(
            cfg.database_url,
            """
            SELECT COUNT(*)::bigint FROM audit_logs
            WHERE change_summary ILIKE '%%Tier 1 spine complete%%'
               OR change_summary ILIKE '%%prod cutover%%'
            """,
        )
        or 0
    )
    return n > 0


def build_verify_baseline(cfg: MigrationConfig) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for key, sql, _min in _MINIMUM_CHECKS:
        counts[key] = int(run_scalar(cfg.database_url, sql) or 0)

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": "Compare prod DB after pg_restore with: python -m migrations_cli migration-verify",
        "alembic_head": _alembic_head(cfg),
        "counts": counts,
        "legacy_id_map_by_source": _legacy_map_by_source(cfg),
        "duplicate_arc_proc_extras": _duplicate_arc_proc_extras(cfg),
        "cutover_audit_log_present": _cutover_audit_present(cfg),
        "migration_events_rows": int(
            run_scalar(cfg.database_url, "SELECT COUNT(*)::bigint FROM migration_events") or 0
        ),
    }


def write_baseline(cfg: MigrationConfig, path: Path) -> dict[str, Any]:
    data = build_verify_baseline(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    log.info("migration_verify_baseline.wrote %s", json.dumps({"path": str(path)}))
    return data


def _compare_counts(
    actual: dict[str, int],
    expected: dict[str, int],
    *,
    tolerance: int,
) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for key, exp in expected.items():
        act = actual.get(key)
        if act is None:
            failures.append({"check": key, "error": "missing in database"})
            continue
        if abs(act - exp) > tolerance:
            failures.append(
                {
                    "check": key,
                    "expected": exp,
                    "actual": act,
                    "delta": act - exp,
                    "tolerance": tolerance,
                }
            )
    return failures


def run_verify_import(
    cfg: MigrationConfig,
    *,
    baseline_path: Path,
    tolerance: int,
    output_format: str,
) -> int:
    if not baseline_path.is_file():
        raise SystemExit(
            f"Baseline file not found: {baseline_path}\n"
            "Generate on the source DB before cutover:\n"
            "  python -m migrations_cli migration-verify-baseline"
        )

    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    current = build_verify_baseline(cfg)
    failures: list[dict[str, Any]] = []

    exp_head = baseline.get("alembic_head")
    act_head = current.get("alembic_head")
    if exp_head and act_head != exp_head:
        failures.append(
            {"check": "alembic_head", "expected": exp_head, "actual": act_head}
        )

    failures.extend(
        _compare_counts(
            current.get("counts") or {},
            baseline.get("counts") or {},
            tolerance=tolerance,
        )
    )

    dup = current.get("duplicate_arc_proc_extras", 0)
    if dup != 0:
        failures.append(
            {
                "check": "duplicate_arc_proc_extras",
                "expected": 0,
                "actual": dup,
            }
        )

    for key, _sql, minimum in _MINIMUM_CHECKS:
        act = (current.get("counts") or {}).get(key, 0)
        if act < minimum:
            failures.append(
                {
                    "check": f"{key}_minimum",
                    "minimum": minimum,
                    "actual": act,
                }
            )

    report: dict[str, Any] = {
        "status": "PASS" if not failures else "FAIL",
        "baseline_file": str(baseline_path),
        "baseline_generated_at": baseline.get("generated_at"),
        "current_generated_at": current.get("generated_at"),
        "failures": failures,
        "current": current,
    }

    if output_format == "json":
        print(json.dumps(report, indent=2, default=str))
    else:
        lines = [
            "=== Migration verify (post-restore) ===",
            f"Baseline: {baseline_path} ({baseline.get('generated_at', '?')})",
            f"Status: {report['status']}",
            "",
        ]
        if failures:
            lines.append("Failures:")
            for f in failures:
                lines.append(f"  - {json.dumps(f, default=str)}")
        else:
            lines.append("All checks passed.")
            lines.append("")
            lines.append("Key counts on this database:")
            for k, v in sorted((current.get("counts") or {}).items()):
                lines.append(f"  {k}: {v}")
        print("\n".join(lines))

    log.info(
        "migration_verify.done %s",
        json.dumps({"status": report["status"], "failure_count": len(failures)}),
    )
    return 0 if not failures else 1
