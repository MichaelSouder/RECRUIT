"""index assessments/session_notes subject_id and study_id

These are the columns filtered on every list request (get_assessments,
get_session_notes) and were unindexed while newer tables (study_procedures,
migration_events) got this right from the start. See docs/BACKEND_REVIEW.md §6.

Revision ID: 3253355094fb
Revises: d1e4f9a02b11
Create Date: 2026-07-16

"""
from typing import Sequence, Union

from alembic import op

revision: str = "3253355094fb"
down_revision: Union[str, Sequence[str], None] = "d1e4f9a02b11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(op.f("ix_assessments_subject_id"), "assessments", ["subject_id"], unique=False)
    op.create_index(op.f("ix_assessments_study_id"), "assessments", ["study_id"], unique=False)
    op.create_index(op.f("ix_session_notes_subject_id"), "session_notes", ["subject_id"], unique=False)
    op.create_index(op.f("ix_session_notes_study_id"), "session_notes", ["study_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_session_notes_study_id"), table_name="session_notes")
    op.drop_index(op.f("ix_session_notes_subject_id"), table_name="session_notes")
    op.drop_index(op.f("ix_assessments_study_id"), table_name="assessments")
    op.drop_index(op.f("ix_assessments_subject_id"), table_name="assessments")
