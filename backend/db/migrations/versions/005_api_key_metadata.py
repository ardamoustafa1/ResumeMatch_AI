"""add api key metadata

Revision ID: 005_api_key_metadata
Revises: 4ede89ad0d16
Create Date: 2026-06-20 11:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "005_api_key_metadata"
down_revision: Union[str, Sequence[str], None] = "4ede89ad0d16"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to api_keys
    op.add_column(
        "api_keys",
        sa.Column(
            "name", sa.String(length=100), server_default="Default Key", nullable=False
        ),
    )
    op.add_column(
        "api_keys", sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "api_keys", sa.Column("device_info", sa.String(length=255), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("api_keys", "device_info")
    op.drop_column("api_keys", "last_used_at")
    op.drop_column("api_keys", "name")
