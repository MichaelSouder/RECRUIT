from __future__ import annotations

import pytest

from airgap import manifest
from airgap.errors import ManifestError


def test_parse_valid(tmp_path):
    path = tmp_path / "MANIFEST.txt"
    path.write_text("IMAGE_PREFIX=registry.example.com/recruit\nIMAGE_TAG=2026-07-16\nEXTRA=1\n")
    m = manifest.parse(path)
    assert m.image_prefix == "registry.example.com/recruit"
    assert m.image_tag == "2026-07-16"
    assert m.get("EXTRA") == "1"
    assert m.get("MISSING", "default") == "default"


def test_missing_file_raises(tmp_path):
    with pytest.raises(ManifestError):
        manifest.parse(tmp_path / "MANIFEST.txt")


def test_missing_image_prefix_raises(tmp_path):
    path = tmp_path / "MANIFEST.txt"
    path.write_text("IMAGE_TAG=2026-07-16\n")
    with pytest.raises(ManifestError):
        manifest.parse(path)


def test_missing_image_tag_raises(tmp_path):
    path = tmp_path / "MANIFEST.txt"
    path.write_text("IMAGE_PREFIX=registry.example.com/recruit\n")
    with pytest.raises(ManifestError):
        manifest.parse(path)


def test_first_occurrence_wins(tmp_path):
    path = tmp_path / "MANIFEST.txt"
    path.write_text("IMAGE_PREFIX=first\nIMAGE_PREFIX=second\nIMAGE_TAG=t\n")
    m = manifest.parse(path)
    assert m.image_prefix == "first"


def test_comments_and_blanks_ignored(tmp_path):
    path = tmp_path / "MANIFEST.txt"
    path.write_text("# comment\n\nIMAGE_PREFIX=p\nIMAGE_TAG=t\n")
    m = manifest.parse(path)
    assert m.image_prefix == "p"
    assert m.image_tag == "t"
