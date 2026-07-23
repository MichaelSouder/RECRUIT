"""Thin wrapper over the `docker`/`podman` CLI, invoked via subprocess.

Every mutating or inspecting call goes through `_run`, which is the one seam
tests can intercept via an injected `run_fn`. Higher-level modules (stack.py,
bundle.py, prune.py) that need to test *sequences* of decisions (e.g. "is
this container already running?") use a hand-written FakeEngine test double
in conftest.py that implements the same public methods instead of injecting
into a real ContainerEngine -- see scripts/airgap/tests/conftest.py.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Callable, Sequence

from . import logging_utils
from .errors import AirgapError, EngineNotFoundError

RunFn = Callable[..., "subprocess.CompletedProcess[str]"]


@dataclass
class CommandResult:
    argv: list[str]
    returncode: int
    stdout: str = ""
    stderr: str = ""

    @property
    def ok(self) -> bool:
        return self.returncode == 0


@dataclass
class ImageRecord:
    repository: str
    tag: str
    image_id: str
    created_at: str = ""


class ContainerEngine:
    """Wraps `docker` or `podman`. `self.name` is the literal CLI binary used."""

    def __init__(self, name: str, run_fn: RunFn | None = None) -> None:
        self.name = name
        self._run_fn = run_fn or subprocess.run

    # -- detection ---------------------------------------------------------

    @classmethod
    def detect(
        cls, *, prefer: str | None = None, which_fn: Callable[[str], str | None] = shutil.which
    ) -> "ContainerEngine":
        """Pick an engine. `prefer` mirrors DOCKER_CMD: if set, it must exist."""
        if prefer:
            if not which_fn(prefer):
                raise EngineNotFoundError(
                    f"Requested container engine not found on PATH: {prefer}",
                    remediation="Install it, or unset DOCKER_CMD/--engine to auto-detect.",
                )
            return cls(prefer)
        for candidate in ("docker", "podman"):
            if which_fn(candidate):
                return cls(candidate)
        raise EngineNotFoundError(
            "Neither docker nor podman found on PATH.",
            remediation="Install one of them, or set DOCKER_CMD / --engine explicitly.",
        )

    @classmethod
    def detect_by_image(
        cls,
        image_hint: str,
        *,
        prefer: str | None = None,
        which_fn: Callable[[str], str | None] = shutil.which,
        run_fn: RunFn | None = None,
    ) -> "ContainerEngine":
        """Like detect(), but prefer whichever engine already has `image_hint`
        loaded when no engine is forced (mirrors airgap-stack-up.sh's
        pick_engine()). `run_fn` is passed through to the constructed engine
        (used by tests to avoid needing a real docker/podman on PATH).
        """
        if prefer:
            if not which_fn(prefer):
                raise EngineNotFoundError(
                    f"Requested container engine not found on PATH: {prefer}",
                    remediation="Install it, or unset DOCKER_CMD/--engine to auto-detect.",
                )
            return cls(prefer, run_fn)
        for candidate in ("docker", "podman"):
            if which_fn(candidate):
                engine = cls(candidate, run_fn)
                if engine.image_exists(image_hint):
                    return engine
        return cls.detect(which_fn=which_fn)

    # -- low-level exec ------------------------------------------------------

    def _run(self, args: Sequence[str], *, stream: bool = False) -> CommandResult:
        argv = [self.name, *args]
        logging_utils.log_cmd(argv)
        if stream:
            proc = self._run_fn(argv, text=True)
            return CommandResult(argv=argv, returncode=proc.returncode)
        proc = self._run_fn(argv, capture_output=True, text=True)
        return CommandResult(
            argv=argv,
            returncode=proc.returncode,
            stdout=proc.stdout or "",
            stderr=proc.stderr or "",
        )

    def _run_checked(self, args: Sequence[str], *, stream: bool = False, error_cls=AirgapError, context: dict | None = None) -> CommandResult:
        result = self._run(args, stream=stream)
        if not result.ok:
            logging_utils.log_cmd_failure(result.argv, result.returncode, result.stderr)
            raise error_cls(
                f"`{self.name} {' '.join(args)}` failed (exit {result.returncode}).",
                context=context,
            )
        return result

    # -- images --------------------------------------------------------------

    def image_exists(self, ref: str) -> bool:
        return self._run(["image", "inspect", ref]).ok

    def image_id(self, ref: str) -> str | None:
        result = self._run(["image", "inspect", ref, "-f", "{{.Id}}"])
        if not result.ok:
            return None
        raw = result.stdout.strip()
        return raw.replace("sha256:", "")[:12] if raw else None

    def image_env(self, ref_or_id: str) -> str:
        """Space-joined Config.Env entries, for tag_if_untagged's marker sniff."""
        result = self._run(["inspect", ref_or_id, "--format", "{{range .Config.Env}}{{.}} {{end}}"])
        return result.stdout if result.ok else ""

    def image_ids(self) -> list[str]:
        result = self._run(["images", "-q"])
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def images(self, repo: str) -> list[ImageRecord]:
        result = self._run(["images", "--format", "{{.Tag}}\t{{.CreatedAt}}\t{{.ID}}", repo])
        records = []
        for line in result.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) != 3:
                continue
            tag, created, image_id = parts
            records.append(ImageRecord(repository=repo, tag=tag, image_id=image_id, created_at=created))
        return records

    def tag(self, source: str, target: str) -> None:
        self._run_checked(["tag", source, target])

    def rmi(self, ref: str) -> bool:
        return self._run(["rmi", ref]).ok

    def image_prune(self) -> None:
        self._run_checked(["image", "prune", "-f"])

    def load(self, tar_path: str) -> None:
        self._run_checked(["load", "-i", tar_path], stream=True)

    # -- containers ------------------------------------------------------------

    def container_exists(self, name: str) -> bool:
        return self._run(["container", "inspect", name]).ok

    def container_running(self, name: str) -> bool:
        result = self._run(["container", "inspect", "-f", "{{.State.Running}}", name])
        return result.ok and result.stdout.strip() == "true"

    def container_image_id(self, name: str) -> str | None:
        result = self._run(["container", "inspect", "-f", "{{.Image}}", name])
        if not result.ok:
            return None
        raw = result.stdout.strip()
        return raw.replace("sha256:", "")[:12] if raw else None

    def rm_container(self, name: str) -> None:
        self._run_checked(["rm", "-f", name])

    def run_detached(
        self,
        *,
        name: str,
        image: str,
        network: str | None = None,
        env: dict[str, str] | None = None,
        publish: str | None = None,
        volume: str | None = None,
        restart: str | None = "unless-stopped",
        extra_hosts: Sequence[str] = (),
        command: Sequence[str] | None = None,
    ) -> None:
        args = ["run", "-d", "--name", name]
        if network:
            args += ["--network", network]
        for host in extra_hosts:
            args += [f"--add-host={host}"]
        for key, val in (env or {}).items():
            args += ["-e", f"{key}={val}"]
        if publish:
            args += ["-p", publish]
        if volume:
            args += ["-v", volume]
        if restart:
            args += ["--restart", restart]
        args.append(image)
        if command:
            args += list(command)
        self._run_checked(args, context={"container": name, "image": image})

    def exec_in(self, name: str, argv: Sequence[str], env: dict[str, str] | None = None) -> CommandResult:
        args = ["exec"]
        for key, val in (env or {}).items():
            args += ["-e", f"{key}={val}"]
        args += [name, *argv]
        return self._run(args)

    # -- network / volume --------------------------------------------------------

    def network_exists(self, name: str) -> bool:
        return self._run(["network", "inspect", name]).ok

    def network_create(self, name: str) -> None:
        if self.network_exists(name):
            return
        self._run_checked(["network", "create", name])

    def volume_create(self, name: str) -> None:
        # Best-effort/idempotent, matches bash's `volume create ... || true`.
        self._run(["volume", "create", name])
