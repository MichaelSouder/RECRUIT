"""Full port of airgap-stack-up.sh: bring up (or reconcile) postgres, redis,
backend, and frontend containers from a loaded image bundle.

Safety-critical invariant, preserved exactly from the bash original: postgres
and redis are *never* removed while running. Each gets a three-way check --
absent (create fresh), exists+running (untouched, zero mutating calls),
exists+stopped (removed and recreated, logged as "stale from a previous
attempt"). `--recreate-app` only ever touches backend/frontend.
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from . import logging_utils
from .engine import ContainerEngine
from .envfile import apply_env_file
from .errors import HealthCheckError, ImageMissingError, SecretsError
from .manifest import Manifest
from .manifest import parse as parse_manifest

DEFAULT_CORS_ORIGINS = "http://127.0.0.1:18080,http://localhost:18080"


def _truthy(val: str | None) -> bool:
    return (val or "").strip().lower() in {"1", "true", "yes", "on"}


def _abs_path(p: str) -> Path:
    return Path(p).expanduser().resolve()


def resolve_and_load_env(
    bundle_dir: Path, *, env_file: str | None = None, environ: dict[str, str] | None = None
) -> None:
    environ = os.environ if environ is None else environ
    if env_file:
        apply_env_file(_abs_path(env_file), environ)
        return
    recruit_env_file = environ.get("RECRUIT_ENV_FILE")
    if recruit_env_file:
        apply_env_file(_abs_path(recruit_env_file), environ)
        return
    candidate = bundle_dir / "recruit-airgap.env"
    if candidate.is_file():
        apply_env_file(candidate, environ)
        return
    logging_utils.log_info(
        f"No env file loaded (optional). Create {candidate} or pass env_file / set RECRUIT_ENV_FILE."
    )


@dataclass
class StackConfig:
    bundle_dir: Path
    image_prefix: str
    image_tag: str
    docker_cmd: str | None
    postgres_image: str
    redis_image: str
    backend_image: str
    frontend_image: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_service_port: str
    network: str
    pg_volume: str
    cors_origins: str
    use_host_postgres: bool
    database_url: str
    pghost_for_backend: str
    postgres_service_host: str | None
    postgres_wait_host: str
    postgres_wait_port: str
    secret_key: str
    ssn_encryption_key: str
    redis_password: str
    algorithm: str
    access_token_expire_minutes: str
    environment: str
    debug: str
    seed_initial_admin: str
    initial_admin_email: str
    initial_admin_password: str
    postgres_publish: str
    redis_publish: str
    backend_publish: str
    frontend_publish: str
    pg_ready_timeout: int
    http_check_timeout: int
    stack_settle_sec: int
    redis_url: str
    backend_extra_hosts: list[str] = field(default_factory=list)


def build_config(bundle_dir: Path, environ: dict[str, str], *, manifest: Manifest) -> StackConfig:
    def env(key: str, default: str = "") -> str:
        return environ.get(key, default)

    image_prefix = env("IMAGE_PREFIX") or manifest.image_prefix
    tag = env("TAG") or env("IMAGE_TAG") or manifest.image_tag

    postgres_user = env("POSTGRES_USER", "postgres")
    postgres_password = env("POSTGRES_PASSWORD", "postgres")
    postgres_db = env("POSTGRES_DB", "recruit_db")
    # `or` not a default arg: env() returns "" for a present-but-blank var (POSTGRES_SERVICE_PORT=),
    # and "" would later crash int(config.postgres_wait_port). `or` collapses blank to the default too.
    postgres_service_port = env("POSTGRES_SERVICE_PORT") or "5432"

    use_host_postgres = _truthy(env("USE_HOST_POSTGRES"))

    backend_extra_hosts: list[str] = []
    postgres_service_host: str | None = None
    if use_host_postgres:
        database_url = env("DATABASE_URL")
        if not database_url:
            raise SecretsError(
                "USE_HOST_POSTGRES is set but DATABASE_URL is empty.",
                remediation="Set DATABASE_URL to reach the host DB from the backend container.",
            )
        postgres_service_host = env("POSTGRES_SERVICE_HOST")
        if not postgres_service_host:
            raise SecretsError(
                "USE_HOST_POSTGRES is set but POSTGRES_SERVICE_HOST is empty.",
                remediation=(
                    "Set it to the same hostname used in DATABASE_URL "
                    "(e.g. host.containers.internal or host.docker.internal)."
                ),
            )
        if postgres_service_host == "host.docker.internal" and env("DOCKER_CMD") == "docker":
            backend_extra_hosts.append("host.docker.internal:host-gateway")
        pghost_for_backend = postgres_service_host
    else:
        database_url = env("DATABASE_URL") or (
            f"postgresql://{postgres_user}:{postgres_password}@postgres:5432/{postgres_db}"
        )
        pghost_for_backend = "postgres"

    redis_password = env("REDIS_PASSWORD")

    return StackConfig(
        bundle_dir=bundle_dir,
        image_prefix=image_prefix,
        image_tag=tag,
        docker_cmd=env("DOCKER_CMD") or None,
        postgres_image=env("POSTGRES_IMAGE", "postgres:15"),
        redis_image=env("REDIS_IMAGE", "redis:7-alpine"),
        backend_image=f"{image_prefix}/recruit-backend:{tag}",
        frontend_image=f"{image_prefix}/recruit-frontend:{tag}",
        postgres_user=postgres_user,
        postgres_password=postgres_password,
        postgres_db=postgres_db,
        postgres_service_port=postgres_service_port,
        network=env("RECRUIT_NETWORK", "recruit_network"),
        pg_volume=env("RECRUIT_PG_VOLUME", "recruit_postgres_data"),
        cors_origins=env("CORS_ORIGINS", DEFAULT_CORS_ORIGINS),
        use_host_postgres=use_host_postgres,
        database_url=database_url,
        pghost_for_backend=pghost_for_backend,
        postgres_service_host=postgres_service_host,
        postgres_wait_host=env("POSTGRES_WAIT_HOST", "127.0.0.1"),
        postgres_wait_port=env("POSTGRES_WAIT_PORT") or postgres_service_port,
        secret_key=env("SECRET_KEY"),
        ssn_encryption_key=env("SSN_ENCRYPTION_KEY"),
        redis_password=redis_password,
        algorithm=env("ALGORITHM", "HS256"),
        access_token_expire_minutes=env("ACCESS_TOKEN_EXPIRE_MINUTES", "30"),
        environment=env("ENVIRONMENT", "production"),
        debug=env("DEBUG", "false"),
        seed_initial_admin=env("SEED_INITIAL_ADMIN", "true"),
        initial_admin_email=env("INITIAL_ADMIN_EMAIL", "admin@example.com"),
        initial_admin_password=env("INITIAL_ADMIN_PASSWORD"),
        postgres_publish=env("POSTGRES_PUBLISH", "15432:5432"),
        redis_publish=env("REDIS_PUBLISH", "16379:6379"),
        backend_publish=env("BACKEND_PUBLISH", "18000:8000"),
        frontend_publish=env("FRONTEND_PUBLISH", "18080:80"),
        pg_ready_timeout=int(env("PG_READY_TIMEOUT") or "120"),
        http_check_timeout=int(env("HTTP_CHECK_TIMEOUT") or "15"),
        stack_settle_sec=int(env("STACK_SETTLE_SEC") or "5"),
        redis_url=env("REDIS_URL") or f"redis://:{redis_password}@redis:6379/0",
        backend_extra_hosts=backend_extra_hosts,
    )


def require_secrets(config: StackConfig) -> None:
    if not config.secret_key:
        raise SecretsError(
            "SECRET_KEY is not set.",
            remediation="Add it to recruit-airgap.env or export it. Example: openssl rand -hex 32",
        )
    if len(config.secret_key) < 32:
        raise SecretsError(
            "SECRET_KEY is too short (the backend requires at least 32 characters and will "
            "refuse to start otherwise). Example: openssl rand -hex 32"
        )
    if not config.ssn_encryption_key:
        raise SecretsError(
            "SSN_ENCRYPTION_KEY is not set.",
            remediation=(
                "Add it to recruit-airgap.env or export it (use a DIFFERENT value than "
                "SECRET_KEY, and back it up separately — losing it after deploy makes every "
                "stored SSN permanently unrecoverable). Example: openssl rand -hex 32"
            ),
        )
    if len(config.ssn_encryption_key) < 32:
        raise SecretsError(
            "SSN_ENCRYPTION_KEY is too short (the backend requires at least 32 characters "
            "and will refuse to start otherwise). Example: openssl rand -hex 32"
        )
    if not config.redis_password:
        raise SecretsError(
            "REDIS_PASSWORD is not set.",
            remediation=(
                "Add it to recruit-airgap.env or export it. Redis is published to the host "
                "(REDIS_PUBLISH) and runs with no auth otherwise. Example: openssl rand -hex 32"
            ),
        )
    if config.seed_initial_admin in ("true", "1"):
        if not config.initial_admin_password:
            raise SecretsError(
                "INITIAL_ADMIN_PASSWORD is not set (required when SEED_INITIAL_ADMIN is true)."
            )
        if len(config.initial_admin_password) < 8:
            raise SecretsError("INITIAL_ADMIN_PASSWORD must be at least 8 characters.")


def _hub_library_alias(ref: str) -> str | None:
    """For short Hub refs like postgres:15, return docker.io/library/postgres:15."""
    if "/" in ref:
        return None
    name, _, tag = ref.partition(":")
    return f"docker.io/library/{name}:{tag or 'latest'}"


def _resolve_image(engine: ContainerEngine, role: str, candidates: list[str]) -> str:
    tried = [c for c in candidates if c]
    for ref in tried:
        if engine.image_exists(ref):
            logging_utils.log_ok(f"Image present ({role}): {ref}")
            return ref
    raise ImageMissingError(
        f"Missing image ({role}). Tried: {', '.join(tried)}",
        remediation="Load all .tar files first (bundle.load_images), using the same engine for load and stack-up.",
    )


def require_all_images(engine: ContainerEngine, config: StackConfig) -> tuple[str, str, str, str]:
    postgres_image = config.postgres_image
    if not config.use_host_postgres:
        alias = _hub_library_alias(config.postgres_image)
        candidates = [alias, config.postgres_image] if alias else [config.postgres_image]
        postgres_image = _resolve_image(engine, "postgres", candidates)
    else:
        logging_utils.log_info("USE_HOST_POSTGRES: skipping postgres container image check.")

    alias = _hub_library_alias(config.redis_image)
    candidates = [alias, config.redis_image] if alias else [config.redis_image]
    redis_image = _resolve_image(engine, "redis", candidates)

    backend_image = _resolve_image(engine, "backend", [config.backend_image])
    frontend_image = _resolve_image(engine, "frontend", [config.frontend_image])

    return postgres_image, redis_image, backend_image, frontend_image


def ensure_network(engine: ContainerEngine, name: str, *, dry_run: bool) -> None:
    if engine.network_exists(name):
        logging_utils.log_ok("Network already exists.")
        return
    if dry_run:
        logging_utils.log_info(f"[dry-run] would run: {engine.name} network create {name}")
        return
    engine.network_create(name)
    logging_utils.log_ok("Network ready.")


def ensure_volume(engine: ContainerEngine, name: str, *, dry_run: bool) -> None:
    if dry_run:
        logging_utils.log_info(f"[dry-run] would run: {engine.name} volume create {name}")
        return
    engine.volume_create(name)
    logging_utils.log_ok("Volume ready (created or already present).")


def recreate_app_containers(engine: ContainerEngine, *, dry_run: bool) -> None:
    for name in ("backend", "frontend"):
        if engine.container_exists(name):
            logging_utils.log_warn(f"Removing container: {name}")
            if dry_run:
                logging_utils.log_info(f"[dry-run] would run: {engine.name} rm -f {name}")
            else:
                engine.rm_container(name)


def _ensure_running_container(
    engine: ContainerEngine,
    name: str,
    *,
    dry_run: bool,
    ok_message: str,
    stale_message: str,
    creating_message: str,
    create_fn: Callable[[], None],
    dry_run_create_hint: str,
) -> None:
    """Shared three-way branch: absent -> create; running -> untouched;
    stopped -> remove + recreate ("stale from a previous attempt").
    This is the safety-critical logic -- it must never remove a running
    container.
    """
    if engine.container_exists(name):
        if engine.container_running(name):
            logging_utils.log_ok(ok_message)
            return
        logging_utils.log_warn(stale_message)
        if dry_run:
            logging_utils.log_info(f"[dry-run] would run: {engine.name} rm -f {name}")
        else:
            engine.rm_container(name)
    logging_utils.log_info(creating_message)
    if dry_run:
        logging_utils.log_info(f"[dry-run] would run: {dry_run_create_hint}")
        return
    create_fn()


def ensure_postgres(engine: ContainerEngine, config: StackConfig, *, dry_run: bool) -> None:
    _ensure_running_container(
        engine,
        "postgres",
        dry_run=dry_run,
        ok_message="Postgres already running.",
        stale_message="Postgres container exists but is stopped — removing and recreating (stale container from a previous attempt).",
        creating_message=f"Creating Postgres ({config.postgres_image})...",
        dry_run_create_hint=f"{engine.name} run -d --name postgres --network {config.network} {config.postgres_image}",
        create_fn=lambda: engine.run_detached(
            name="postgres",
            image=config.postgres_image,
            network=config.network,
            env={
                "POSTGRES_USER": config.postgres_user,
                "POSTGRES_PASSWORD": config.postgres_password,
                "POSTGRES_DB": config.postgres_db,
            },
            publish=config.postgres_publish,
            volume=f"{config.pg_volume}:/var/lib/postgresql/data",
            restart="unless-stopped",
        ),
    )


def ensure_redis(engine: ContainerEngine, config: StackConfig, *, dry_run: bool) -> None:
    _ensure_running_container(
        engine,
        "redis",
        dry_run=dry_run,
        ok_message="Redis already running.",
        stale_message="Redis container exists but is stopped — removing and recreating.",
        creating_message=f"Creating Redis ({config.redis_image})...",
        dry_run_create_hint=(
            f"{engine.name} run -d --name redis --network {config.network} {config.redis_image} "
            f"redis-server --requirepass ****"
        ),
        create_fn=lambda: engine.run_detached(
            name="redis",
            image=config.redis_image,
            network=config.network,
            publish=config.redis_publish,
            restart="unless-stopped",
            command=["redis-server", "--requirepass", config.redis_password],
        ),
    )


def _backend_inner_command(config: StackConfig) -> str:
    return (
        "echo 'Waiting for PostgreSQL...' && "
        f'until pg_isready -h "${{PGHOST:-postgres}}" -p "${{PGPORT:-5432}}" -U {config.postgres_user}; '
        "do sleep 1; done && "
        "echo 'PostgreSQL is ready!' && "
        "echo 'Initializing database...' && "
        "python -c 'import app.models; from app.database import Base, engine; "
        "Base.metadata.create_all(bind=engine)' 2>&1 || true && "
        "python scripts/add_assessment_time_to_assessments.py 2>&1 || echo 'Migration may have already run' && "
        "echo 'Database initialized!' && "
        "exec uvicorn app.main:app --host 0.0.0.0 --port 8000"
    )


def start_backend(engine: ContainerEngine, config: StackConfig, *, dry_run: bool) -> None:
    env = {
        "DATABASE_URL": config.database_url,
        "PGHOST": config.pghost_for_backend,
        "PGPORT": config.postgres_service_port,
        "REDIS_URL": config.redis_url,
        "SECRET_KEY": config.secret_key,
        "SSN_ENCRYPTION_KEY": config.ssn_encryption_key,
        "ALGORITHM": config.algorithm,
        "ACCESS_TOKEN_EXPIRE_MINUTES": config.access_token_expire_minutes,
        "CORS_ORIGINS": config.cors_origins,
        "ENVIRONMENT": config.environment,
        "DEBUG": config.debug,
        "SEED_INITIAL_ADMIN": config.seed_initial_admin,
        "INITIAL_ADMIN_EMAIL": config.initial_admin_email,
        "INITIAL_ADMIN_PASSWORD": config.initial_admin_password,
    }
    _ensure_running_container(
        engine,
        "backend",
        dry_run=dry_run,
        ok_message="Backend already running.",
        stale_message="Backend container exists but is stopped — removing and recreating.",
        creating_message="Creating backend...",
        dry_run_create_hint=f"{engine.name} run -d --name backend {config.backend_image}",
        create_fn=lambda: engine.run_detached(
            name="backend",
            image=config.backend_image,
            network=config.network,
            env=env,
            publish=config.backend_publish,
            restart="unless-stopped",
            extra_hosts=tuple(config.backend_extra_hosts),
            command=["sh", "-c", _backend_inner_command(config)],
        ),
    )


def start_frontend(engine: ContainerEngine, config: StackConfig, *, dry_run: bool) -> None:
    _ensure_running_container(
        engine,
        "frontend",
        dry_run=dry_run,
        ok_message="Frontend already running.",
        stale_message="Frontend container exists but is stopped — removing and recreating.",
        creating_message="Creating frontend...",
        dry_run_create_hint=f"{engine.name} run -d --name frontend {config.frontend_image}",
        create_fn=lambda: engine.run_detached(
            name="frontend",
            image=config.frontend_image,
            network=config.network,
            publish=config.frontend_publish,
            restart="unless-stopped",
        ),
    )


def wait_pg_ready(engine: ContainerEngine, config: StackConfig, *, dry_run: bool) -> None:
    if dry_run:
        logging_utils.log_info("Skipping Postgres container readiness wait (dry-run).")
        return
    max_wait = config.pg_ready_timeout
    logging_utils.log_info(f"Waiting for Postgres container (timeout {max_wait}s)...")
    for i in range(1, max_wait + 1):
        if engine.exec_in("postgres", ["pg_isready", "-U", config.postgres_user]).ok:
            logging_utils.log_ok("Postgres container is accepting connections.")
            return
        time.sleep(1)
        if i % 10 == 0:
            logging_utils.log_info(f"  ... still waiting ({i}s / {max_wait}s)")
    raise HealthCheckError(
        f"Postgres container did not become ready within {max_wait}s.",
        remediation=f"Check: {engine.name} logs postgres",
    )


def host_pg_reachable(
    host: str,
    port: int,
    user: str,
    *,
    which_fn: Callable[[str], str | None] = shutil.which,
    run_fn: Callable[..., "subprocess.CompletedProcess[bytes]"] = subprocess.run,
    connect_fn: Callable[..., object] = socket.create_connection,
) -> bool:
    """Three-tier readiness check for USE_HOST_POSTGRES mode, in preference
    order: pg_isready, then `nc -z`, then a raw TCP connect (replaces bash's
    `/dev/tcp`, with an explicit timeout).
    """
    if which_fn("pg_isready"):
        result = run_fn(["pg_isready", "-h", host, "-p", str(port), "-U", user], capture_output=True)
        return result.returncode == 0
    if which_fn("nc"):
        result = run_fn(["nc", "-z", host, str(port)], capture_output=True)
        return result.returncode == 0
    try:
        connect_fn((host, port), timeout=2)
        return True
    except OSError:
        return False


def wait_pg_ready_host(config: StackConfig, *, dry_run: bool) -> None:
    if dry_run:
        logging_utils.log_info("Skipping host Postgres readiness wait (dry-run).")
        return
    host = config.postgres_wait_host
    port = int(config.postgres_wait_port)
    max_wait = config.pg_ready_timeout
    logging_utils.log_info(f"Waiting for host Postgres at {host}:{port} (timeout {max_wait}s)...")
    for i in range(1, max_wait + 1):
        if host_pg_reachable(host, port, config.postgres_user):
            logging_utils.log_ok(f"Host Postgres is reachable ({host}:{port}).")
            return
        time.sleep(1)
        if i % 10 == 0:
            logging_utils.log_info(f"  ... still waiting ({i}s / {max_wait}s)")
    raise HealthCheckError(
        f"Host Postgres not reachable at {host}:{port} within {max_wait}s.",
        remediation="Ensure PostgreSQL listens on TCP and pg_hba.conf allows this host.",
    )


def http_ok(url: str, timeout: float) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310 - fixed http(s) urls only
            return 200 <= resp.status < 300
    except (urllib.error.URLError, OSError, TimeoutError, ValueError):
        return False


def verify_health(config: StackConfig, *, dry_run: bool) -> dict[str, bool]:
    if dry_run:
        return {"backend": True, "frontend": True}

    if config.stack_settle_sec > 0:
        logging_utils.log_info(f"Waiting {config.stack_settle_sec}s for HTTP endpoints to settle...")
        time.sleep(config.stack_settle_sec)

    # [-2] not [0]: a publish spec may carry an optional host IP (HOST_IP:HOSTPORT:CTRPORT),
    # so the host port is always the second-to-last colon-separated field, not the first.
    be_port = config.backend_publish.split(":")[-2]
    fe_port = config.frontend_publish.split(":")[-2]
    be_url = f"http://127.0.0.1:{be_port}/health"
    fe_url = f"http://127.0.0.1:{fe_port}/recruit/health"

    be_ok = http_ok(be_url, config.http_check_timeout)
    fe_ok = http_ok(fe_url, config.http_check_timeout)

    if be_ok:
        logging_utils.log_ok(f"Backend health: OK ({be_url})")
    else:
        logging_utils.log_warn(f"Backend health check failed or not ready yet. Try: curl -sf {be_url}")
    if fe_ok:
        logging_utils.log_ok(f"Frontend health: OK ({fe_url})")
    else:
        logging_utils.log_warn(f"Frontend health check failed or not ready yet. Try: curl -sf {fe_url}")

    return {"backend": be_ok, "frontend": fe_ok}


def stack_up(
    bundle_dir: str | Path,
    *,
    recreate_app: bool = False,
    dry_run: bool = False,
    env_file: str | None = None,
    environ: dict[str, str] | None = None,
    engine: ContainerEngine | None = None,
) -> dict[str, bool]:
    environ = os.environ if environ is None else environ
    bundle_dir = Path(bundle_dir).expanduser().resolve()
    logging_utils.log_info(f"Bundle directory: {bundle_dir}")

    manifest = parse_manifest(bundle_dir / "MANIFEST.txt")
    resolve_and_load_env(bundle_dir, env_file=env_file, environ=environ)
    config = build_config(bundle_dir, environ, manifest=manifest)

    if config.cors_origins == DEFAULT_CORS_ORIGINS:
        logging_utils.log_warn(
            "CORS_ORIGINS left at localhost defaults. Set CORS_ORIGINS for real browser URLs "
            "(scheme+host+port, no path)."
        )

    require_secrets(config)

    if engine is None:
        # Standalone use (e.g. the `stack-up` CLI subcommand): auto-detect,
        # preferring whichever engine already has the backend image loaded.
        # Callers that already loaded images themselves (bundle.apply_bundle)
        # pass their engine through instead, so load and run always agree.
        engine = ContainerEngine.detect_by_image(config.backend_image, prefer=config.docker_cmd)
    logging_utils.log_ok(f"Using container engine: {engine.name}")

    if recreate_app:
        recreate_app_containers(engine, dry_run=dry_run)

    logging_utils.log_info("Checking local images...")
    postgres_image, redis_image, backend_image, frontend_image = require_all_images(engine, config)
    config.postgres_image, config.redis_image = postgres_image, redis_image
    config.backend_image, config.frontend_image = backend_image, frontend_image

    ensure_network(engine, config.network, dry_run=dry_run)

    if config.use_host_postgres:
        logging_utils.log_info(
            "Mode: USE_HOST_POSTGRES (Redis + backend + frontend only; database on host)."
        )
        wait_pg_ready_host(config, dry_run=dry_run)
    else:
        ensure_volume(engine, config.pg_volume, dry_run=dry_run)
        ensure_postgres(engine, config, dry_run=dry_run)
        wait_pg_ready(engine, config, dry_run=dry_run)

    ensure_redis(engine, config, dry_run=dry_run)
    start_backend(engine, config, dry_run=dry_run)
    start_frontend(engine, config, dry_run=dry_run)

    if dry_run:
        logging_utils.log_ok("Dry-run finished (no changes applied). Re-run without --dry-run to start containers.")
        return {"backend": True, "frontend": True}

    logging_utils.log_info("Verifying stack...")
    return verify_health(config, dry_run=dry_run)
