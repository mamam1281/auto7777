 """Add JWT auth models manually

Revision ID: fd7d48eb32b8
Revises: 359612bc3b0c
Create Date: 2025-07-31 09:39:28.792431

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd7d48eb32b8'
down_revision: Union[str, None] = '359612bc3b0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add last_login_at column to users table
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(), nullable=True))
    
    # Create login_attempts table
    op.create_table('login_attempts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('site_id', sa.String(length=50), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('attempted_at', sa.DateTime(), nullable=False),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('failure_reason', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_login_attempts_id', 'login_attempts', ['id'], unique=False)
    op.create_index('ix_login_attempts_site_id', 'login_attempts', ['site_id'], unique=False)
    op.create_index('ix_login_attempts_ip_address', 'login_attempts', ['ip_address'], unique=False)
    op.create_index('ix_login_attempts_success', 'login_attempts', ['success'], unique=False)
    op.create_index('ix_login_attempts_attempted_at', 'login_attempts', ['attempted_at'], unique=False)
    op.create_index('ix_login_attempts_site_id_attempted_at', 'login_attempts', ['site_id', 'attempted_at'], unique=False)
    op.create_index('ix_login_attempts_ip_attempted_at', 'login_attempts', ['ip_address', 'attempted_at'], unique=False)
    
    # Create refresh_tokens table
    op.create_table('refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sa.String(length=128), nullable=False),
        sa.Column('device_fingerprint', sa.String(length=128), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('is_revoked', sa.Boolean(), nullable=False),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('revoke_reason', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_refresh_tokens_id', 'refresh_tokens', ['id'], unique=False)
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'], unique=False)
    op.create_index('ix_refresh_tokens_token_hash', 'refresh_tokens', ['token_hash'], unique=True)
    op.create_index('ix_refresh_tokens_device_fingerprint', 'refresh_tokens', ['device_fingerprint'], unique=False)
    op.create_index('ix_refresh_tokens_expires_at', 'refresh_tokens', ['expires_at'], unique=False)
    op.create_index('ix_refresh_tokens_is_revoked', 'refresh_tokens', ['is_revoked'], unique=False)
    op.create_index('ix_refresh_tokens_user_id_created_at', 'refresh_tokens', ['user_id', 'created_at'], unique=False)
    op.create_index('ix_refresh_tokens_expires_at_revoked', 'refresh_tokens', ['expires_at', 'is_revoked'], unique=False)
    
    # Create user_sessions table
    op.create_table('user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=128), nullable=False),
        sa.Column('device_fingerprint', sa.String(length=128), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('login_at', sa.DateTime(), nullable=False),
        sa.Column('last_activity_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('logout_at', sa.DateTime(), nullable=True),
        sa.Column('logout_reason', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_sessions_id', 'user_sessions', ['id'], unique=False)
    op.create_index('ix_user_sessions_user_id', 'user_sessions', ['user_id'], unique=False)
    op.create_index('ix_user_sessions_session_id', 'user_sessions', ['session_id'], unique=True)
    op.create_index('ix_user_sessions_device_fingerprint', 'user_sessions', ['device_fingerprint'], unique=False)
    op.create_index('ix_user_sessions_ip_address', 'user_sessions', ['ip_address'], unique=False)
    op.create_index('ix_user_sessions_login_at', 'user_sessions', ['login_at'], unique=False)
    op.create_index('ix_user_sessions_last_activity_at', 'user_sessions', ['last_activity_at'], unique=False)
    op.create_index('ix_user_sessions_expires_at', 'user_sessions', ['expires_at'], unique=False)
    op.create_index('ix_user_sessions_is_active', 'user_sessions', ['is_active'], unique=False)
    op.create_index('ix_user_sessions_user_id_active', 'user_sessions', ['user_id', 'is_active'], unique=False)
    op.create_index('ix_user_sessions_last_activity_active', 'user_sessions', ['last_activity_at', 'is_active'], unique=False)
    op.create_index('ix_user_sessions_expires_at_active', 'user_sessions', ['expires_at', 'is_active'], unique=False)
    
    # Create security_events table
    op.create_table('security_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('metadata', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_security_events_id', 'security_events', ['id'], unique=False)
    op.create_index('ix_security_events_user_id', 'security_events', ['user_id'], unique=False)
    op.create_index('ix_security_events_event_type', 'security_events', ['event_type'], unique=False)
    op.create_index('ix_security_events_severity', 'security_events', ['severity'], unique=False)
    op.create_index('ix_security_events_ip_address', 'security_events', ['ip_address'], unique=False)
    op.create_index('ix_security_events_created_at', 'security_events', ['created_at'], unique=False)
    op.create_index('ix_security_events_type_created_at', 'security_events', ['event_type', 'created_at'], unique=False)
    op.create_index('ix_security_events_severity_created_at', 'security_events', ['severity', 'created_at'], unique=False)
    op.create_index('ix_security_events_user_id_created_at', 'security_events', ['user_id', 'created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop security_events table
    op.drop_table('security_events')
    
    # Drop user_sessions table
    op.drop_table('user_sessions')
    
    # Drop refresh_tokens table
    op.drop_table('refresh_tokens')
    
    # Drop login_attempts table
    op.drop_table('login_attempts')
    
    # Remove last_login_at column from users table
    op.drop_column('users', 'last_login_at')
