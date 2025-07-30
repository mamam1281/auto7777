"""Add missing user columns

Revision ID: 8ed124af2831
Revises: 1b9d3b6dbdb1
Create Date: 2025-07-30 03:57:03.000262

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ed124af2831'
down_revision: Union[str, None] = '1b9d3b6dbdb1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing user columns."""
    # Add cyber_token_balance column
    op.add_column('users', sa.Column('cyber_token_balance', sa.Integer(), nullable=True, default=200))
    
    # Add password_changed_at column
    op.add_column('users', sa.Column('password_changed_at', sa.DateTime(), nullable=True))
    
    # Update existing users to have default cyber token balance
    op.execute("UPDATE users SET cyber_token_balance = 200 WHERE cyber_token_balance IS NULL")


def downgrade() -> None:
    """Remove added user columns."""
    op.drop_column('users', 'password_changed_at')
    op.drop_column('users', 'cyber_token_balance')
