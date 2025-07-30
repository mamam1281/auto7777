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
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
