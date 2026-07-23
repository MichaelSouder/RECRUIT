from __future__ import annotations

import pytest

from airgap.engine import ContainerEngine
from airgap.errors import EngineNotFoundError


class FakeProc:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class ScriptedRunFn:
    """Records every argv it's called with; returns canned results from the
    first matching predicate, defaulting to success with empty output.
    """

    def __init__(self):
        self.calls: list[list[str]] = []
        self._responses: list[tuple] = []

    def when(self, predicate, *, returncode=0, stdout="", stderr=""):
        self._responses.append((predicate, FakeProc(returncode, stdout, stderr)))
        return self

    def __call__(self, argv, **kwargs):
        self.calls.append(list(argv))
        for predicate, proc in self._responses:
            if predicate(argv):
                return proc
        return FakeProc(0, "", "")


def test_image_exists_true():
    run_fn = ScriptedRunFn().when(lambda a: a[:3] == ["podman", "image", "inspect"], returncode=0)
    engine = ContainerEngine("podman", run_fn=run_fn)
    assert engine.image_exists("postgres:15") is True


def test_image_exists_false():
    run_fn = ScriptedRunFn().when(lambda a: True, returncode=1)
    engine = ContainerEngine("podman", run_fn=run_fn)
    assert engine.image_exists("missing:1") is False


def test_container_running_true():
    run_fn = ScriptedRunFn().when(lambda a: "container" in a, returncode=0, stdout="true\n")
    engine = ContainerEngine("docker", run_fn=run_fn)
    assert engine.container_running("backend") is True


def test_container_running_false_when_stopped():
    run_fn = ScriptedRunFn().when(lambda a: "container" in a, returncode=0, stdout="false\n")
    engine = ContainerEngine("docker", run_fn=run_fn)
    assert engine.container_running("backend") is False


def test_container_running_false_when_absent():
    run_fn = ScriptedRunFn().when(lambda a: True, returncode=1)
    engine = ContainerEngine("docker", run_fn=run_fn)
    assert engine.container_running("backend") is False


def test_run_detached_builds_expected_argv():
    run_fn = ScriptedRunFn()
    engine = ContainerEngine("podman", run_fn=run_fn)
    engine.run_detached(
        name="backend",
        image="prefix/recruit-backend:tag",
        network="recruit_network",
        env={"A": "1", "B": "two"},
        publish="18000:8000",
        extra_hosts=("host.docker.internal:host-gateway",),
        command=["sh", "-c", "echo hi"],
    )
    argv = run_fn.calls[-1]
    assert argv[0:3] == ["podman", "run", "-d"]
    assert argv[3:5] == ["--name", "backend"]
    assert "--network" in argv and "recruit_network" in argv
    assert "--add-host=host.docker.internal:host-gateway" in argv
    assert "-e" in argv and "A=1" in argv and "B=two" in argv
    assert "-p" in argv and "18000:8000" in argv
    assert argv[-3:] == ["sh", "-c", "echo hi"]
    assert "prefix/recruit-backend:tag" in argv


def test_run_detached_raises_on_failure():
    run_fn = ScriptedRunFn().when(lambda a: True, returncode=1, stderr="boom")
    engine = ContainerEngine("podman", run_fn=run_fn)
    with pytest.raises(Exception):
        engine.run_detached(name="backend", image="x")


def test_load_streams_without_capture():
    seen_kwargs = {}

    def run_fn(argv, **kwargs):
        seen_kwargs.update(kwargs)
        return FakeProc(0)

    engine = ContainerEngine("podman", run_fn=run_fn)
    engine.load("/bundle/recruit-backend.tar")
    assert "capture_output" not in seen_kwargs


def test_detect_prefers_docker_then_podman():
    which = {"docker": "/usr/bin/docker", "podman": "/usr/bin/podman"}
    engine = ContainerEngine.detect(which_fn=lambda name: which.get(name))
    assert engine.name == "docker"


def test_detect_falls_back_to_podman():
    which = {"podman": "/usr/bin/podman"}
    engine = ContainerEngine.detect(which_fn=lambda name: which.get(name))
    assert engine.name == "podman"


def test_detect_raises_when_none_found():
    with pytest.raises(EngineNotFoundError):
        ContainerEngine.detect(which_fn=lambda name: None)


def test_detect_prefer_missing_raises():
    with pytest.raises(EngineNotFoundError):
        ContainerEngine.detect(prefer="docker", which_fn=lambda name: None)


def test_detect_by_image_prefers_engine_that_has_it():
    which = {"docker": "/usr/bin/docker", "podman": "/usr/bin/podman"}

    def run_fn(argv, **kwargs):
        # docker doesn't have the image, podman does.
        if argv[0] == "docker":
            return FakeProc(returncode=1)
        return FakeProc(returncode=0)

    engine = ContainerEngine.detect_by_image(
        "prefix/recruit-backend:tag", which_fn=lambda n: which.get(n), run_fn=run_fn
    )
    assert engine.name == "podman"


def test_detect_by_image_falls_back_to_plain_detect_when_neither_has_it():
    which = {"docker": "/usr/bin/docker", "podman": "/usr/bin/podman"}
    run_fn = ScriptedRunFn().when(lambda a: True, returncode=1)
    engine = ContainerEngine.detect_by_image(
        "prefix/recruit-backend:tag", which_fn=lambda n: which.get(n), run_fn=run_fn
    )
    assert engine.name == "docker"
