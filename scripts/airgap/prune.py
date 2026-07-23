"""Port of prune-old-images.sh: remove old recruit-backend/recruit-frontend
image tags after a successful update, keeping the most recent `keep_old_tags`
plus whatever is currently running. Never touches postgres/redis images.
"""

from __future__ import annotations

from pathlib import Path

from . import logging_utils
from .engine import ContainerEngine
from .manifest import Manifest
from .manifest import parse as parse_manifest

PROTECTED_MARKERS = ("postgres", "redis")


def _running_image_id(engine: ContainerEngine, container_name: str) -> str | None:
    if not engine.container_exists(container_name):
        return None
    return engine.container_image_id(container_name)


def _prune_repo(
    engine: ContainerEngine,
    repo: str,
    protect_id: str | None,
    *,
    keep_old_tags: int,
    dry_run: bool,
) -> None:
    # Defense in depth: only ever called with the two literal app repos below,
    # but never allow this to touch infra images.
    if any(marker in repo for marker in PROTECTED_MARKERS):
        logging_utils.log_err(f"Refusing to prune {repo} — not an app image.")
        return

    records = engine.images(repo)
    if not records:
        logging_utils.log_info(f"No local images found for {repo}; nothing to prune.")
        return

    records = sorted(records, key=lambda r: r.created_at, reverse=True)

    old_count = 0
    for record in records:
        if not record.tag or record.tag == "<none>":
            continue
        ref = f"{repo}:{record.tag}"
        if protect_id and record.image_id == protect_id:
            logging_utils.log_info(f"Keeping {ref} (currently running).")
            continue
        if old_count < keep_old_tags:
            logging_utils.log_info(f"Keeping {ref} (old, within KEEP_OLD_TAGS={keep_old_tags}).")
            old_count += 1
            continue
        if dry_run:
            logging_utils.log_info(f"[dry-run] would remove {ref}")
        else:
            logging_utils.log_warn(f"Removing old image: {ref}")
            if not engine.rmi(ref):
                logging_utils.log_warn(f"Could not remove {ref} (may still be referenced); skipping.")


def prune_old_images(
    bundle_dir: str | Path,
    engine: ContainerEngine,
    *,
    manifest: Manifest | None = None,
    keep_old_tags: int = 1,
    dry_run: bool = False,
) -> None:
    bundle_dir = Path(bundle_dir)
    if manifest is None:
        manifest = parse_manifest(bundle_dir / "MANIFEST.txt")

    backend_repo = f"{manifest.image_prefix}/recruit-backend"
    frontend_repo = f"{manifest.image_prefix}/recruit-frontend"

    _prune_repo(
        engine,
        backend_repo,
        _running_image_id(engine, "backend"),
        keep_old_tags=keep_old_tags,
        dry_run=dry_run,
    )
    _prune_repo(
        engine,
        frontend_repo,
        _running_image_id(engine, "frontend"),
        keep_old_tags=keep_old_tags,
        dry_run=dry_run,
    )

    if dry_run:
        logging_utils.log_info(f"[dry-run] would run: {engine.name} image prune -f")
    else:
        logging_utils.log_info("Pruning dangling (untagged) image layers...")
        engine.image_prune()

    logging_utils.log_ok("Prune complete.")
