from __future__ import annotations

import pytest

from airgap import cli
from airgap.errors import AirgapError, LockHeldError


def test_help_exits_zero():
    parser = cli.build_parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["--help"])
    assert exc.value.code == 0


def test_unknown_command_exits_nonzero():
    parser = cli.build_parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(["not-a-command"])
    assert exc.value.code != 0


def test_no_command_exits_nonzero():
    parser = cli.build_parser()
    with pytest.raises(SystemExit) as exc:
        parser.parse_args([])
    assert exc.value.code != 0


def test_main_prints_error_and_returns_its_exit_code(monkeypatch, capsys):
    def boom(args):
        raise AirgapError("something broke", remediation="try again")

    monkeypatch.setattr(cli, "_cmd_stack_up", boom)
    code = cli.main(["stack-up", "/nonexistent"])
    assert code == 1
    err = capsys.readouterr().err
    assert "something broke" in err


def test_main_zero_exit_code_error_is_not_collapsed_to_one(monkeypatch, capsys):
    def boom(args):
        raise LockHeldError("already running")

    monkeypatch.setattr(cli, "_cmd_cron_update", boom)
    code = cli.main(["cron-update"])
    assert code == 0


def test_main_unexpected_exception_returns_one(monkeypatch):
    def boom(args):
        raise ValueError("surprise")

    monkeypatch.setattr(cli, "_cmd_stack_up", boom)
    code = cli.main(["stack-up"])
    assert code == 1


def test_default_bundle_dir_prefers_output_container_images(tmp_path):
    (tmp_path / "output" / "container-images").mkdir(parents=True)
    (tmp_path / "output" / "container-images" / "MANIFEST.txt").write_text("x")
    (tmp_path / "container-images").mkdir()
    (tmp_path / "container-images" / "recruit-backend.tar").write_bytes(b"x")
    found = cli._default_bundle_dir(tmp_path)
    assert found == tmp_path / "output" / "container-images"


def test_default_bundle_dir_falls_back_to_container_images(tmp_path):
    (tmp_path / "container-images").mkdir()
    (tmp_path / "container-images" / "recruit-backend.tar").write_bytes(b"x")
    found = cli._default_bundle_dir(tmp_path)
    assert found == tmp_path / "container-images"


def test_default_bundle_dir_raises_when_none_found(tmp_path):
    with pytest.raises(AirgapError):
        cli._default_bundle_dir(tmp_path)


def test_install_cron_uses_repo_root_launcher_by_default(monkeypatch):
    captured = {}

    def fake_install(*, launcher_path, schedule, log_file):
        captured["launcher_path"] = launcher_path
        return "line"

    monkeypatch.setattr(cli.cron_install, "install_cron", fake_install)
    parser = cli.build_parser()
    args = parser.parse_args(["install-cron"])
    cli._cmd_install_cron(args)
    assert captured["launcher_path"] == cli.REPO_ROOT / "scripts" / "airgap-cli"
