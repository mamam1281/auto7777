"""add admin rank to user model

Revision ID: f9799d6b44b3
Revises: e6a362273e71
Create Date: 2025-07-29 10:10:26.646048

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9799d6b44b3'
down_revision: Union[str, None] = 'e6a362273e71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the new Enum type first
    user_rank_enum = sa.Enum('STANDARD', 'VIP', 'PREMIUM', 'ADMIN', name='userrankenum')
    user_rank_enum.create(op.get_bind(), checkfirst=True)
    # Now alter the column to use the new Enum type
    op.execute("ALTER TABLE users ALTER COLUMN rank TYPE userrankenum USING rank::userrankenum")


def downgrade() -> None:
    """Downgrade schema."""
    # Revert the column to VARCHAR first
    user_rank_enum = sa.Enum('STANDARD', 'VIP', 'PREMIUM', 'ADMIN', name='userrankenum')
    op.alter_column('users', 'rank',
        existing_type=user_rank_enum,
        type_=sa.VARCHAR(length=20),
        existing_nullable=False)
    # Then drop the Enum type
    user_rank_enum.drop(op.get_bind(), checkfirst=True)
