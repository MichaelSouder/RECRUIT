#!/usr/bin/env python3
"""
Backward-compatible entry point — delegates to db_snapshot_pdf.py --preset recruit.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    script = Path(__file__).resolve().parent / "db_snapshot_pdf.py"
    r = subprocess.run(
        [sys.executable, str(script), "--preset", "recruit", *sys.argv[1:]],
        check=False,
    )
    raise SystemExit(r.returncode)
