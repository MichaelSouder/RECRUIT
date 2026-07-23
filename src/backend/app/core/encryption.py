import base64
import hashlib

from cryptography.fernet import Fernet
from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator

from app.config import settings


def _derive_fernet_key(passphrase: str) -> bytes:
    """Fernet requires a 32-byte urlsafe-base64 key; SSN_ENCRYPTION_KEY is an arbitrary
    32+ char passphrase (same shape as SECRET_KEY), so hash it down to a fixed-size key."""
    return base64.urlsafe_b64encode(hashlib.sha256(passphrase.encode()).digest())


_fernet = Fernet(_derive_fernet_key(settings.ssn_encryption_key))


def get_fernet() -> Fernet:
    """Exposes the module's Fernet instance for one-off encrypt/decrypt work outside the
    ORM column path — e.g. the Alembic migration that backfills existing plaintext SSNs."""
    return _fernet


class EncryptedString(TypeDecorator):
    """Encrypts a string column at rest with Fernet (AES-128-CBC + HMAC, random IV per
    write). Never use this on a column that needs equality/LIKE filtering — ciphertext is
    non-deterministic, so the same plaintext never encrypts to the same value twice.
    """

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return _fernet.encrypt(value.encode()).decode()

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return _fernet.decrypt(value.encode()).decode()
