import pytest
from pydantic import ValidationError

from app.config import Settings


def test_settings_requires_secret_key(monkeypatch):
    # conftest.py sets SECRET_KEY in the process environment so the rest of the app can
    # boot for every other test; clear it here to exercise the real "nothing set" path.
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(ValidationError, match="secret_key"):
        Settings(_env_file=None)


def test_settings_rejects_short_secret_key(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(ValidationError, match="32 characters"):
        Settings(_env_file=None, secret_key="too-short")


def test_settings_accepts_valid_secret_key():
    settings = Settings(_env_file=None, secret_key="a" * 32)
    assert settings.secret_key == "a" * 32
