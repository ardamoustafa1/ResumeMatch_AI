"""add mfa fields

Revision ID: 007_add_mfa
Revises: 006_audit_status
Create Date: 2026-06-21 13:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "007_add_mfa"
down_revision: Union[str, Sequence[str], None] = "006_audit_status"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("totp_secret", sa.String(length=32), nullable=True))
    op.add_column("users", sa.Column("mfa_enabled", sa.Boolean(), server_default="false", nullable=False))


def downgrade() -> None:
    op.drop_column("users", "mfa_enabled")
    op.drop_column("users", "totp_secret")
