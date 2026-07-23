"""encrypt subjects.ssn at rest

Widens subjects.ssn from VARCHAR to TEXT (Fernet ciphertext is much longer than a
9-digit SSN) and encrypts any existing plaintext values with the key derived from
SSN_ENCRYPTION_KEY (see app/core/encryption.py). Idempotent in both directions: a value
that already decrypts under the current key is left alone on upgrade, and a value that
doesn't decrypt is left alone on downgrade — so re-running against a partially-migrated
database is a no-op rather than double-encrypting or corrupting data.

Requires SSN_ENCRYPTION_KEY to be set to the same value used at the time this runs and
thereafter — alembic/env.py already imports app.config.settings, which fails fast if it
isn't. Back this key up before running against production; there is no way to recover
existing SSNs if it's lost.

Revision ID: 8d5c3e1a9f47
Revises: 3253355094fb
Create Date: 2026-07-16

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from cryptography.fernet import InvalidToken

from app.core.encryption import get_fernet

revision: str = "8d5c3e1a9f47"
down_revision: Union[str, Sequence[str], None] = "3253355094fb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_subjects = sa.table("subjects", sa.column("id", sa.Integer), sa.column("ssn", sa.Text))


def upgrade() -> None:
    op.alter_column("subjects", "ssn", type_=sa.Text(), existing_type=sa.String(), existing_nullable=True)

    fernet = get_fernet()
    connection = op.get_bind()
    rows = connection.execute(sa.select(_subjects.c.id, _subjects.c.ssn).where(_subjects.c.ssn.isnot(None))).fetchall()
    for row in rows:
        try:
            fernet.decrypt(row.ssn.encode())
            continue  # already encrypted under the current key
        except InvalidToken:
            pass
        encrypted = fernet.encrypt(row.ssn.encode()).decode()
        connection.execute(_subjects.update().where(_subjects.c.id == row.id).values(ssn=encrypted))


def downgrade() -> None:
    fernet = get_fernet()
    connection = op.get_bind()
    rows = connection.execute(sa.select(_subjects.c.id, _subjects.c.ssn).where(_subjects.c.ssn.isnot(None))).fetchall()
    for row in rows:
        try:
            decrypted = fernet.decrypt(row.ssn.encode()).decode()
        except InvalidToken:
            continue  # not encrypted under the current key — leave as-is
        connection.execute(_subjects.update().where(_subjects.c.id == row.id).values(ssn=decrypted))

    op.alter_column("subjects", "ssn", type_=sa.String(), existing_type=sa.Text(), existing_nullable=True)
