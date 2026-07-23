from __future__ import annotations

import fcntl
import os
import subprocess

import pytest

from airgap import autoupdate
from airgap.errors import AirgapError, GitDivergedError, HealthCheckError, LockHeldError


def _head(repo_dir) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(repo_dir), capture_output=True, text=True, check=True
    ).stdout.strip()


def _no_lfs_run_fn(argv, **kwargs):
    if argv[:2] == ["git", "lfs"]:
        return subprocess.CompletedProcess(argv, 1, stdout="", stderr="git: 'lfs' is not a git command")
    return subprocess.run(argv, **kwargs)


def _fake_lfs_run_fn(argv, **kwargs):
    if argv[:2] == ["git", "lfs"]:
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")
    return subprocess.run(argv, **kwargs)


def test_up_to_date_returns_false(git_fixture, tmp_path):
    result = autoupdate.cron_update(
        repo_dir=git_fixture.clone_dir, lock_file=tmp_path / "lock", run_fn=_no_lfs_run_fn
    )
    assert result is False


def test_wrong_branch_raises(git_fixture, tmp_path):
    subprocess.run(
        ["git", "checkout", "-q", "-b", "other"], cwd=str(git_fixture.clone_dir), check=True
    )
    with pytest.raises(AirgapError):
        autoupdate.cron_update(repo_dir=git_fixture.clone_dir, lock_file=tmp_path / "lock", run_fn=_no_lfs_run_fn)


def test_diverged_raises_git_diverged_error_and_does_not_reset(git_fixture, tmp_path):
    git_fixture.commit_bundle_change()
    git_fixture.diverge_clone()
    local_head_before = _head(git_fixture.clone_dir)

    with pytest.raises(GitDivergedError):
        autoupdate.cron_update(repo_dir=git_fixture.clone_dir, lock_file=tmp_path / "lock", run_fn=_no_lfs_run_fn)

    # Never auto-resets a diverged deploy-only clone.
    assert _head(git_fixture.clone_dir) == local_head_before


def test_bundle_unchanged_after_merge_returns_false_and_skips_update(git_fixture, tmp_path, monkeypatch):
    git_fixture.commit_unrelated_change()

    def _boom(*args, **kwargs):
        raise AssertionError("apply_bundle must not be called when the bundle is unchanged")

    monkeypatch.setattr(autoupdate.bundle_module, "apply_bundle", _boom)

    result = autoupdate.cron_update(
        repo_dir=git_fixture.clone_dir, lock_file=tmp_path / "lock", run_fn=_no_lfs_run_fn
    )
    assert result is False
    # The ff-only merge itself did happen (repo advanced).
    assert _head(git_fixture.clone_dir) == _head(git_fixture.remote_dir)


def test_bundle_changed_healthy_rolls_out_and_prunes(git_fixture, tmp_path, monkeypatch, fake_engine):
    git_fixture.commit_bundle_change()

    applied = {}

    def fake_apply_bundle(bundle_dir, *, engine, dry_run=False, **kwargs):
        applied["dry_run"] = dry_run
        applied["bundle_dir"] = bundle_dir
        return {"backend": True, "frontend": True}

    pruned = {}

    def fake_prune(bundle_dir, engine, **kwargs):
        pruned["called"] = True

    monkeypatch.setattr(autoupdate.bundle_module, "apply_bundle", fake_apply_bundle)
    monkeypatch.setattr(autoupdate.prune_module, "prune_old_images", fake_prune)
    monkeypatch.setattr(autoupdate.stack_module, "http_ok", lambda url, timeout: True)

    result = autoupdate.cron_update(
        repo_dir=git_fixture.clone_dir,
        lock_file=tmp_path / "lock",
        run_fn=_fake_lfs_run_fn,
        engine=fake_engine,
        health=autoupdate.HealthCheckConfig(retries=1, retry_delay_sec=0),
    )

    assert result is True
    assert applied["dry_run"] is False
    assert pruned.get("called") is True


def test_bundle_changed_unhealthy_raises_and_does_not_prune(git_fixture, tmp_path, monkeypatch, fake_engine):
    git_fixture.commit_bundle_change()

    monkeypatch.setattr(
        autoupdate.bundle_module,
        "apply_bundle",
        lambda bundle_dir, *, engine, dry_run=False, **kwargs: {"backend": False, "frontend": True},
    )
    pruned = {"called": False}
    monkeypatch.setattr(
        autoupdate.prune_module, "prune_old_images", lambda *a, **k: pruned.__setitem__("called", True)
    )
    monkeypatch.setattr(autoupdate.stack_module, "http_ok", lambda url, timeout: False)

    with pytest.raises(HealthCheckError):
        autoupdate.cron_update(
            repo_dir=git_fixture.clone_dir,
            lock_file=tmp_path / "lock",
            run_fn=_fake_lfs_run_fn,
            engine=fake_engine,
            health=autoupdate.HealthCheckConfig(retries=1, retry_delay_sec=0),
        )

    assert pruned["called"] is False


def test_dry_run_makes_zero_git_mutations(git_fixture, tmp_path, monkeypatch, fake_engine):
    git_fixture.commit_bundle_change()
    head_before = _head(git_fixture.clone_dir)

    applied = {}
    monkeypatch.setattr(
        autoupdate.bundle_module,
        "apply_bundle",
        lambda bundle_dir, *, engine, dry_run=False, **kwargs: applied.update(dry_run=dry_run) or {},
    )

    result = autoupdate.cron_update(
        repo_dir=git_fixture.clone_dir,
        lock_file=tmp_path / "lock",
        run_fn=_no_lfs_run_fn,
        engine=fake_engine,
        dry_run=True,
    )

    assert result is False
    assert applied["dry_run"] is True
    # Dry-run must never actually merge -- HEAD is untouched.
    assert _head(git_fixture.clone_dir) == head_before


def test_lock_contention_raises_lock_held_error(git_fixture, tmp_path):
    lock_file = tmp_path / "lock"
    fd = os.open(str(lock_file), os.O_CREAT | os.O_RDWR, 0o644)
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        with pytest.raises(LockHeldError):
            autoupdate.cron_update(repo_dir=git_fixture.clone_dir, lock_file=lock_file, run_fn=_no_lfs_run_fn)
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def test_lfs_absent_warns_and_continues(git_fixture, tmp_path, capsys):
    git_fixture.commit_unrelated_change()
    result = autoupdate.cron_update(
        repo_dir=git_fixture.clone_dir, lock_file=tmp_path / "lock", run_fn=_no_lfs_run_fn
    )
    assert result is False
    out = capsys.readouterr().out
    assert "git-lfs not installed" in out


def test_lfs_present_pulls_without_warning(git_fixture, tmp_path, capsys):
    git_fixture.commit_unrelated_change()
    result = autoupdate.cron_update(
        repo_dir=git_fixture.clone_dir, lock_file=tmp_path / "lock", run_fn=_fake_lfs_run_fn
    )
    assert result is False
    out = capsys.readouterr().out
    assert "git-lfs not installed" not in out
