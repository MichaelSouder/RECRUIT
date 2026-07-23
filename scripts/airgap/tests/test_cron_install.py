from __future__ import annotations

import subprocess

import pytest

from airgap import cron_install
from airgap.errors import AirgapError


class ScriptedRunFn:
    def __init__(self, list_output: str = "", list_returncode: int = 0):
        self.calls: list[list[str]] = []
        self.list_output = list_output
        self.list_returncode = list_returncode
        self.installed: str | None = None

    def __call__(self, argv, **kwargs):
        self.calls.append(list(argv))
        if argv == ["crontab", "-l"]:
            return subprocess.CompletedProcess(argv, self.list_returncode, stdout=self.list_output, stderr="")
        if argv == ["crontab", "-"]:
            self.installed = kwargs.get("input", "")
            return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")
        raise AssertionError(f"unexpected crontab invocation: {argv}")


def _launcher(tmp_path):
    p = tmp_path / "airgap-cli"
    p.write_text("#!/usr/bin/env python3\n")
    p.chmod(0o755)
    return p


def test_installs_new_entry_when_none_exists(tmp_path):
    launcher = _launcher(tmp_path)
    run_fn = ScriptedRunFn(list_output="", list_returncode=1)  # no crontab yet
    line = cron_install.install_cron(
        launcher_path=launcher,
        schedule="*/30 * * * *",
        log_file=tmp_path / "log" / "cron.log",
        which_fn=lambda n: "/usr/bin/crontab",
        run_fn=run_fn,
    )
    assert str(launcher) in line
    assert "*/30 * * * *" in line
    assert run_fn.installed is not None
    assert line.strip() in run_fn.installed
    assert (tmp_path / "log").is_dir()


def test_idempotent_when_entry_already_present(tmp_path):
    launcher = _launcher(tmp_path)
    existing = f"0 * * * * {launcher} cron-update >> /var/log/x.log 2>&1\n"
    run_fn = ScriptedRunFn(list_output=existing, list_returncode=0)
    line = cron_install.install_cron(
        launcher_path=launcher,
        log_file=tmp_path / "log" / "cron.log",
        which_fn=lambda n: "/usr/bin/crontab",
        run_fn=run_fn,
    )
    assert line.strip() == existing.strip()
    # crontab - (the install step) must never be called when already present.
    assert ["crontab", "-"] not in run_fn.calls


def test_appends_to_existing_unrelated_crontab(tmp_path):
    launcher = _launcher(tmp_path)
    run_fn = ScriptedRunFn(list_output="*/5 * * * * /some/other/job.sh\n", list_returncode=0)
    cron_install.install_cron(
        launcher_path=launcher,
        log_file=tmp_path / "log" / "cron.log",
        which_fn=lambda n: "/usr/bin/crontab",
        run_fn=run_fn,
    )
    assert "/some/other/job.sh" in run_fn.installed
    assert str(launcher) in run_fn.installed


def test_missing_crontab_binary_raises(tmp_path):
    launcher = _launcher(tmp_path)
    with pytest.raises(AirgapError):
        cron_install.install_cron(launcher_path=launcher, which_fn=lambda n: None)


def test_missing_launcher_raises(tmp_path):
    with pytest.raises(AirgapError):
        cron_install.install_cron(launcher_path=tmp_path / "does-not-exist", which_fn=lambda n: "/usr/bin/crontab")
