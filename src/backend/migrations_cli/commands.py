"""Subcommands for migrations_cli."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import bcrypt

from migrations_cli.config import MigrationConfig, masked_recruit_url
from migrations_cli.db import connect, run_query, run_scalar
from migrations_cli.etl_arc import (
    _migration_system_user_id,
    import_arc_auth_users,
    import_arc_studies,
    import_arc_study_acl_users,
    import_arc_studyproc_list,
    import_arc_subject_study,
    import_arc_subjects,
    import_arc_user_study,
    progress_summary,
)
from migrations_cli.etl_arc_instruments import import_arc_instrument_tables
from migrations_cli.etl_arc_proc import (
    import_arc_assessment_types,
    import_arc_proc_list,
    prune_duplicate_arc_proc_assessments,
)
from migrations_cli.etl_dvbic import (
    import_dvbic_session_notes,
    import_dvbic_studies,
    import_dvbic_subject_study,
    import_dvbic_subjects,
    import_dvbic_subjects2,
)
from migrations_cli.etl_dvbic_instruments import import_dvbic_instrument_tables
from migrations_cli.completeness import run_completeness
from migrations_cli.verify_import import (
    _DEFAULT_BASELINE,
    run_verify_import,
    write_baseline,
)
from migrations_cli.etl_deploy_audit import insert_migration_audit_log
from migrations_cli.gap_report import build_gap_report, render_report

log = logging.getLogger("migrations_cli")


def _j(data: dict) -> str:
    return json.dumps(data, default=str)


def cmd_set_user_password(cfg: MigrationConfig, email: str, password: str) -> int:
    """Set ``users.hashed_password`` for local/dev recovery (bcrypt)."""
    email_clean = (email or "").strip().lower()
    pwd = (password or "").strip()
    if not email_clean:
        log.error("set_user_password.missing_email")
        return 1
    if not pwd:
        log.error(
            "set_user_password.missing_password — pass plain text via RECRUIT_NEW_PASSWORD "
            "(do not commit): RECRUIT_NEW_PASSWORD='…' python -m migrations_cli set-user-password --email …"
        )
        return 1
    hashed = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt()).decode()
    with connect(cfg.database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE users
                SET hashed_password = %s, updated_at = NOW() AT TIME ZONE 'UTC'
                WHERE email = %s
                """,
                (hashed, email_clean),
            )
            updated = cur.rowcount
        conn.commit()
    if updated == 0:
        log.error("set_user_password.no_user %s", _j({"email": email_clean}))
        return 1
    log.info("set_user_password.done %s", _j({"email": email_clean}))
    print(f"Updated password for {email_clean!r}.")
    return 0


def cmd_preflight(cfg: MigrationConfig) -> int:
    log.info("preflight.start %s", _j({"recruit": masked_recruit_url(cfg)}))
    try:
        v = run_scalar(cfg.database_url, "SELECT version();")
        log.info("preflight.recruit_ok %s", _j({"version": str(v)[:120]}))
    except Exception as e:
        log.error("preflight.recruit_failed %s", _j({"error": str(e)}))
        return 1

    if cfg.legacy_arc_url:
        try:
            n = run_scalar(cfg.legacy_arc_url, "SELECT COUNT(*) FROM subj_list;")
            log.info("preflight.arc_ok %s", _j({"subj_list_rows": int(n)}))
        except Exception as e:
            log.error("preflight.arc_failed %s", _j({"error": str(e)}))
            return 1
    else:
        log.warning("preflight.arc_skipped (set LEGACY_ARC_DATABASE_URL for arc checks)")

    if cfg.legacy_dvbic_research_url:
        try:
            n = run_scalar(cfg.legacy_dvbic_research_url, "SELECT COUNT(*) FROM subjects;")
            log.info("preflight.dvbic_ok %s", _j({"subjects_rows": int(n)}))
        except Exception as e:
            log.error("preflight.dvbic_failed %s", _j({"error": str(e)}))
            return 1
    else:
        log.warning(
            "preflight.dvbic_skipped (set LEGACY_DVBIC_RESEARCH_DATABASE_URL for dvbic checks)"
        )

    if cfg.dry_run:
        log.info("preflight.dry_run %s", _j({"note": "No writes performed in preflight"}))
    log.info("preflight.done")
    return 0


