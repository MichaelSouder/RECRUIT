"""Parse recruit-airgap.env style KEY=value files (port of airgap-stack-up.sh's
load_env_file). Blank lines and #-comments are skipped, an optional leading
`export ` is allowed, and one matching pair of surrounding quotes is
stripped from the value. Variables already present in the target environment
are never overridden -- shell exports win over the file, same as the bash
version.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from . import logging_utils

_LINE_RE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$")


def parse_env_file(path: str | Path) -> dict[str, str]:
    path = Path(path)
    values: dict[str, str] = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.rstrip("\r")
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = _LINE_RE.match(line)
        if not match:
            logging_utils.log_warn(f"Skipping malformed env line: {line[:72]}")
            continue
        key, val = match.group(1), match.group(2).strip()
        if len(val) >= 2 and ((val[0] == val[-1] == '"') or (val[0] == val[-1] == "'")):
            val = val[1:-1]
        values[key] = val
    return values


def apply_env_file(path: str | Path, environ: dict[str, str] | None = None) -> dict[str, str]:
    """Load `path` into `environ` (defaults to os.environ) without overriding
    keys already present. Returns the subset that was actually applied.
    """
    if environ is None:
        environ = os.environ
    values = parse_env_file(path)
    applied: dict[str, str] = {}
    for key, val in values.items():
        if key in environ:
            continue
        environ[key] = val
        applied[key] = val
    logging_utils.log_ok(
        f"Loaded env file: {path} ({len(applied)} variable(s) applied; existing shell vars kept)."
    )
    return applied
