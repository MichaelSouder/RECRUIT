from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from airgap import manifest, stack
from airgap.errors import ImageMissingError, SecretsError


def _bundle(tmp_path):
    d = tmp_path / "bundle"
    d.mkdir()
    (d / "MANIFEST.txt").write_text("IMAGE_PREFIX=prefix\nIMAGE_TAG=tag\n")
    return d


def _seed_all_images(fake_engine, *, use_host_postgres=False):
    if not use_host_postgres:
        fake_engine.seed_image("docker.io/library/postgres:15")
    fake_engine.seed_image("docker.io/library/redis:7-alpine")
    fake_engine.seed_image("prefix/recruit-backend:tag")
    fake_engine.seed_image("prefix/recruit-frontend:tag")


def _base_environ(**overrides):
    env = {
        "SECRET_KEY": "x" * 32,
        "SSN_ENCRYPTION_KEY": "y" * 32,
        "REDIS_PASSWORD": "z" * 20,
        "INITIAL_ADMIN_PASSWORD": "adminpass1",
    }
    env.update(overrides)
    return env


def _make_config(**overrides) -> stack.StackConfig:
    base = dict(
        bundle_dir=Path("/bundle"),
        image_prefix="prefix",
        image_tag="tag",
        docker_cmd=None,
        postgres_image="postgres:15",
        redis_image="redis:7-alpine",
        backend_image="prefix/recruit-backend:tag",
        frontend_image="prefix/recruit-frontend:tag",
        postgres_user="postgres",
        postgres_password="postgres",
        postgres_db="recruit_db",
        postgres_service_port="5432",
        network="recruit_network",
        pg_volume="recruit_postgres_data",
        cors_origins="http://example.com",
        use_host_postgres=False,
        database_url="postgresql://postgres:postgres@postgres:5432/recruit_db",
        pghost_for_backend="postgres",
        postgres_service_host=None,
        postgres_wait_host="127.0.0.1",
        postgres_wait_port="5432",
        secret_key="x" * 32,
        ssn_encryption_key="y" * 32,
        redis_password="z" * 20,
        algorithm="HS256",
        access_token_expire_minutes="30",
        environment="production",
        debug="false",
        seed_initial_admin="true",
        initial_admin_email="admin@example.com",
        initial_admin_password="adminpass1",
        postgres_publish="15432:5432",
        redis_publish="16379:6379",
        backend_publish="18000:8000",
        frontend_publish="18080:80",
        pg_ready_timeout=5,
        http_check_timeout=5,
        stack_settle_sec=0,
        redis_url="redis://redis:6379/0",
        backend_extra_hosts=[],
    )
    base.update(overrides)
    return stack.StackConfig(**base)


# -- postgres/redis three-way branch: the safety-critical logic --------------


def test_postgres_absent_creates(fake_engine):
    stack.ensure_postgres(fake_engine, _make_config(), dry_run=False)
    assert fake_engine.container_exists("postgres")
    assert len(fake_engine.calls_for("run_detached")) == 1
    assert fake_engine.calls_for("rm_container") == []


def test_postgres_running_untouched(fake_engine):
    fake_engine.seed_container("postgres", "docker.io/library/postgres:15", running=True)
    stack.ensure_postgres(fake_engine, _make_config(), dry_run=False)
    assert fake_engine.calls_for("rm_container") == []
    assert fake_engine.calls_for("run_detached") == []


def test_postgres_stopped_recreated(fake_engine):
    fake_engine.seed_container("postgres", "docker.io/library/postgres:15", running=False)
    stack.ensure_postgres(fake_engine, _make_config(), dry_run=False)
    assert fake_engine.calls_for("rm_container") == [("rm_container", "postgres")]
    assert len(fake_engine.calls_for("run_detached")) == 1


def test_redis_absent_creates(fake_engine):
    stack.ensure_redis(fake_engine, _make_config(), dry_run=False)
    assert fake_engine.container_exists("redis")
    assert len(fake_engine.calls_for("run_detached")) == 1


def test_redis_created_with_requirepass(fake_engine):
    stack.ensure_redis(fake_engine, _make_config(redis_password="topsecret123"), dry_run=False)
    [(_, _, _, kwargs)] = fake_engine.calls_for("run_detached")
    assert kwargs["command"] == ["redis-server", "--requirepass", "topsecret123"]


def test_redis_running_untouched(fake_engine):
    fake_engine.seed_container("redis", "docker.io/library/redis:7-alpine", running=True)
    stack.ensure_redis(fake_engine, _make_config(), dry_run=False)
    assert fake_engine.calls_for("rm_container") == []
    assert fake_engine.calls_for("run_detached") == []


def test_redis_stopped_recreated(fake_engine):
    fake_engine.seed_container("redis", "docker.io/library/redis:7-alpine", running=False)
    stack.ensure_redis(fake_engine, _make_config(), dry_run=False)
    assert fake_engine.calls_for("rm_container") == [("rm_container", "redis")]
    assert len(fake_engine.calls_for("run_detached")) == 1


