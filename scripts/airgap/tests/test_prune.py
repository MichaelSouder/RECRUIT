from __future__ import annotations

from airgap import manifest, prune
from airgap.engine import ImageRecord


def _manifest():
    return manifest.Manifest(image_prefix="prefix", image_tag="tag", raw={})


def _seed_backend_images(fake_engine, tags_newest_first):
    # created_at values are single characters, descending -- real docker/podman
    # CreatedAt strings are full timestamps that sort correctly lexicographically;
    # this mimics that without fussing over numeric-string sort order.
    letters = "zyxwvutsrqponmlkjihgfedcba"
    records = [
        ImageRecord(repository="prefix/recruit-backend", tag=tag, image_id=f"id-{tag}", created_at=letters[i])
        for i, tag in enumerate(tags_newest_first)
    ]
    fake_engine.image_records["prefix/recruit-backend"] = records
    return records


def test_keeps_running_image_and_keep_old_tags(fake_engine):
    _seed_backend_images(fake_engine, ["v3", "v2", "v1"])
    fake_engine.seed_container("backend", "id-v1", running=True)  # running an OLD tag deliberately

    prune.prune_old_images("/bundle", fake_engine, manifest=_manifest(), keep_old_tags=1)

    removed = {c[1] for c in fake_engine.calls_for("rmi")}
    # v1 protected (running), v3 kept as newest-within-KEEP_OLD_TAGS, v2 removed.
    assert removed == {"prefix/recruit-backend:v2"}


def test_never_touches_postgres_or_redis_repo():
    # _prune_repo is the unit under test here; use a throwaway fake with no images.
    class Dummy:
        name = "podman"

        def images(self, repo):
            raise AssertionError("should never even list images for a protected repo")

    prune._prune_repo(Dummy(), "docker.io/library/postgres", None, keep_old_tags=1, dry_run=False)
    prune._prune_repo(Dummy(), "someprefix/redis-thing", None, keep_old_tags=1, dry_run=False)


def test_dry_run_makes_no_rmi_or_prune_calls(fake_engine):
    _seed_backend_images(fake_engine, ["v3", "v2", "v1"])
    prune.prune_old_images("/bundle", fake_engine, manifest=_manifest(), keep_old_tags=1, dry_run=True)
    assert fake_engine.calls_for("rmi") == []
    assert fake_engine.calls_for("image_prune") == []


def test_no_local_images_is_a_noop(fake_engine):
    prune.prune_old_images("/bundle", fake_engine, manifest=_manifest(), keep_old_tags=1)
    assert fake_engine.calls_for("rmi") == []


def test_rmi_failure_does_not_raise(fake_engine, monkeypatch):
    _seed_backend_images(fake_engine, ["v2", "v1"])
    monkeypatch.setattr(fake_engine, "rmi", lambda ref: False)
    # Should not raise even though rmi() reports failure -- just warns and continues.
    prune.prune_old_images("/bundle", fake_engine, manifest=_manifest(), keep_old_tags=0)
