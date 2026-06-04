"""user_study.study_role for per-study access level

Revision ID: c7a2b1f04e90
Revises: b3e8a1c92d40
Create Date: 2026-05-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c7a2b1f04e90"
down_revision: Union[str, Sequence[str], None] = "b3e8a1c92d40"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_study",
        sa.Column(
            "study_role",
            sa.String(),
            nullable=False,
            server_default="viewer",
        ),
    )
    # Keep server_default so legacy INSERT (user_id, study_id) still works.


def downgrade() -> None:
    op.drop_column("user_study", "study_role")
