from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pytest

# Make `airgap` importable without an install step: scripts/ (the parent of
# the airgap/ package) needs to be on sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from airgap.engine import CommandResult, ImageRecord  # noqa: E402


@dataclass
class FakeContainer:
    image: str
    running: bool = True


class FakeEngine:
    """Stateful docker/podman double implementing ContainerEngine's public
    surface. Tracks container/image/network/volume state across calls
    within a test (the postgres/redis lifecycle logic depends on sequential
    inspect results), and records every call for assertions -- in
    particular, tests that assert *zero* mutating calls happened for an
    already-running container.
    """

    def __init__(self, name: str = "podman") -> None:
        self.name = name
        self.containers: dict[str, FakeContainer] = {}
        self.images_present: dict[str, str] = {}  # ref -> image id
        self.image_envs: dict[str, str] = {}  # ref-or-id -> Config.Env string
        self.image_records: dict[str, list[ImageRecord]] = {}  # repo -> records
        self.networks: set[str] = set()
        self.volumes: set[str] = set()
        self.calls: list[tuple] = []

    # -- test setup helpers --------------------------------------------------

    def seed_image(self, ref: str, image_id: str | None = None, env: str = "") -> None:
        self.images_present[ref] = image_id or ref
        if env:
            self.image_envs[ref] = env
            self.image_envs[self.images_present[ref]] = env

    def seed_container(self, name: str, image: str, *, running: bool) -> None:
        self.containers[name] = FakeContainer(image=image, running=running)

    def calls_for(self, method: str) -> list[tuple]:
        return [c for c in self.calls if c[0] == method]

    # -- images ---------------------------------------------------------------

    def image_exists(self, ref: str) -> bool:
        self.calls.append(("image_exists", ref))
        return ref in self.images_present

    def image_id(self, ref: str) -> str | None:
        return self.images_present.get(ref)

    def image_env(self, ref_or_id: str) -> str:
        return self.image_envs.get(ref_or_id, "")

    def image_ids(self) -> list[str]:
        return sorted(set(self.images_present.values()))

    def images(self, repo: str) -> list[ImageRecord]:
        return list(self.image_records.get(repo, []))

    def tag(self, source: str, target: str) -> None:
        self.calls.append(("tag", source, target))
        self.images_present[target] = self.images_present.get(source, source)

    def rmi(self, ref: str) -> bool:
        self.calls.append(("rmi", ref))
        return True

    def image_prune(self) -> None:
        self.calls.append(("image_prune",))

    def load(self, tar_path: str) -> None:
        self.calls.append(("load", tar_path))

    # -- containers -------------------------------------------------------------

    def container_exists(self, name: str) -> bool:
        self.calls.append(("container_exists", name))
        return name in self.containers

    def container_running(self, name: str) -> bool:
        self.calls.append(("container_running", name))
        c = self.containers.get(name)
        return bool(c and c.running)

    def container_image_id(self, name: str) -> str | None:
        c = self.containers.get(name)
        return c.image if c else None

    def rm_container(self, name: str) -> None:
        self.calls.append(("rm_container", name))
        self.containers.pop(name, None)

    def run_detached(self, *, name: str, image: str, **kwargs) -> None:
        self.calls.append(("run_detached", name, image, kwargs))
        self.containers[name] = FakeContainer(image=image, running=True)

    def exec_in(self, name: str, argv, env=None) -> CommandResult:
        self.calls.append(("exec_in", name, tuple(argv)))
        return CommandResult(argv=list(argv), returncode=0, stdout="", stderr="")

    # -- network / volume ---------------------------------------------------------

    def network_exists(self, name: str) -> bool:
        return name in self.networks

    def network_create(self, name: str) -> None:
        self.calls.append(("network_create", name))
        self.networks.add(name)

    def volume_create(self, name: str) -> None:
        self.calls.append(("volume_create", name))
        self.volumes.add(name)


@pytest.fixture
def fake_engine() -> FakeEngine:
    return FakeEngine()


def _run_git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True, text=True)


@dataclass
class GitFixture:
    remote_dir: Path
    clone_dir: Path

    def commit_bundle_change(self, message: str = "bump bundle") -> None:
        bundle = self.remote_dir / "output" / "container-images"
        bundle.mkdir(parents=True, exist_ok=True)
        (bundle / "MANIFEST.txt").write_text(f"IMAGE_TAG={message}\n")
        _run_git(self.remote_dir, "add", "-A")
        _run_git(self.remote_dir, "commit", "-m", message)

    def commit_unrelated_change(self, message: str = "unrelated") -> None:
        (self.remote_dir / "README.md").write_text(message)
        _run_git(self.remote_dir, "add", "-A")
        _run_git(self.remote_dir, "commit", "-m", message)

    def diverge_clone(self) -> None:
        (self.clone_dir / "local-only.txt").write_text("local\n")
        _run_git(self.clone_dir, "add", "-A")
        _run_git(self.clone_dir, "commit", "-m", "local divergent commit")


@pytest.fixture
def git_fixture(tmp_path: Path) -> GitFixture:
    remote_dir = tmp_path / "remote"
    clone_dir = tmp_path / "clone"
    remote_dir.mkdir()

    _run_git(remote_dir, "init", "-q", "-b", "main")
    _run_git(remote_dir, "config", "user.email", "test@example.com")
    _run_git(remote_dir, "config", "user.name", "Test")
    (remote_dir / "README.md").write_text("initial\n")
    _run_git(remote_dir, "add", "-A")
    _run_git(remote_dir, "commit", "-m", "initial")

    subprocess.run(
        ["git", "clone", "-q", str(remote_dir), str(clone_dir)],
        check=True,
        capture_output=True,
        text=True,
    )
    _run_git(clone_dir, "config", "user.email", "test@example.com")
    _run_git(clone_dir, "config", "user.name", "Test")

    return GitFixture(remote_dir=remote_dir, clone_dir=clone_dir)
