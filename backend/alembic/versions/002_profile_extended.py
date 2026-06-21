"""Add profile extended fields: bio, preferred_subjects, study_hours_per_day, target_exam_year

Revision ID: 002_profile_extended
Revises: 001_initial_identity
Create Date: 2026-06-17 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_profile_extended"
down_revision: Union[str, None] = "001_initial_identity"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add extended profile fields."""
    op.add_column("profiles", sa.Column("target_exam_year", sa.Integer(), nullable=True))
    op.add_column("profiles", sa.Column("bio", sa.String(length=1000), nullable=True))
    op.add_column("profiles", sa.Column("preferred_subjects", sa.JSON(), nullable=True, server_default=sa.text("'[]'::jsonb")))
    op.add_column("profiles", sa.Column("study_hours_per_day", sa.Float(), nullable=True))
    op.drop_column("profiles", "target_year")


def downgrade() -> None:
    """Remove extended profile fields."""
    op.add_column("profiles", sa.Column("target_year", sa.Integer(), nullable=True))
    op.drop_column("profiles", "study_hours_per_day")
    op.drop_column("profiles", "preferred_subjects")
    op.drop_column("profiles", "bio")
    op.drop_column("profiles", "target_exam_year")