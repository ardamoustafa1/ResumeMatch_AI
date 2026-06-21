"""add team workspaces

Revision ID: 008_team_workspaces
Revises: 007_add_mfa
Create Date: 2026-06-21 15:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "008_team_workspaces"
down_revision: Union[str, Sequence[str], None] = "007_add_mfa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workspaces",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    
    op.create_table(
        "workspace_members",
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.String(length=20), server_default="member", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("workspace_id", "user_id")
    )
    
    op.add_column("analyses", sa.Column("workspace_id", sa.UUID(), nullable=True))
    op.create_foreign_key("fk_analyses_workspace_id", "analyses", "workspaces", ["workspace_id"], ["id"], ondelete="SET NULL")
    op.create_index(op.f("ix_analyses_workspace_id"), "analyses", ["workspace_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_analyses_workspace_id"), table_name="analyses")
    op.drop_constraint("fk_analyses_workspace_id", "analyses", type_="foreignkey")
    op.drop_column("analyses", "workspace_id")
    
    op.drop_table("workspace_members")
    op.drop_table("workspaces")