def cmd_validate(cfg: MigrationConfig) -> int:
    log.info("validate.start %s", _j({"recruit": masked_recruit_url(cfg)}))
    try:
        rev = run_scalar(
            cfg.database_url,
            "SELECT version_num FROM alembic_version ORDER BY version_num DESC LIMIT 1;",
        )
        log.info("validate.alembic %s", _j({"head_revision": rev}))
        counts = run_query(
            cfg.database_url,
            """
            SELECT relname, n_live_tup::bigint
            FROM pg_stat_user_tables
            WHERE schemaname = 'public'
              AND relname IN (
                'users','studies','subjects','assessments','assessment_types','subject_study',
                'user_study','session_notes',
                'legacy_id_map','migration_events'
              )
            ORDER BY relname;
            """,
        )
        for name, n in counts:
            log.info("validate.table_estimate %s", _j({"table": name, "live_rows": int(n)}))
        has_map = run_scalar(cfg.database_url, "SELECT COUNT(*) FROM legacy_id_map;")
        has_events = run_scalar(cfg.database_url, "SELECT COUNT(*) FROM migration_events;")
        mig_user = run_scalar(
            cfg.database_url,
            "SELECT COUNT(*) FROM users WHERE email = 'migration-system@recruit.internal';",
        )
        log.info(
            "validate.summary %s",
            _j(
                {
                    "legacy_id_map_rows": int(has_map),
                    "migration_events_rows": int(has_events),
                    "migration_system_user": int(mig_user),
                }
            ),
        )
    except Exception as e:
        log.error("validate.failed %s", _j({"error": str(e)}))
        return 1
    log.info("validate.done")
    return 0


def cmd_legacy_stats(cfg: MigrationConfig) -> int:
    """Read-only vertical slice: core counts on `arc` (and optional dvbic)."""
    if not cfg.legacy_arc_url:
        log.error("legacy_stats.missing_arc_url")
        print(
            "LEGACY_ARC_DATABASE_URL is required for legacy-stats.\n"
            "Example (Docker host port to snapshot):\n"
            "  export LEGACY_ARC_DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:15432/arc",
            file=sys.stderr,
        )
        return 1
    log.info("legacy_stats.start")
    try:
        rows = run_query(
            cfg.legacy_arc_url,
            """
            SELECT 'study_desc' AS t, COUNT(*)::bigint FROM study_desc
            UNION ALL SELECT 'subj_list', COUNT(*) FROM subj_list
            UNION ALL SELECT 'study_list', COUNT(*) FROM study_list
            UNION ALL SELECT 'proc_list', COUNT(*) FROM proc_list
            UNION ALL SELECT 'auth_user', COUNT(*) FROM auth_user;
            """,
        )
        for t, n in rows:
            log.info("legacy_stats.arc %s", _j({"table": t, "rows": int(n)}))
            print(f"arc.{t}\t{int(n)}")
    except Exception as e:
        log.error("legacy_stats.arc_failed %s", _j({"error": str(e)}))
        return 1

    if cfg.legacy_dvbic_research_url:
        try:
            rows = run_query(
                cfg.legacy_dvbic_research_url,
                """
                SELECT 'subjects' AS t, COUNT(*)::bigint FROM subjects
                UNION ALL SELECT 'studies', COUNT(*) FROM studies;
                """,
            )
            for t, n in rows:
                log.info("legacy_stats.dvbic %s", _j({"table": t, "rows": int(n)}))
                print(f"dvbic_research.{t}\t{int(n)}")
        except Exception as e:
            log.error("legacy_stats.dvbic_failed %s", _j({"error": str(e)}))
            return 1

    log.info("legacy_stats.done")
    return 0


def cmd_import_arc_auth_users(cfg: MigrationConfig) -> int:
    return import_arc_auth_users(cfg)


def cmd_import_arc_studies(cfg: MigrationConfig) -> int:
    return import_arc_studies(cfg)


def cmd_progress_summary(cfg: MigrationConfig) -> int:
    return progress_summary(cfg)


def cmd_import_arc_subjects(cfg: MigrationConfig) -> int:
    return import_arc_subjects(cfg)


def cmd_import_arc_subject_study(cfg: MigrationConfig) -> int:
    return import_arc_subject_study(cfg)


def cmd_import_arc_studyproc_list(cfg: MigrationConfig) -> int:
    return import_arc_studyproc_list(cfg)


def cmd_import_arc_study_acl_users(cfg: MigrationConfig) -> int:
    return import_arc_study_acl_users(cfg)


def cmd_import_arc_user_study(cfg: MigrationConfig) -> int:
    return import_arc_user_study(cfg)


def cmd_migration_completeness(cfg: MigrationConfig, *, output_format: str) -> int:
    return run_completeness(cfg, output_format=output_format)


