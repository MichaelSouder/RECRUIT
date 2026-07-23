"""argparse entry point for the air-gap tooling. Invoked via the
`scripts/airgap-cli` launcher, e.g.:

    scripts/airgap-cli stack-up --recreate-app
    scripts/airgap-cli cron-update --dry-run
    scripts/airgap-cli install-cron
"""

from __future__ import annotations

import argparse
import os
import sys
import traceback
from pathlib import Path

from . import autoupdate, bundle, cron_install, logging_utils, prune, stack
from .engine import ContainerEngine
from .errors import AirgapError

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _default_bundle_dir(start: Path | None = None) -> Path:
    root = start or REPO_ROOT
    for candidate in (root / "output" / "container-images", root / "container-images"):
        if (candidate / "recruit-backend.tar").is_file() or (candidate / "MANIFEST.txt").is_file():
            return candidate
    raise AirgapError(
        "No bundle directory given, and none found at output/container-images/ or container-images/.",
        remediation="Pass a bundle directory explicitly.",
    )


def _resolve_bundle_dir(arg: str | None) -> Path:
    return Path(arg).expanduser().resolve() if arg else _default_bundle_dir()


def _add_common_bundle_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("bundle_dir", nargs="?", default=None, help="Bundle directory (default: auto-detect)")
    parser.add_argument("--dry-run", action="store_true", help="Print actions only, make no changes")
    parser.add_argument("--engine", choices=["docker", "podman"], default=None, help="Force container engine")
    parser.add_argument("--env-file", default=None, help="KEY=value env file (default: <bundle>/recruit-airgap.env)")


def _cmd_update_containers(args: argparse.Namespace) -> int:
    bundle_dir = _resolve_bundle_dir(args.bundle_dir)
    logging_utils.log_info(f"Bundle: {bundle_dir}")
    engine = ContainerEngine.detect(prefer=args.engine)
    logging_utils.log_ok(f"Using container engine: {engine.name}")
    bundle.apply_bundle(bundle_dir, engine=engine, dry_run=args.dry_run, env_file=args.env_file)
    logging_utils.log_ok("Update complete.")
    return 0


def _cmd_prune_images(args: argparse.Namespace) -> int:
    bundle_dir = _resolve_bundle_dir(args.bundle_dir)
    engine = ContainerEngine.detect(prefer=args.engine)
    prune.prune_old_images(bundle_dir, engine, keep_old_tags=args.keep, dry_run=args.dry_run)
    return 0


def _cmd_stack_up(args: argparse.Namespace) -> int:
    bundle_dir = _resolve_bundle_dir(args.bundle_dir)
    result = stack.stack_up(
        bundle_dir,
        recreate_app=args.recreate_app,
        dry_run=args.dry_run,
        env_file=args.env_file,
        engine=ContainerEngine.detect(prefer=args.engine) if args.engine else None,
    )
    if not args.dry_run and not all(result.values()):
        return 1
    return 0


def _cmd_cron_update(args: argparse.Namespace) -> int:
    repo_dir = Path(args.repo_dir).expanduser().resolve() if args.repo_dir else REPO_ROOT
    health = autoupdate.HealthCheckConfig(
        backend_publish=args.backend_publish,
        frontend_publish=args.frontend_publish,
        http_check_timeout=args.http_check_timeout,
        retries=args.health_retries,
        retry_delay_sec=args.health_retry_delay_sec,
    )
    try:
        autoupdate.cron_update(
            repo_dir=repo_dir,
            remote=args.remote,
            branch=args.branch,
            lock_file=args.lock_file,
            health=health,
            skip_prune=args.skip_prune,
            keep_old_tags=args.keep,
            dry_run=args.dry_run,
            docker_cmd=args.engine,
        )
    except AirgapError as exc:
        if exc.exit_code == 0:
            # Lock contention: skip this run silently (same as bash's exit 0).
            logging_utils.log_warn(str(exc))
            return 0
        raise
    return 0


def _cmd_install_cron(args: argparse.Namespace) -> int:
    launcher = Path(args.launcher).expanduser().resolve() if args.launcher else (REPO_ROOT / "scripts" / "airgap-cli")
    cron_install.install_cron(launcher_path=launcher, schedule=args.schedule, log_file=args.log_file)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="airgap-cli", description="RECRUIT air-gap deploy/update tooling.")
    parser.add_argument("--debug", action="store_true", help="Trace subprocess calls and show full tracebacks")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("update-containers", help="Load a bundle's images and recreate backend/frontend")
    _add_common_bundle_args(p)
    p.set_defaults(func=_cmd_update_containers)

    p = sub.add_parser("prune-images", help="Remove old backend/frontend image tags")
    _add_common_bundle_args(p)
    p.add_argument("--keep", type=int, default=1, help="Old tags to keep beyond the running one (default: 1)")
    p.set_defaults(func=_cmd_prune_images)

    p = sub.add_parser("stack-up", help="Bring up (or reconcile) the full stack from a bundle")
    _add_common_bundle_args(p)
    p.add_argument("--recreate-app", action="store_true", help="Remove/recreate backend+frontend only")
    p.set_defaults(func=_cmd_stack_up)

    p = sub.add_parser("cron-update", help="Unattended update: fetch, roll out if changed, health-check, prune")
    p.add_argument("--repo-dir", default=None, help="Deploy-only clone root (default: this checkout)")
    p.add_argument("--remote", default="origin")
    p.add_argument("--branch", default="main")
    p.add_argument("--lock-file", default=autoupdate.DEFAULT_LOCK_FILE)
    p.add_argument("--backend-publish", default="18000:8000")
    p.add_argument("--frontend-publish", default="18080:80")
    p.add_argument("--http-check-timeout", type=float, default=10)
    p.add_argument("--health-retries", type=int, default=10)
    p.add_argument("--health-retry-delay-sec", type=float, default=3)
    p.add_argument("--skip-prune", action="store_true")
    p.add_argument("--keep", type=int, default=1)
    p.add_argument("--engine", choices=["docker", "podman"], default=None)
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=_cmd_cron_update)

    p = sub.add_parser("install-cron", help="Install the hourly cron-update job into crontab")
    p.add_argument("--launcher", default=None, help="Path to the airgap-cli launcher (default: this checkout's)")
    p.add_argument("--schedule", default=cron_install.DEFAULT_SCHEDULE)
    p.add_argument("--log-file", default=cron_install.DEFAULT_LOG_FILE)
    p.set_defaults(func=_cmd_install_cron)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging_utils.set_debug(args.debug or bool(os.environ.get("AIRGAP_DEBUG")))
    try:
        return args.func(args)
    except AirgapError as exc:
        # exit_code 0 (e.g. LockHeldError) is intentionally benign -- `or 1`
        # would wrongly collapse it to a failure, so check for None instead.
        if exc.exit_code == 0:
            logging_utils.log_warn(exc.message)
            return 0
        logging_utils.log_err(exc.message)
        if exc.context:
            logging_utils.log_info(f"Context: {exc.context}")
        if exc.remediation:
            logging_utils.log_info(exc.remediation)
        return exc.exit_code if exc.exit_code is not None else 1
    except KeyboardInterrupt:
        logging_utils.log_warn("Interrupted.")
        return 130
    except Exception:
        logging_utils.log_err("Unexpected error.")
        if logging_utils.is_debug():
            traceback.print_exc()
        else:
            logging_utils.log_info("Re-run with --debug for a full traceback.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
