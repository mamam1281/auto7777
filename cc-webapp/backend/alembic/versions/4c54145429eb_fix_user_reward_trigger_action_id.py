"""fix_user_reward_trigger_action_id

Revision ID: 4c54145429eb
Revises: 7cc34a83cfee
Create Date: 2025-06-08 04:48:46.643135

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4c54145429eb"
down_revision: Union[str, None] = "7cc34a83cfee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add trigger_action_id column if missing."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c["name"] for c in inspector.get_columns("user_rewards")]
    if "trigger_action_id" not in columns:
        with op.batch_alter_table("user_rewards") as batch_op:
            batch_op.add_column(sa.Column("trigger_action_id", sa.Integer(), nullable=True))
            batch_op.create_foreign_key(
                "fk_user_rewards_trigger_action_id_user_actions",
                "user_actions",
                ["trigger_action_id"],
                ["id"],
            )


def downgrade() -> None:
    """Remove trigger_action_id column."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c["name"] for c in inspector.get_columns("user_rewards")]
    if "trigger_action_id" in columns:
        with op.batch_alter_table("user_rewards") as batch_op:
            batch_op.drop_constraint(
                "fk_user_rewards_trigger_action_id_user_actions",
                type_="foreignkey",
            )
            batch_op.drop_column("trigger_action_id")
