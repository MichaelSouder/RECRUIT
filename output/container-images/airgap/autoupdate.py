"""Port of airgap-cron-update.sh: the hourly unattended-update entry point.

Fetches the tracked branch, fast-forward-only merges (never resets -- this
clone is deploy-only and must never diverge), pulls LFS objects, and only if
`output/container-images/` actually changed between old and new HEAD does it
roll out an update: load the new images, recreate backend/frontend, health
check, then either prune the old images (success) or leave them in place
with rollback instructions printed (failure).

A single-instance flock prevents overlapping runs; contention is treated as
benign (skip this hour, try next hour), not an error.
"""

from __future__ import annotations

import contextlib
import fcntl
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from . import bundle as bundle_module
from . import logging_utils
from . import prune as prune_module
from . import stack as stack_module
from .engine import ContainerEngine
from .errors import AirgapError, GitDivergedError, HealthCheckError, LockHeldError

BUNDLE_SUBDIR = "output/container-images"
DEFAULT_LOCK_FILE = "/tmp/recruit-airgap-cron-update.lock"

RunFn = Callable[..., "subprocess.CompletedProcess[str]"]


@contextlib.contextmanager
def _acquire_lock(lock_file: Path):
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(lock_file), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        raise LockHeldError(
            f"Another run is already in progress (lock: {lock_file}). Exiting.",
        ) from None
    try:
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def _git(repo_dir: Path, args: list[str], *, run_fn: RunFn) -> "subprocess.CompletedProcess[str]":
    argv = ["git", *args]
    logging_utils.log_cmd(argv)
    result = run_fn(argv, cwd=str(repo_dir), capture_output=True, text=True)
    if result.returncode != 0:
        logging_utils.log_cmd_failure(argv, result.returncode, result.stderr)
    return result


def _current_branch(repo_dir: Path, run_fn: RunFn) -> str:
    return _git(repo_dir, ["rev-parse", "--abbrev-ref", "HEAD"], run_fn=run_fn).stdout.strip()


def _rev_parse(repo_dir: Path, ref: str, run_fn: RunFn) -> str:
    return _git(repo_dir, ["rev-parse", ref], run_fn=run_fn).stdout.strip()


def _lfs_available(repo_dir: Path, run_fn: RunFn) -> bool:
    return _git(repo_dir, ["lfs", "version"], run_fn=run_fn).returncode == 0


def _bundle_changed(repo_dir: Path, old: str, new: str, run_fn: RunFn) -> bool:
    result = _git(repo_dir, ["diff", "--quiet", old, new, "--", BUNDLE_SUBDIR], run_fn=run_fn)
    return result.returncode != 0


def _ff_only_merge(repo_dir: Path, remote: str, branch: str, run_fn: RunFn) -> None:
    result = _git(repo_dir, ["merge", "--ff-only", f"{remote}/{branch}"], run_fn=run_fn)
    if result.returncode != 0:
        raise GitDivergedError(
            f"Fast-forward merge failed — local clone has diverged from {remote}/{branch}.",
            remediation=(
                "This clone is deploy-only; never commit or hand-edit files in it. "
                "Investigate manually (git status, git log) before retrying — not auto-resetting."
            ),
        )


def _lfs_pull(repo_dir: Path, run_fn: RunFn) -> None:
    if _lfs_available(repo_dir, run_fn):
        logging_utils.log_info("Running git lfs pull to materialize any new tars...")
        result = _git(repo_dir, ["lfs", "pull"], run_fn=run_fn)
        if result.returncode != 0:
            raise AirgapError("git lfs pull failed.", context={"repo_dir": str(repo_dir)})
    else:
        logging_utils.log_warn(
            "git-lfs not installed; large files under "
            f"{BUNDLE_SUBDIR}/ may still be pointer stubs. Install git-lfs on this host."
        )


@dataclass
class HealthCheckConfig:
    backend_publish: str = "18000:8000"
    frontend_publish: str = "18080:80"
    http_check_timeout: float = 10
    retries: int = 10
    retry_delay_sec: float = 3


def _check_health(cfg: HealthCheckConfig, *, sleep_fn: Callable[[float], None] = time.sleep) -> bool:
    """Stricter, blocking retry loop -- stack.stack_up()'s own tail-end health
    check only warns and always returns, so the cron wrapper must verify
    health itself before it's safe to prune the images just replaced.
    """
    # [-2]: publish spec may include an optional host IP (HOST_IP:HOSTPORT:CTRPORT).
    be_port = cfg.backend_publish.split(":")[-2]
    fe_port = cfg.frontend_publish.split(":")[-2]
    be_url = f"http://127.0.0.1:{be_port}/health"
    fe_url = f"http://127.0.0.1:{fe_port}/recruit/health"
    for attempt in range(1, cfg.retries + 1):
        be_ok = stack_module.http_ok(be_url, cfg.http_check_timeout)
        fe_ok = stack_module.http_ok(fe_url, cfg.http_check_timeout)
        if be_ok and fe_ok:
            logging_utils.log_ok(f"Backend and frontend health checks passed (attempt {attempt}/{cfg.retries}).")
            return True
        logging_utils.log_info(
            f"Health check {attempt}/{cfg.retries}: backend={int(be_ok)} frontend={int(fe_ok)}; "
            f"retrying in {cfg.retry_delay_sec}s..."
        )
        sleep_fn(cfg.retry_delay_sec)
    return False


