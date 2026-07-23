from __future__ import annotations

import pytest

from airgap import bundle, manifest
from airgap.errors import ImageMissingError


def _make_bundle_dir(tmp_path, *, with_manifest=True):
    d = tmp_path / "bundle"
    d.mkdir()
    for name in bundle.REQUIRED_TARS:
        (d / name).write_bytes(b"fake-tar")
    if with_manifest:
        (d / "MANIFEST.txt").write_text("IMAGE_PREFIX=prefix\nIMAGE_TAG=tag\n")
    return d


def test_load_images_happy_path(tmp_path, fake_engine):
    d = _make_bundle_dir(tmp_path)
    m = manifest.parse(d / "MANIFEST.txt")
    bundle.load_images(d, fake_engine, manifest=m)
    load_calls = fake_engine.calls_for("load")
    assert len(load_calls) == 4
    loaded_paths = {c[1] for c in load_calls}
    assert loaded_paths == {str(d / name) for name in bundle.REQUIRED_TARS}


def test_load_images_missing_tar_raises(tmp_path, fake_engine):
    d = tmp_path / "bundle"
    d.mkdir()
    (d / "postgres-15.tar").write_bytes(b"x")
    with pytest.raises(ImageMissingError):
        bundle.load_images(d, fake_engine)


def test_dry_run_makes_zero_load_calls(tmp_path, fake_engine):
    d = _make_bundle_dir(tmp_path)
    m = manifest.parse(d / "MANIFEST.txt")
    bundle.load_images(d, fake_engine, manifest=m, dry_run=True)
    assert fake_engine.calls_for("load") == []
    assert fake_engine.calls_for("tag") == []


def test_tag_if_untagged_fallback_tags_matching_image(tmp_path, fake_engine):
    d = _make_bundle_dir(tmp_path)
    m = manifest.parse(d / "MANIFEST.txt")
    # postgres:15 alias never landed after load, but some untagged image has
    # the PGDATA marker in its env -- the fallback should find and tag it.
    fake_engine.images_present["some-other-id"] = "some-other-id"
    fake_engine.image_envs["some-other-id"] = "PATH=/usr/bin PGDATA=/var/lib/postgresql/data"
    # backend/frontend already tagged directly (no scan needed for these)
    fake_engine.seed_image(f"{m.image_prefix}/recruit-backend:{m.image_tag}")
    fake_engine.seed_image(f"{m.image_prefix}/recruit-frontend:{m.image_tag}")
    fake_engine.seed_image("docker.io/library/redis:7-alpine")

    bundle.load_images(d, fake_engine, manifest=m)

    assert fake_engine.images_present["docker.io/library/postgres:15"] == "some-other-id"
    tag_calls = fake_engine.calls_for("tag")
    assert ("tag", "some-other-id", "docker.io/library/postgres:15") in tag_calls


def test_tag_if_untagged_warns_when_nothing_matches(tmp_path, fake_engine, capsys):
    d = _make_bundle_dir(tmp_path)
    m = manifest.parse(d / "MANIFEST.txt")
    fake_engine.seed_image(f"{m.image_prefix}/recruit-backend:{m.image_tag}")
    fake_engine.seed_image(f"{m.image_prefix}/recruit-frontend:{m.image_tag}")
    fake_engine.seed_image("docker.io/library/redis:7-alpine")
    # postgres image never appears anywhere, and no untagged image has PGDATA.
    bundle.load_images(d, fake_engine, manifest=m)
    out = capsys.readouterr().out
    assert "Could not find image to tag as docker.io/library/postgres:15" in out