def test_backend_running_untouched(fake_engine):
    fake_engine.seed_container("backend", "prefix/recruit-backend:tag", running=True)
    stack.start_backend(fake_engine, _make_config(), dry_run=False)
    assert fake_engine.calls_for("rm_container") == []
    assert fake_engine.calls_for("run_detached") == []


def test_frontend_running_untouched(fake_engine):
    fake_engine.seed_container("frontend", "prefix/recruit-frontend:tag", running=True)
    stack.start_frontend(fake_engine, _make_config(), dry_run=False)
    assert fake_engine.calls_for("rm_container") == []
    assert fake_engine.calls_for("run_detached") == []


def test_recreate_app_containers_only_touches_backend_frontend(fake_engine):
    fake_engine.seed_container("postgres", "pg", running=True)
    fake_engine.seed_container("redis", "rd", running=True)
    fake_engine.seed_container("backend", "be", running=True)
    fake_engine.seed_container("frontend", "fe", running=True)
    stack.recreate_app_containers(fake_engine, dry_run=False)
    removed = {c[1] for c in fake_engine.calls_for("rm_container")}
    assert removed == {"backend", "frontend"}


def test_dry_run_stopped_postgres_makes_no_mutating_calls(fake_engine):
    fake_engine.seed_container("postgres", "docker.io/library/postgres:15", running=False)
    stack.ensure_postgres(fake_engine, _make_config(), dry_run=True)
    assert fake_engine.calls_for("rm_container") == []
    assert fake_engine.calls_for("run_detached") == []


# -- secrets validation --------------------------------------------------------


def test_require_secrets_missing_key_raises():
    with pytest.raises(SecretsError):
        stack.require_secrets(_make_config(secret_key=""))


def test_require_secrets_too_short_raises():
    with pytest.raises(SecretsError):
        stack.require_secrets(_make_config(secret_key="short"))


def test_require_secrets_missing_ssn_key_raises():
    with pytest.raises(SecretsError):
        stack.require_secrets(_make_config(ssn_encryption_key=""))


def test_require_secrets_ssn_key_too_short_raises():
    with pytest.raises(SecretsError):
        stack.require_secrets(_make_config(ssn_encryption_key="short"))


def test_require_secrets_missing_redis_password_raises():
    with pytest.raises(SecretsError):
        stack.require_secrets(_make_config(redis_password=""))


def test_require_secrets_admin_password_required_when_seeding():
    with pytest.raises(SecretsError):
        stack.require_secrets(_make_config(initial_admin_password=""))


def test_require_secrets_admin_password_not_required_when_not_seeding():
    stack.require_secrets(_make_config(seed_initial_admin="false", initial_admin_password=""))


# -- host postgres three-tier readiness fallback ------------------------------


def test_host_postgres_readiness_pg_isready_used_when_present():
    calls = []

    def run_fn(argv, **kwargs):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0)

    ok = stack.host_pg_reachable(
        "127.0.0.1", 5432, "postgres",
        which_fn=lambda n: "/usr/bin/pg_isready" if n == "pg_isready" else None,
        run_fn=run_fn,
    )
    assert ok is True
    assert calls[0][0] == "pg_isready"


def test_host_postgres_readiness_pg_isready_missing_falls_to_nc():
    calls = []

    def run_fn(argv, **kwargs):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0)

    ok = stack.host_pg_reachable(
        "127.0.0.1", 5432, "postgres",
        which_fn=lambda n: "/usr/bin/nc" if n == "nc" else None,
        run_fn=run_fn,
    )
    assert ok is True
    assert calls[0][0] == "nc"


def test_host_postgres_readiness_nc_missing_falls_to_socket():
    connected = {}

    class _Ctx:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def connect_fn(addr, timeout=None):
        connected["addr"] = addr
        connected["timeout"] = timeout
        return _Ctx()

    ok = stack.host_pg_reachable(
        "127.0.0.1", 5432, "postgres", which_fn=lambda n: None, connect_fn=connect_fn
    )
    assert ok is True
    assert connected["addr"] == ("127.0.0.1", 5432)
    assert connected["timeout"] is not None


def test_host_postgres_readiness_socket_failure_returns_false():
    def connect_fn(addr, timeout=None):
        raise OSError("connection refused")

    ok = stack.host_pg_reachable(
        "127.0.0.1", 5432, "postgres", which_fn=lambda n: None, connect_fn=connect_fn
    )
    assert ok is False


# -- image resolution ------------------------------------------------------------


def test_short_name_resolves_docker_io_library_alias(fake_engine):
    _seed_all_images(fake_engine)
    pg, redis_img, be, fe = stack.require_all_images(fake_engine, _make_config())
    assert pg == "docker.io/library/postgres:15"
    assert redis_img == "docker.io/library/redis:7-alpine"
    assert be == "prefix/recruit-backend:tag"
    assert fe == "prefix/recruit-frontend:tag"


def test_require_all_images_raises_when_missing(fake_engine):
    with pytest.raises(ImageMissingError):
        stack.require_all_images(fake_engine, _make_config())


