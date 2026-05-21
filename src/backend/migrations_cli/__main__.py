"""Entry point: python -m migrations_cli"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time

from migrations_cli import __version__
from migrations_cli.commands import (
    cmd_deploy_check,
    cmd_import_arc_assessment_types,
    cmd_import_arc_auth_users,
    cmd_import_arc_instrument_tables,
    cmd_import_arc_proc_list,
    cmd_import_arc_studies,
    cmd_import_arc_studyproc_list,
    cmd_import_arc_subject_study,
    cmd_import_arc_subjects,
    cmd_import_arc_study_acl_users,
    cmd_import_arc_user_study,
    cmd_migration_completeness,
    cmd_migration_verify,
    cmd_migration_verify_baseline,
    cmd_import_dvbic_instrument_tables,
    cmd_import_dvbic_session_notes,
    cmd_import_dvbic_studies,
    cmd_import_dvbic_subject_study,
    cmd_import_dvbic_subjects,
    cmd_import_dvbic_subjects2,
    cmd_legacy_gap_report,
    cmd_legacy_stats,
    cmd_prune_duplicate_arc_proc_assessments,
    cmd_preflight,
    cmd_progress_summary,
    cmd_record_migration_audit,
    cmd_set_user_password,
    cmd_validate,
)
from migrations_cli.config import load_config


class JsonLogFormatter(logging.Formatter):
    """One JSON object per line for log aggregation."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(payload, default=str)


