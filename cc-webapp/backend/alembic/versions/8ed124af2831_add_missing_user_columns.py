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
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