def test_use_host_postgres_skips_postgres_image_check(fake_engine):
    fake_engine.seed_image("docker.io/library/redis:7-alpine")
    fake_engine.seed_image("prefix/recruit-backend:tag")
    fake_engine.seed_image("prefix/recruit-frontend:tag")
    config = _make_config(use_host_postgres=True)
    # Should not raise even though no postgres image is present at all.
    stack.require_all_images(fake_engine, config)


# -- build_config: USE_HOST_POSTGRES validation and add-host gateway ---------


def _manifest():
    return manifest.Manifest(image_prefix="prefix", image_tag="tag", raw={})


def test_use_host_postgres_requires_database_url():
    environ = _base_environ(USE_HOST_POSTGRES="1")
    with pytest.raises(SecretsError):
        stack.build_config(Path("/bundle"), environ, manifest=_manifest())


def test_use_host_postgres_requires_service_host():
    environ = _base_environ(USE_HOST_POSTGRES="1", DATABASE_URL="postgresql://x")
    with pytest.raises(SecretsError):
        stack.build_config(Path("/bundle"), environ, manifest=_manifest())


def test_add_host_gateway_only_for_docker_with_host_docker_internal():
    environ = _base_environ(
        USE_HOST_POSTGRES="1",
        DATABASE_URL="postgresql://x",
        POSTGRES_SERVICE_HOST="host.docker.internal",
        DOCKER_CMD="docker",
    )
    config = stack.build_config(Path("/bundle"), environ, manifest=_manifest())
    assert config.backend_extra_hosts == ["host.docker.internal:host-gateway"]


def test_add_host_gateway_not_added_for_podman():
    environ = _base_environ(
        USE_HOST_POSTGRES="1",
        DATABASE_URL="postgresql://x",
        POSTGRES_SERVICE_HOST="host.docker.internal",
        DOCKER_CMD="podman",
    )
    config = stack.build_config(Path("/bundle"), environ, manifest=_manifest())
    assert config.backend_extra_hosts == []


def test_add_host_gateway_not_added_for_containers_internal_host():
    environ = _base_environ(
        USE_HOST_POSTGRES="1",
        DATABASE_URL="postgresql://x",
        POSTGRES_SERVICE_HOST="host.containers.internal",
        DOCKER_CMD="docker",
    )
    config = stack.build_config(Path("/bundle"), environ, manifest=_manifest())
    assert config.backend_extra_hosts == []


# -- full stack_up orchestration ----------------------------------------------


def test_stack_up_zero_mutations_when_everything_already_running(tmp_path, fake_engine):
    d = _bundle(tmp_path)
    _seed_all_images(fake_engine)
    fake_engine.seed_container("postgres", "docker.io/library/postgres:15", running=True)
    fake_engine.seed_container("redis", "docker.io/library/redis:7-alpine", running=True)
    fake_engine.seed_container("backend", "prefix/recruit-backend:tag", running=True)
    fake_engine.seed_container("frontend", "prefix/recruit-frontend:tag", running=True)
    fake_engine.networks.add("recruit_network")

    result = stack.stack_up(d, dry_run=True, environ=_base_environ(), engine=fake_engine)

    assert result == {"backend": True, "frontend": True}
    assert fake_engine.calls_for("run_detached") == []
    assert fake_engine.calls_for("rm_container") == []


def test_stack_up_fresh_bootstrap_creates_everything(tmp_path, fake_engine, monkeypatch):
    d = _bundle(tmp_path)
    _seed_all_images(fake_engine)
    monkeypatch.setattr(stack, "http_ok", lambda url, timeout: True)

    result = stack.stack_up(
        d, dry_run=False, environ=_base_environ(STACK_SETTLE_SEC="0"), engine=fake_engine
    )

    assert result == {"backend": True, "frontend": True}
    for name in ("postgres", "redis", "backend", "frontend"):
        assert fake_engine.container_exists(name)
    assert "recruit_network" in fake_engine.networks
    assert "recruit_postgres_data" in fake_engine.volumes


def test_stack_up_recreate_app_leaves_db_running_but_replaces_app(tmp_path, fake_engine, monkeypatch):
    d = _bundle(tmp_path)
    _seed_all_images(fake_engine)
    fake_engine.seed_container("postgres", "docker.io/library/postgres:15", running=True)
    fake_engine.seed_container("redis", "docker.io/library/redis:7-alpine", running=True)
    fake_engine.seed_container("backend", "old-image", running=True)
    fake_engine.seed_container("frontend", "old-image", running=True)
    fake_engine.networks.add("recruit_network")
    monkeypatch.setattr(stack, "http_ok", lambda url, timeout: True)

    stack.stack_up(
        d,
        recreate_app=True,
        dry_run=False,
        environ=_base_environ(STACK_SETTLE_SEC="0"),
        engine=fake_engine,
    )

    removed = {c[1] for c in fake_engine.calls_for("rm_container")}
    assert removed == {"backend", "frontend"}
    assert fake_engine.container_running("backend")
    assert fake_engine.container_running("frontend")
    assert fake_engine.containers["backend"].image == "prefix/recruit-backend:tag"
