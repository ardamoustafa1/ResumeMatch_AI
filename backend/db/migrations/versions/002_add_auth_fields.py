"""add auth fields

Revision ID: 002
Revises: 001
Create Date: 2026-06-19 13:18:00.000000

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE users ADD COLUMN hashed_password VARCHAR(255);")
    op.execute("UPDATE users SET hashed_password = '!' WHERE hashed_password IS NULL;")
    op.execute("ALTER TABLE users ALTER COLUMN hashed_password SET NOT NULL;")
    op.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;")
    op.execute(
        "ALTER TABLE users ADD COLUMN is_superuser BOOLEAN NOT NULL DEFAULT FALSE;"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS is_superuser;")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS is_active;")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS hashed_password;")
