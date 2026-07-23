"""Parse MANIFEST.txt (produced by export-container-images.sh)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .errors import ManifestError


@dataclass
class Manifest:
    image_prefix: str
    image_tag: str
    raw: dict[str, str]

    def get(self, key: str, default: str = "") -> str:
        return self.raw.get(key, default)


def _parse_lines(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        if key not in values:  # first occurrence wins, matches bash `head -1`
            values[key] = val.strip()
    return values


def parse(path: str | Path) -> Manifest:
    path = Path(path)
    if not path.is_file():
        raise ManifestError(
            f"MANIFEST.txt not found: {path}",
            remediation="Pass the directory that contains MANIFEST.txt (same folder as the .tar files).",
        )
    values = _parse_lines(path.read_text())

    image_prefix = values.get("IMAGE_PREFIX", "")
    if not image_prefix:
        raise ManifestError(
            "Could not read IMAGE_PREFIX from MANIFEST.txt.",
            context={"manifest": str(path)},
        )
    image_tag = values.get("IMAGE_TAG", "")
    if not image_tag:
        raise ManifestError(
            "Could not read IMAGE_TAG from MANIFEST.txt.",
            context={"manifest": str(path)},
        )
    return Manifest(image_prefix=image_prefix, image_tag=image_tag, raw=values)
