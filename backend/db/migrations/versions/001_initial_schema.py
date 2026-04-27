"""initial schema

Revision ID: 001
Revises: 
Create Date: 2026-04-27 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use native UUID generation. We can enable pgcrypto just in case for older PG versions.
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

    op.execute("""
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)

    op.execute("""
        CREATE TABLE analyses (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            cv_text TEXT NOT NULL,
            jd_text TEXT NOT NULL,
            company TEXT,
            recruiter_name TEXT,
            status VARCHAR(20) DEFAULT 'pending',
            result JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)
    op.execute("CREATE INDEX idx_analyses_user_id ON analyses(user_id);")
    op.execute("CREATE INDEX idx_analyses_status ON analyses(status);")

    op.execute("""
        CREATE TABLE outreach_messages (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
            generated_message TEXT NOT NULL,
            model_used VARCHAR(50) NOT NULL,
            is_edited BOOLEAN DEFAULT FALSE,
            final_message TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)
    op.execute("CREATE INDEX idx_outreach_messages_analysis_id ON outreach_messages(analysis_id);")

    op.execute("""
        CREATE TABLE telegram_configs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            chat_id VARCHAR(50) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id)
        );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS telegram_configs CASCADE;")
    op.execute("DROP TABLE IF EXISTS outreach_messages CASCADE;")
    op.execute("DROP TABLE IF EXISTS analyses CASCADE;")
    op.execute("DROP TABLE IF EXISTS users CASCADE;")
