"""study_procedures for arc.studyproc_list matrix

Revision ID: d1e4f9a02b11
Revises: c7a2b1f04e90
Create Date: 2026-05-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d1e4f9a02b11"
down_revision: Union[str, Sequence[str], None] = "c7a2b1f04e90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "study_procedures",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("proc_code", sa.String(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column("legacy_index", sa.Integer(), nullable=True),
        sa.Column("data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["study_id"], ["studies.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("study_id", "proc_code", name="uq_study_procedures_study_proc"),
    )
    op.create_index(op.f("ix_study_procedures_id"), "study_procedures", ["id"], unique=False)
    op.create_index(op.f("ix_study_procedures_study_id"), "study_procedures", ["study_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_study_procedures_study_id"), table_name="study_procedures")
    op.drop_index(op.f("ix_study_procedures_id"), table_name="study_procedures")
    op.drop_table("study_procedures")
