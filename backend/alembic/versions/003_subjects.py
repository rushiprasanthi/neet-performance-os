"""Create subjects table.

Revision ID: 003_subjects
Revises: 002_profile_extended
Create Date: 2026-06-17 10:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "003_subjects"
down_revision: Union[str, None] = "002_profile_extended"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "subjects",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(
        "ix_subjects_name_active",
        "subjects",
        ["name"],
        postgresql_where=sa.text("is_active = true")
    )
    op.create_index(
        "ix_subjects_code_active",
        "subjects",
        ["code"],
        postgresql_where=sa.text("is_active = true")
    )


def downgrade() -> None:
    op.drop_index(
        "ix_subjects_code_active",
        table_name="subjects",
        postgresql_where=sa.text("is_active = true")
    )
    op.drop_index(
        "ix_subjects_name_active",
        table_name="subjects",
        postgresql_where=sa.text("is_active = true")
    )
    op.drop_table("subjects")