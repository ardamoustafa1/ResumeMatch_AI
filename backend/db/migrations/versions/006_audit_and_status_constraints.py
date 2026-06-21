"""add audit events and analysis status constraint

Revision ID: 006_audit_status
Revises: 005_api_key_metadata
Create Date: 2026-06-21 12:00:00.000000
"""

from alembic import op

revision = "006_audit_status"
down_revision = "005_api_key_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE analyses
        ADD CONSTRAINT ck_analyses_status
        CHECK (
            status IN (
                'pending',
                'processing',
                'completed',
                'partial_completed',
                'failed'
            )
        );
        """
    )
    op.execute(
        """
        CREATE TABLE audit_events (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE SET NULL,
            event_type VARCHAR(100) NOT NULL,
            ip_address INET,
            user_agent VARCHAR(255),
            metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    op.execute(
        "CREATE INDEX idx_audit_events_user_created "
        "ON audit_events(user_id, created_at DESC);"
    )
    op.execute(
        "CREATE INDEX idx_audit_events_type_created "
        "ON audit_events(event_type, created_at DESC);"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS audit_events;")
    op.execute(
        "ALTER TABLE analyses DROP CONSTRAINT IF EXISTS ck_analyses_status;"
    )