def _setup_logging(*, json_logs: bool) -> logging.Logger:
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    h = logging.StreamHandler(sys.stdout)
    if json_logs:
        h.setFormatter(JsonLogFormatter())
    else:
        h.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    root.handlers.clear()
    root.addHandler(h)
    return logging.getLogger("migrations_cli")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="migrations_cli", description=__doc__)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="For import commands: log work but roll back RECRUIT writes.",
    )
    parser.add_argument(
        "--json-logs",
        action="store_true",
        help="Emit structured JSON lines to stdout.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_pre = sub.add_parser("preflight", help="Check DATABASE_URL and optional legacy URLs.")
    p_val = sub.add_parser("validate", help="Check RECRUIT DB alembic head and row estimates.")
    sub.add_parser(
        "deploy-check",
        help="validate plus deploy warnings (e.g. duplicate arc proc_list assessments).",
    )
    p_stats = sub.add_parser(
        "legacy-stats",
        help="Print core table row counts from legacy arc (and dvbic if URL set).",
    )
    p_gap = sub.add_parser(
        "legacy-gap-report",
        help="Inventory Arc + dvbic_research public tables vs current migrations_cli coverage (read-only).",
    )
    p_gap.add_argument(
        "--output-format",
        choices=("text", "json"),
        default="text",
        help="text (default) or machine-readable json.",
    )
    p_gap.add_argument(
        "--with-stats",
        action="store_true",
        help="Include pg_stat_user_tables.n_live_tup estimates per table (approximate).",
    )
    sub.add_parser(
        "import-arc-auth-users",
        help="Copy arc.auth_user into RECRUIT users + legacy_id_map (requires MIGRATION_BATCH_ID unless --dry-run).",
    )
    sub.add_parser(
        "import-arc-studies",
        help="Copy arc.study_desc into RECRUIT studies + legacy_id_map (requires MIGRATION_BATCH_ID unless --dry-run).",
    )
    sub.add_parser(
        "import-arc-subjects",
        help="Copy arc.subj_list into RECRUIT subjects + legacy_id_map.",
    )
    sub.add_parser(
        "import-arc-subject-study",
        help="Copy arc.study_list into RECRUIT subject_study (needs arc maps for subjects + studies).",
    )
    sub.add_parser(
        "import-arc-studyproc-list",
        help="Copy arc.studyproc_list into RECRUIT study_procedures + legacy_id_map (needs import-arc-studies map).",
    )
    sub.add_parser(
        "import-arc-study-acl-users",
        help="Create stub RECRUIT users for study_acl.usr not in arc.auth_user (run before import-arc-user-study).",
    )
    sub.add_parser(
        "import-arc-user-study",
        help="Copy arc.study_acl into RECRUIT user_study (needs auth maps and/or import-arc-study-acl-users).",
    )
    p_complete = sub.add_parser(
        "migration-completeness",
        help="Read-only spine counts vs legacy + gap table totals (cutover gate).",
    )
    p_complete.add_argument(
        "--output-format",
        choices=("text", "json"),
        default="text",
    )
    p_vbase = sub.add_parser(
        "migration-verify-baseline",
        help="Write data/migration_verify_baseline.json from current RECRUIT DB (before pg_dump).",
    )
    p_vbase.add_argument(
        "--baseline",
        default="",
        help="Output path (default: repo data/migration_verify_baseline.json).",
    )
    p_verify = sub.add_parser(
        "migration-verify",
        help="After prod pg_restore: compare DB to baseline (needs only DATABASE_URL).",
    )
    p_verify.add_argument(
        "--baseline",
        default="",
        help="Baseline JSON path (default: repo data/migration_verify_baseline.json).",
    )
    p_verify.add_argument(
        "--tolerance",
        type=int,
        default=0,
        help="Allowed absolute delta per count vs baseline (default 0).",
    )
    p_verify.add_argument(
        "--output-format",
        choices=("text", "json"),
        default="text",
    )
    sub.add_parser(
        "import-arc-assessment-types",
        help="Create RECRUIT assessment_types from arc.proc_desc (run before import-arc-proc-list).",
    )
    sub.add_parser(
        "import-arc-proc-list",
        help="Copy arc.proc_list into RECRUIT assessments + legacy_id_map (needs types + subject maps).",
    )
    sub.add_parser(
        "import-arc-instrument-tables",
        help="Copy configured arc instrument tables into assessments (full row JSON) + migration_events on orphans.",
    )
    sub.add_parser(
        "import-dvbic-studies",
        help="Copy dvbic_research.studies into RECRUIT studies + legacy_id_map.",
    )
    sub.add_parser(
        "import-dvbic-subjects",
        help="Copy dvbic_research.subjects into RECRUIT subjects + legacy_id_map.",
    )
    sub.add_parser(
        "import-dvbic-subjects2",
        help="Copy dvbic_research.subjects2 into RECRUIT subjects + legacy_id_map (subjects2 keys; run after subjects).",
    )
    sub.add_parser(
        "import-dvbic-subject-study",
        help="Infer DVbic subject↔study links from legacy tables → RECRUIT subject_study (needs DVbic maps).",
    )
    sub.add_parser(
        "import-dvbic-session-notes",
        help="Copy dvbic_research.session_notes into RECRUIT session_notes + legacy_id_map.",
    )
    sub.add_parser(
        "import-dvbic-instrument-tables",
        help="Copy dvbic_research tables with subject_id/subjectid/clientid into assessments (streams large tables).",
    )
    sub.add_parser(
        "progress-summary",
        help="Print RECRUIT pg_stat estimates and latest legacy_id_map rows.",
    )
    p_prune = sub.add_parser(
        "prune-duplicate-arc-proc-assessments",
        help="Dry-run: count duplicate arc-proc-* rows per proc_num; use --apply to delete extras (after backup).",
    )
    p_prune.add_argument(
        "--apply",
        action="store_true",
        help="Delete duplicate assessments and repoint legacy_id_map when needed (ignored with --dry-run).",
    )
    p_audit = sub.add_parser(
        "record-migration-audit",
        help="Append one audit_logs row for a migration milestone (migration system user).",
    )
    p_audit.add_argument(
        "summary",
        nargs="*",
        default=["Legacy migration milestone recorded."],
        help="Summary text (default if omitted).",
    )
    p_pw = sub.add_parser(
        "set-user-password",
        help="Set bcrypt password for one user (password from RECRUIT_NEW_PASSWORD env var).",
    )
    p_pw.add_argument(
        "--email",
        required=True,
        help="User email (matched case-insensitively after lowercasing).",
    )

    args = parser.parse_args(argv)
    _setup_logging(json_logs=args.json_logs)
    log = logging.getLogger("migrations_cli")

    try:
        cfg = load_config(dry_run=args.dry_run)
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 1

    if args.command == "preflight":
        return cmd_preflight(cfg)
    if args.command == "validate":
        return cmd_validate(cfg)
    if args.command == "deploy-check":
        return cmd_deploy_check(cfg)
    if args.command == "legacy-stats":
        return cmd_legacy_stats(cfg)
    if args.command == "legacy-gap-report":
        return cmd_legacy_gap_report(
            cfg,
            output_format=args.output_format,
            with_stats=args.with_stats,
        )
    if args.command == "import-arc-auth-users":
        return cmd_import_arc_auth_users(cfg)
    if args.command == "import-arc-studies":
        return cmd_import_arc_studies(cfg)
    if args.command == "import-arc-subjects":
        return cmd_import_arc_subjects(cfg)
    if args.command == "import-arc-subject-study":
        return cmd_import_arc_subject_study(cfg)
    if args.command == "import-arc-studyproc-list":
        return cmd_import_arc_studyproc_list(cfg)
    if args.command == "import-arc-study-acl-users":
        return cmd_import_arc_study_acl_users(cfg)
    if args.command == "import-arc-user-study":
        return cmd_import_arc_user_study(cfg)
    if args.command == "migration-completeness":
        return cmd_migration_completeness(cfg, output_format=args.output_format)
    if args.command == "migration-verify-baseline":
        return cmd_migration_verify_baseline(cfg, baseline_path=args.baseline)
    if args.command == "migration-verify":
        return cmd_migration_verify(
            cfg,
            baseline_path=args.baseline,
            tolerance=args.tolerance,
            output_format=args.output_format,
        )
    if args.command == "import-arc-assessment-types":
        return cmd_import_arc_assessment_types(cfg)
    if args.command == "import-arc-proc-list":
        return cmd_import_arc_proc_list(cfg)
    if args.command == "import-arc-instrument-tables":
        return cmd_import_arc_instrument_tables(cfg)
    if args.command == "import-dvbic-studies":
        return cmd_import_dvbic_studies(cfg)
    if args.command == "import-dvbic-subjects":
        return cmd_import_dvbic_subjects(cfg)
    if args.command == "import-dvbic-subjects2":
        return cmd_import_dvbic_subjects2(cfg)
    if args.command == "import-dvbic-subject-study":
        return cmd_import_dvbic_subject_study(cfg)
    if args.command == "import-dvbic-session-notes":
        return cmd_import_dvbic_session_notes(cfg)
    if args.command == "import-dvbic-instrument-tables":
        return cmd_import_dvbic_instrument_tables(cfg)
    if args.command == "progress-summary":
        return cmd_progress_summary(cfg)
    if args.command == "prune-duplicate-arc-proc-assessments":
        return cmd_prune_duplicate_arc_proc_assessments(cfg, apply=args.apply)
    if args.command == "record-migration-audit":
        summary = " ".join(args.summary).strip() or "Legacy migration milestone recorded."
        return cmd_record_migration_audit(cfg, summary)
    if args.command == "set-user-password":
        return cmd_set_user_password(cfg, args.email, os.environ.get("RECRUIT_NEW_PASSWORD", ""))
    log.error("unknown_command %s", args.command)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
