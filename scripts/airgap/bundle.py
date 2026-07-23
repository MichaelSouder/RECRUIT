"""Load images from an exported bundle directory (port of
load-container-images.sh), including the tag_if_untagged() fallback for
archives that didn't embed fully-qualified RepoTags.

Unlike the original bash script, `dry_run=True` here genuinely performs zero
mutating calls -- the original `update-containers.sh --dry-run` still ran
this step for real, which was a bug.
"""

from __future__ import annotations

from pathlib import Path

from . import logging_utils
from . import stack as _stack
from .engine import ContainerEngine
from .errors import ImageMissingError
from .manifest import Manifest
from .manifest import parse as parse_manifest

REQUIRED_TARS = (
    "postgres-15.tar",
    "redis-7-alpine.tar",
    "recruit-backend.tar",
    "recruit-frontend.tar",
)


def _tag_if_untagged(engine: ContainerEngine, want_tag: str, env_markers: tuple[str, ...]) -> None:
    if engine.image_exists(want_tag):
        return
    logging_utils.log_info(
        f"{want_tag} not found — scanning untagged images by ENV markers {'|'.join(env_markers)} ..."
    )
    for image_id in engine.image_ids():
        env_str = engine.image_env(image_id)
        if any(marker in env_str for marker in env_markers):
            logging_utils.log_info(f"Tagging {image_id} -> {want_tag}")
            engine.tag(image_id, want_tag)
            return
    logging_utils.log_warn(f"Could not find image to tag as {want_tag}")


def load_images(
    bundle_dir: str | Path,
    engine: ContainerEngine,
    *,
    manifest: Manifest | None = None,
    dry_run: bool = False,
) -> None:
    bundle_dir = Path(bundle_dir)

    for name in REQUIRED_TARS:
        path = bundle_dir / name
        if not path.is_file():
            raise ImageMissingError(f"Missing bundle file: {path}")
        logging_utils.log_info(f"==> {name}")
        if dry_run:
            logging_utils.log_info(f"[dry-run] would run: {engine.name} load -i {path}")
            continue
        engine.load(str(path))

    if dry_run:
        logging_utils.log_info(
            "[dry-run] skipping tag-fallback and image listing (no images were loaded)."
        )
        return

    _tag_if_untagged(engine, "docker.io/library/postgres:15", ("PGDATA",))
    _tag_if_untagged(engine, "docker.io/library/redis:7-alpine", ("REDIS_VERSION",))

    if manifest is not None:
        backend_ref = f"{manifest.image_prefix}/recruit-backend:{manifest.image_tag}"
        frontend_ref = f"{manifest.image_prefix}/recruit-frontend:{manifest.image_tag}"
        _tag_if_untagged(engine, backend_ref, ("APP_MODULE", "uvicorn", "PYTHONDONTWRITEBYTECODE"))
        _tag_if_untagged(engine, frontend_ref, ("NGINX_VERSION",))

    logging_utils.log_ok("Images loaded.")


def apply_bundle(
    bundle_dir: str | Path,
    *,
    engine: ContainerEngine,
    dry_run: bool = False,
    env_file: str | None = None,
    environ: dict[str, str] | None = None,
) -> dict[str, bool]:
    """Load a bundle's images and recreate backend/frontend from them --
    port of update-containers.sh (load-container-images.sh +
    airgap-stack-up.sh --recreate-app). Postgres/Redis are never touched.

    `engine` is loaded from and passed through to stack_up() so the images
    that get loaded and the containers that get run always agree on which
    container engine (docker vs podman) is in play.
    """
    bundle_dir = Path(bundle_dir)
    manifest = parse_manifest(bundle_dir / "MANIFEST.txt")
    load_images(bundle_dir, engine, manifest=manifest, dry_run=dry_run)
    return _stack.stack_up(
        bundle_dir,
        recreate_app=True,
        dry_run=dry_run,
        env_file=env_file,
        environ=environ,
        engine=engine,
    )
