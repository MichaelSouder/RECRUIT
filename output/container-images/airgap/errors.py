"""Exception hierarchy for the air-gap tooling.

Every error that should produce a clean, actionable message at the CLI level
(rather than a raw traceback) is an AirgapError. Each carries a `context`
dict identifying what was being done (which container/image/step) so detail
isn't lost when the exception is caught several call-frames away from where
it was raised, plus a `remediation` hint and a process exit code.
"""

from __future__ import annotations

from typing import Any


class AirgapError(Exception):
    """Base for all expected/handled failures in the air-gap tooling."""

    exit_code = 1

    def __init__(
        self,
        message: str,
        *,
        remediation: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.remediation = remediation
        self.context = context or {}

    def __str__(self) -> str:  # pragma: no cover - trivial
        parts = [self.message]
        if self.context:
            ctx = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"[{ctx}]")
        if self.remediation:
            parts.append(f"\n  -> {self.remediation}")
        return " ".join(parts[:2]) + ("".join(parts[2:]) if len(parts) > 2 else "")


class EngineNotFoundError(AirgapError):
    """Neither docker nor podman (or an explicitly requested engine) was found."""

    exit_code = 1


class ImageMissingError(AirgapError):
    """A required image is not present in the local container engine."""

    exit_code = 1


class ManifestError(AirgapError):
    """MANIFEST.txt is missing or missing a required key."""

    exit_code = 1


class SecretsError(AirgapError):
    """A required secret (SECRET_KEY, INITIAL_ADMIN_PASSWORD, ...) is missing or too short."""

    exit_code = 1


class HealthCheckError(AirgapError):
    """Backend/frontend did not become healthy within the retry budget."""

    exit_code = 1


class GitDivergedError(AirgapError):
    """The deploy clone has diverged from the tracked remote branch (ff-only merge failed)."""

    exit_code = 1


class LockHeldError(AirgapError):
    """Another instance is already running. Callers should treat this as benign (exit 0)."""

    exit_code = 0
