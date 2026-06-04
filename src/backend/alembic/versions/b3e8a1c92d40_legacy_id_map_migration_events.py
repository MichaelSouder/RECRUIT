"""legacy_id_map, migration_events, migration system user

Revision ID: b3e8a1c92d40
Revises: 570711e1fdf8
Create Date: 2026-05-07

Password for migration-system@recruit.internal (placeholder; rotate in production):
  MigrationSystem!DoNotUse0
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "b3e8a1c92d40"
down_revision: Union[str, Sequence[str], None] = "570711e1fdf8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# bcrypt hash for MigrationSystem!DoNotUse0 (see module docstring)
_MIGRATION_USER_HASH = (
    "$2b$12$109o43ODubiH1oAqtn/mWufaetmaeXETPlSDORd010QTOV0ALOZV."
)
_MIGRATION_USER_EMAIL = "migration-system@recruit.internal"


def upgrade() -> None:
    op.create_table(
        "legacy_id_map",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_system", sa.String(length=64), nullable=False),
        sa.Column("source_table", sa.String(length=255), nullable=False),
        sa.Column("source_pk", sa.String(length=255), nullable=False),
        sa.Column("target_table", sa.String(length=64), nullable=False),
        sa.Column("target_pk", sa.Integer(), nullable=False),
        sa.Column("batch_id", sa.String(length=64), nullable=False),
        sa.Column("imported_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_system",
            "source_table",
            "source_pk",
            name="uq_legacy_id_map_source_row",
        ),
    )
    op.create_index(
        "ix_legacy_id_map_source_system", "legacy_id_map", ["source_system"], unique=False
    )
    op.create_index(
        "ix_legacy_id_map_target", "legacy_id_map", ["target_table", "target_pk"], unique=False
    )
    op.create_index("ix_legacy_id_map_batch_id", "legacy_id_map", ["batch_id"], unique=False)

    op.create_table(
        "migration_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("batch_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("detail", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("subject_id", sa.Integer(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_migration_events_batch_id", "migration_events", ["batch_id"], unique=False
    )
    op.create_index(
        "ix_migration_events_event_type", "migration_events", ["event_type"], unique=False
    )
    op.create_index(
        "ix_migration_events_subject_id", "migration_events", ["subject_id"], unique=False
    )
    op.create_index(
        "ix_migration_events_created_by_user_id",
        "migration_events",
        ["created_by_user_id"],
        unique=False,
    )
    op.create_index("ix_migration_events_id", "migration_events", ["id"], unique=False)

    # Literal SQL: constants only (documented placeholder password).
    op.execute(
        f"""
        INSERT INTO users (
            email, hashed_password, full_name, location, phone, piv_certificate_id,
            is_active, is_superuser, role, created_at, updated_at
        )
        SELECT
            '{_MIGRATION_USER_EMAIL}',
            '{_MIGRATION_USER_HASH}',
            'Legacy migration system account',
            NULL, NULL, NULL,
            TRUE, FALSE, 'admin',
            (NOW() AT TIME ZONE 'UTC'), (NOW() AT TIME ZONE 'UTC')
        WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = '{_MIGRATION_USER_EMAIL}');
        """
    )


def downgrade() -> None:
    op.execute("DELETE FROM migration_events")
    op.drop_index("ix_migration_events_id", table_name="migration_events")
    op.drop_index("ix_migration_events_created_by_user_id", table_name="migration_events")
    op.drop_index("ix_migration_events_subject_id", table_name="migration_events")
    op.drop_index("ix_migration_events_event_type", table_name="migration_events")
    op.drop_index("ix_migration_events_batch_id", table_name="migration_events")
    op.drop_table("migration_events")

    op.execute("DELETE FROM legacy_id_map")
    op.drop_index("ix_legacy_id_map_batch_id", table_name="legacy_id_map")
    op.drop_index("ix_legacy_id_map_target", table_name="legacy_id_map")
    op.drop_index("ix_legacy_id_map_source_system", table_name="legacy_id_map")
    op.drop_table("legacy_id_map")

    op.execute(f"DELETE FROM users WHERE email = '{_MIGRATION_USER_EMAIL}'")
