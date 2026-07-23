from __future__ import annotations

from airgap import envfile


def test_parse_basic(tmp_path):
    path = tmp_path / "recruit-airgap.env"
    path.write_text(
        "\n"
        "# a comment\n"
        "SECRET_KEY=abc123\n"
        "export INITIAL_ADMIN_PASSWORD=hunter22\n"
        '  QUOTED="value with spaces"  \n'
        "SINGLE='single quoted'\n"
        "MIXED_QUOTES=\"unbalanced'\n"
    )
    values = envfile.parse_env_file(path)
    assert values["SECRET_KEY"] == "abc123"
    assert values["INITIAL_ADMIN_PASSWORD"] == "hunter22"
    assert values["QUOTED"] == "value with spaces"
    assert values["SINGLE"] == "single quoted"
    # Unbalanced quote pair is left as-is (only a matching pair is stripped).
    assert values["MIXED_QUOTES"] == "\"unbalanced'"


def test_malformed_line_skipped(tmp_path, capsys):
    path = tmp_path / "e.env"
    path.write_text("not a valid line\nGOOD=1\n")
    values = envfile.parse_env_file(path)
    assert values == {"GOOD": "1"}


def test_apply_env_file_does_not_override_existing(tmp_path):
    path = tmp_path / "e.env"
    path.write_text("KEY_A=from_file\nKEY_B=from_file\n")
    environ = {"KEY_A": "from_shell"}
    applied = envfile.apply_env_file(path, environ)
    assert environ["KEY_A"] == "from_shell"
    assert environ["KEY_B"] == "from_file"
    assert applied == {"KEY_B": "from_file"}


def test_apply_env_file_reports_only_applied(tmp_path):
    path = tmp_path / "e.env"
    path.write_text("A=1\nB=2\n")
    environ: dict[str, str] = {}
    applied = envfile.apply_env_file(path, environ)
    assert applied == {"A": "1", "B": "2"}
    assert environ == {"A": "1", "B": "2"}
