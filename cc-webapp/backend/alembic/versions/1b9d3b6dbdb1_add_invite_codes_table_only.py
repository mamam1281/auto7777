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
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
