"""Port of install-airgap-cron.sh: idempotent crontab installer for the
hourly auto-update job.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Callable

from . import logging_utils
from .errors import AirgapError

DEFAULT_SCHEDULE = "0 * * * *"
DEFAULT_LOG_FILE = "/var/log/recruit/airgap-cron-update.log"

RunFn = Callable[..., "subprocess.CompletedProcess[str]"]


def install_cron(
    *,
    launcher_path: str | Path,
    schedule: str = DEFAULT_SCHEDULE,
    log_file: str | Path = DEFAULT_LOG_FILE,
    which_fn: Callable[[str], str | None] = shutil.which,
    run_fn: RunFn = subprocess.run,
) -> str:
    """Adds `<schedule> <launcher_path> cron-update >> <log_file> 2>&1` to the
    current user's crontab, unless a line for this launcher already exists.
    Returns the crontab line that's in effect afterward (new or pre-existing).
    """
    launcher_path = Path(launcher_path).expanduser().resolve()
    if not launcher_path.is_file():
        raise AirgapError(f"Launcher not found: {launcher_path}")

    if not which_fn("crontab"):
        raise AirgapError(
            "crontab not found on this host.",
            remediation="This installer requires cron; install it or add the schedule manually.",
        )

    log_file = Path(log_file)
    log_dir = log_file.parent
    if not log_dir.is_dir():
        logging_utils.log_info(f"Creating log directory: {log_dir}")
        log_dir.mkdir(parents=True, exist_ok=True)

    cron_line = f"{schedule} {launcher_path} cron-update >> {log_file} 2>&1"

    existing = run_fn(["crontab", "-l"], capture_output=True, text=True)
    existing_text = existing.stdout if existing.returncode == 0 else ""

    for line in existing_text.splitlines():
        if str(launcher_path) in line:
            logging_utils.log_ok(f"A cron entry for {launcher_path} already exists; leaving crontab unchanged.")
            logging_utils.log_info(line)
            return line

    new_crontab = existing_text
    if new_crontab and not new_crontab.endswith("\n"):
        new_crontab += "\n"
    new_crontab += cron_line + "\n"

    result = run_fn(["crontab", "-"], input=new_crontab, capture_output=True, text=True)
    if result.returncode != 0:
        raise AirgapError(f"Failed to install crontab entry: {result.stderr.strip()}")

    logging_utils.log_ok("Installed cron entry:")
    logging_utils.log_info(f"  {cron_line}")
    return cron_line
