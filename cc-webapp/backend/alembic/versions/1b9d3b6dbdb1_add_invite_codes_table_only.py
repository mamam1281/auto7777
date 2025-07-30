"""Add invite_codes table only

Revision ID: 1b9d3b6dbdb1
Revises: 665e758acfd0
Create Date: 2025-07-30 03:54:47.598629

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b9d3b6dbdb1'
down_revision: Union[str, None] = '665e758acfd0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add invite_codes table."""
    # Create invite_codes table
    op.create_table(
        'invite_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=6), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('max_uses', sa.Integer(), nullable=True, default=1),
        sa.Column('use_count', sa.Integer(), nullable=False, default=0),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.Column('used_by_user_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_invite_codes_id'), 'invite_codes', ['id'], unique=False)
    op.create_index(op.f('ix_invite_codes_code'), 'invite_codes', ['code'], unique=True)
    
    # Add foreign key constraints
    op.create_foreign_key(
        'fk_invite_codes_created_by_user_id',
        'invite_codes', 'users',
        ['created_by_user_id'], ['id']
    )
    op.create_foreign_key(
        'fk_invite_codes_used_by_user_id',
        'invite_codes', 'users',
        ['used_by_user_id'], ['id']
    )


def downgrade() -> None:
    """Remove invite_codes table."""
    op.drop_table('invite_codes')
