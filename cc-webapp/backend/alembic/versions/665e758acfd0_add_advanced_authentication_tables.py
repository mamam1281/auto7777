"""Add advanced authentication tables

Revision ID: 665e758acfd0
Revises: dd73ef05465d
Create Date: 2025-07-30 12:20:59.204841

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '665e758acfd0'
down_revision: Union[str, None] = 'dd73ef05465d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. User 테이블에 로그인 관련 필드 추가
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('last_login_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('login_count', sa.Integer(), default=0, nullable=True))
        batch_op.add_column(sa.Column('failed_login_attempts', sa.Integer(), default=0, nullable=True))
        batch_op.add_column(sa.Column('account_locked_until', sa.DateTime(), nullable=True))
    
    # 2. UserSession 테이블 생성
    op.create_table('user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('jti', sa.String(255), nullable=False),
        sa.Column('token_type', sa.String(20), default='access', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=True),
        sa.Column('device_info', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('jti'),
        sa.CheckConstraint("token_type IN ('access', 'refresh')", name='chk_token_type')
    )
    
    # 3. LoginAttempt 테이블 생성
    op.create_table('login_attempts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('attempted_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('failure_reason', sa.String(100), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 4. BlacklistedToken 테이블 생성
    op.create_table('blacklisted_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('jti', sa.String(255), nullable=False),
        sa.Column('token_type', sa.String(20), default='access', nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('blacklisted_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('reason', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('jti'),
        sa.CheckConstraint("token_type IN ('access', 'refresh')", name='chk_blacklist_token_type')
    )
    
    # 인덱스 생성
    op.create_index('idx_user_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('idx_user_sessions_jti', 'user_sessions', ['jti'])
    op.create_index('idx_user_sessions_expires_at', 'user_sessions', ['expires_at'])
    op.create_index('idx_user_sessions_is_active', 'user_sessions', ['is_active'])
    
    op.create_index('idx_login_attempts_user_id', 'login_attempts', ['user_id'])
    op.create_index('idx_login_attempts_ip_address', 'login_attempts', ['ip_address'])
    op.create_index('idx_login_attempts_attempted_at', 'login_attempts', ['attempted_at'])
    
    op.create_index('idx_blacklisted_tokens_jti', 'blacklisted_tokens', ['jti'])
    op.create_index('idx_blacklisted_tokens_user_id', 'blacklisted_tokens', ['user_id'])
    op.create_index('idx_blacklisted_tokens_expires_at', 'blacklisted_tokens', ['expires_at'])


def downgrade() -> None:
    """Downgrade schema."""
    # 인덱스 삭제
    op.drop_index('idx_blacklisted_tokens_expires_at')
    op.drop_index('idx_blacklisted_tokens_user_id')
    op.drop_index('idx_blacklisted_tokens_jti')
    
    op.drop_index('idx_login_attempts_attempted_at')
    op.drop_index('idx_login_attempts_ip_address')
    op.drop_index('idx_login_attempts_user_id')
    
    op.drop_index('idx_user_sessions_is_active')
    op.drop_index('idx_user_sessions_expires_at')
    op.drop_index('idx_user_sessions_jti')
    op.drop_index('idx_user_sessions_user_id')
    
    # 테이블 삭제
    op.drop_table('blacklisted_tokens')
    op.drop_table('login_attempts')
    op.drop_table('user_sessions')
    
    # User 테이블 컬럼 삭제
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('account_locked_until')
        batch_op.drop_column('failed_login_attempts')
        batch_op.drop_column('login_count')
        batch_op.drop_column('last_login_at')