def cmd_migration_verify_baseline(cfg: MigrationConfig, *, baseline_path: str) -> int:
    path = Path(baseline_path) if baseline_path else _DEFAULT_BASELINE
    data = write_baseline(cfg, path)
    print(f"Wrote baseline: {path}")
    print(json.dumps({"counts": data.get("counts"), "alembic_head": data.get("alembic_head")}, indent=2))
    return 0


def cmd_migration_verify(
    cfg: MigrationConfig,
    *,
    baseline_path: str,
    tolerance: int,
    output_format: str,
) -> int:
    path = Path(baseline_path) if baseline_path else _DEFAULT_BASELINE
    if cmd_validate(cfg) != 0:
        return 1
    return run_verify_import(
        cfg,
        baseline_path=path,
        tolerance=tolerance,
        output_format=output_format,
    )


def cmd_import_dvbic_studies(cfg: MigrationConfig) -> int:
    return import_dvbic_studies(cfg)


def cmd_import_dvbic_subjects(cfg: MigrationConfig) -> int:
    return import_dvbic_subjects(cfg)


def cmd_import_dvbic_subjects2(cfg: MigrationConfig) -> int:
    return import_dvbic_subjects2(cfg)


def cmd_import_dvbic_subject_study(cfg: MigrationConfig) -> int:
    return import_dvbic_subject_study(cfg)


def cmd_import_dvbic_session_notes(cfg: MigrationConfig) -> int:
    return import_dvbic_session_notes(cfg)


def cmd_import_arc_assessment_types(cfg: MigrationConfig) -> int:
    return import_arc_assessment_types(cfg)


def cmd_import_arc_proc_list(cfg: MigrationConfig) -> int:
    return import_arc_proc_list(cfg)


def cmd_import_arc_instrument_tables(cfg: MigrationConfig) -> int:
    return import_arc_instrument_tables(cfg)


def cmd_import_dvbic_instrument_tables(cfg: MigrationConfig) -> int:
    return import_dvbic_instrument_tables(cfg)


def cmd_deploy_check(cfg: MigrationConfig) -> int:
    """Read-only gate: ``validate`` plus deploy-oriented counts and warnings."""
    if cmd_validate(cfg) != 0:
        return 1
    try:
        dup = run_scalar(
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
        print(f"deploy_check.duplicate_arc_proc_extra_rows_estimate: {int(dup)}")
        print(
            "  (Run `python -m migrations_cli prune-duplicate-arc-proc-assessments --apply` "
            "after backup if non-zero.)"
        )
        ev = run_scalar(cfg.database_url, "SELECT COUNT(*)::bigint FROM migration_events")
        print(f"deploy_check.migration_events_rows: {int(ev)}")
        log.info("deploy_check.done %s", json.dumps({"duplicate_arc_proc_extras": int(dup)}))
    except Exception as e:
        log.error("deploy_check.failed %s", json.dumps({"error": str(e)}))
        return 1
    return 0


def cmd_record_migration_audit(cfg: MigrationConfig, summary: str) -> int:
    """Write one ``audit_logs`` row (migration system user) for go-live / phase milestones."""
    if cfg.dry_run:
        log.info("record_migration_audit.dry_run %s", json.dumps({"summary": summary}))
        print("Dry-run: no audit_logs row written.")
        return 0
    import psycopg2

    recruit = psycopg2.connect(cfg.database_url)
    try:
        r_cur = recruit.cursor()
        mig_uid = _migration_system_user_id(r_cur)
        insert_migration_audit_log(
            r_cur,
            mig_uid,
            action="MIGRATION",
            entity_type="bulk_import",
            entity_id=0,
            change_summary=summary,
            additional_context={
                "migration_batch_id": cfg.migration_batch_id,
                "tool": "migrations_cli record-migration-audit",
            },
        )
        recruit.commit()
        log.info("record_migration_audit.done")
        print("Wrote audit_logs row (migration system user).")
        return 0
    except Exception:
        recruit.rollback()
        raise
    finally:
        recruit.close()


def cmd_prune_duplicate_arc_proc_assessments(cfg: MigrationConfig, *, apply: bool) -> int:
    return prune_duplicate_arc_proc_assessments(cfg, apply=apply)


def cmd_legacy_gap_report(cfg: MigrationConfig, *, output_format: str, with_stats: bool) -> int:
    """Print Arc / dvbic_research public table coverage vs current migrations_cli importers (read-only)."""
    data = build_gap_report(cfg, with_stats=with_stats)
    print(render_report(data, output_format=output_format), end="")
    return 0