def cron_update(
    *,
    repo_dir: str | Path,
    remote: str = "origin",
    branch: str = "main",
    lock_file: str | Path = DEFAULT_LOCK_FILE,
    health: HealthCheckConfig | None = None,
    skip_prune: bool = False,
    keep_old_tags: int = 1,
    dry_run: bool = False,
    docker_cmd: str | None = None,
    engine: ContainerEngine | None = None,
    run_fn: RunFn = subprocess.run,
) -> bool:
    """Returns True if an update was rolled out and is healthy, False if
    there was nothing to do (already up to date, or bundle unchanged).
    Raises AirgapError subclasses on failure; LockHeldError specifically
    means "benign, try again next run" (exit code 0 at the CLI layer).

    `engine` lets callers (tests, or a caller that already detected one)
    skip auto-detection; when None, docker/podman is only probed for if a
    rollout is actually about to happen (up-to-date / bundle-unchanged runs
    never need a container engine at all).
    """
    health = health or HealthCheckConfig()
    repo_dir = Path(repo_dir).expanduser().resolve()
    lock_file = Path(lock_file)

    with _acquire_lock(lock_file):
        current_branch = _current_branch(repo_dir, run_fn)
        if current_branch != branch:
            raise AirgapError(
                f"Expected clone to be on branch '{branch}', found '{current_branch}'.",
                remediation=f"This clone is deploy-only; fix manually (git checkout {branch}) before retrying.",
            )

        logging_utils.log_info(f"Fetching {remote}/{branch}...")
        _git(repo_dir, ["fetch", "--quiet", remote, branch], run_fn=run_fn)

        old_head = _rev_parse(repo_dir, "HEAD", run_fn)
        new_head = _rev_parse(repo_dir, f"{remote}/{branch}", run_fn)

        if old_head == new_head:
            logging_utils.log_ok(f"Up to date ({old_head}).")
            return False

        logging_utils.log_info(f"New commits on {remote}/{branch}: {old_head} -> {new_head}")
        bundle_changed = _bundle_changed(repo_dir, old_head, new_head, run_fn)

        if dry_run:
            logging_utils.log_info(
                f"[dry-run] Would fast-forward merge to {new_head} and run 'git lfs pull' "
                "(not doing so; git state left untouched)."
            )
            if bundle_changed:
                logging_utils.log_info(
                    f"[dry-run] {BUNDLE_SUBDIR}/ would change. Previewing the update against the "
                    "CURRENT checkout (dry-run makes zero mutating calls):"
                )
                engine = engine or ContainerEngine.detect(prefer=docker_cmd)
                bundle_module.apply_bundle(
                    repo_dir / BUNDLE_SUBDIR, engine=engine, dry_run=True
                )
            else:
                logging_utils.log_info(f"[dry-run] {BUNDLE_SUBDIR}/ would NOT change; no container update would run.")
            return False

        _ff_only_merge(repo_dir, remote, branch, run_fn)
        _lfs_pull(repo_dir, run_fn)

        if not bundle_changed:
            logging_utils.log_ok(f"Repo advanced to {new_head} but {BUNDLE_SUBDIR}/ is unchanged; nothing to deploy.")
            return False

        logging_utils.log_info(f"Detected changes under {BUNDLE_SUBDIR}/; rolling out update...")
        engine = ContainerEngine.detect(prefer=docker_cmd)
        try:
            bundle_module.apply_bundle(repo_dir / BUNDLE_SUBDIR, engine=engine, dry_run=False)
        except AirgapError:
            logging_utils.log_err(
                "Update failed. Old images are left in place; containers may be partially updated."
            )
            logging_utils.log_err("Check: podman logs backend / podman logs frontend")
            raise

        if _check_health(health):
            logging_utils.log_ok(f"Update to {new_head} is healthy.")
            if skip_prune:
                logging_utils.log_info("SKIP_PRUNE=1; leaving old images in place.")
            else:
                try:
                    prune_module.prune_old_images(
                        repo_dir / BUNDLE_SUBDIR, engine, keep_old_tags=keep_old_tags, dry_run=False
                    )
                except AirgapError as exc:
                    logging_utils.log_warn(
                        f"prune-old-images reported a problem; old images may still be present (not fatal): {exc}"
                    )
            return True

        raise HealthCheckError(
            f"Backend/frontend failed health checks after updating to {new_head}.",
            remediation=(
                "Old images were left in place (not pruned) for manual rollback. "
                f"git -C {repo_dir} log --oneline -- {BUNDLE_SUBDIR}/   # find the prior good commit; "
                f"git -C {repo_dir} checkout <old-sha> -- {BUNDLE_SUBDIR}/ && git -C {repo_dir} lfs pull; "
                "then re-run the update."
            ),
        )
