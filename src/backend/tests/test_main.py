import asyncio
import subprocess
import sys
import textwrap

from app.main import unhandled_exception_handler


def _docs_url_for_environment(environment: str) -> str | None:
    """app.main bakes docs_url into the FastAPI instance at import time based on
    settings.environment, so the only reliable way to test both branches is a fresh
    interpreter with ENVIRONMENT set before app.main is imported."""
    script = textwrap.dedent(f"""
        import os
        os.environ["ENVIRONMENT"] = {environment!r}
        os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production-use-only-32chars")
        # Avoid app.database's postgres-connect-then-fallback probe (slow, and leaves a
        # stray recruit.db file behind) — this test only cares about app.docs_url.
        os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
        from app.main import app
        print(app.docs_url)
    """)
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        check=True,
        cwd=__file__.rsplit("/tests/", 1)[0],
    )
    output = result.stdout.strip()
    return None if output == "None" else output


def test_docs_disabled_in_production():
    assert _docs_url_for_environment("production") is None


def test_docs_enabled_outside_production():
    assert _docs_url_for_environment("development") == "/docs"


def test_unhandled_exception_handler_returns_generic_500():
    class DummyRequest:
        method = "GET"
        url = type("u", (), {"path": "/boom"})()

    response = asyncio.run(unhandled_exception_handler(DummyRequest(), RuntimeError("boom")))
    assert response.status_code == 500
    assert b"Internal server error" in response.body
    assert b"boom" not in response.body  # exception detail isn't leaked to the client
