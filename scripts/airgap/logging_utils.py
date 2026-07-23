"""Console logging matching the visual language of the old bash scripts
(log_info/log_ok/log_warn/log_err), plus a debug/verbose mode for tracing
subprocess calls and replaying captured stderr on failure.

Deliberately not built on the stdlib `logging` module: the old scripts were
simple line-oriented colored echo, and matching that directly keeps this
package dependency-free and easy to read end to end.
"""

from __future__ import annotations

import os
import sys

_NC = "\033[0m"
_CYAN = "\033[0;36m"
_GREEN = "\033[0;32m"
_YELLOW = "\033[0;33m"
_RED = "\033[0;31m"
_DIM = "\033[2m"

_debug_enabled = bool(os.environ.get("AIRGAP_DEBUG"))


def set_debug(enabled: bool) -> None:
    global _debug_enabled
    _debug_enabled = enabled


def is_debug() -> bool:
    return _debug_enabled


def _use_color(stream) -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    try:
        return stream.isatty()
    except (AttributeError, ValueError):
        return False


def _emit(stream, color: str, tag: str, msg: str) -> None:
    if _use_color(stream):
        print(f"{color}[{tag}]{_NC}  {msg}", file=stream)
    else:
        print(f"[{tag}]  {msg}", file=stream)


def log_info(msg: str) -> None:
    _emit(sys.stdout, _CYAN, "INFO", msg)


def log_ok(msg: str) -> None:
    _emit(sys.stdout, _GREEN, " OK ", msg)


def log_warn(msg: str) -> None:
    _emit(sys.stdout, _YELLOW, "WARN", msg)


def log_err(msg: str) -> None:
    _emit(sys.stderr, _RED, "ERR ", msg)


def log_debug(msg: str) -> None:
    if not _debug_enabled:
        return
    if _use_color(sys.stderr):
        print(f"{_DIM}[DBUG]  {msg}{_NC}", file=sys.stderr)
    else:
        print(f"[DBUG]  {msg}", file=sys.stderr)


def format_argv(argv: list[str]) -> str:
    return " ".join(argv)


def log_cmd(argv: list[str]) -> None:
    """Trace the exact command about to be run. Only prints in debug mode."""
    log_debug(f"$ {format_argv(argv)}")


def log_cmd_failure(argv: list[str], returncode: int, stderr_tail: str) -> None:
    """Print the failing command and a tail of its stderr for copy-paste debugging.

    Always prints (not gated on debug mode) since this only fires on an
    actual failure, where the extra detail is worth the noise.
    """
    log_err(f"Command failed (exit {returncode}): {format_argv(argv)}")
    tail = stderr_tail.strip()
    if tail:
        for line in tail.splitlines()[-20:]:
            log_err(f"  | {line}")
