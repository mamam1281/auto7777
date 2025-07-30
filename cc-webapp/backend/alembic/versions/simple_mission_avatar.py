"""Add mission system and profile image models

Revision ID: simple_001
Revises: 8ed124af2831
Create Date: 2025-07-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'simple_001'
down_revision = '8ed124af2831'
branch_labels = None
depends_on = None


def upgrade():
    # Create missions table
    op.create_table('missions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('mission_type', sa.String(length=50), nullable=False),
        sa.Column('target_value', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('reward_type', sa.String(length=50), nullable=False, server_default='cyber_token'),
        sa.Column('reward_amount', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('reward_description', sa.String(length=200), nullable=True),
        sa.Column('is_daily', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_weekly', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_missions_id'), 'missions', ['id'], unique=False)
    op.create_index(op.f('ix_missions_mission_type'), 'missions', ['mission_type'], unique=False)
    op.create_index(op.f('ix_missions_is_active'), 'missions', ['is_active'], unique=False)

    # Create user_mission_progress table
    op.create_table('user_mission_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('mission_id', sa.Integer(), nullable=False),
        sa.Column('current_progress', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_claimed', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('claimed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['mission_id'], ['missions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_mission_progress_id'), 'user_mission_progress', ['id'], unique=False)
    op.create_index(op.f('ix_user_mission_progress_user_id'), 'user_mission_progress', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_mission_progress_mission_id'), 'user_mission_progress', ['mission_id'], unique=False)

    # Create avatars table
    op.create_table('avatars',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=False),
        sa.Column('thumbnail_url', sa.String(length=500), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False, server_default='basic'),
        sa.Column('unlock_condition', sa.Text(), nullable=True),
        sa.Column('required_rank', sa.String(length=20), nullable=False, server_default='STANDARD'),
        sa.Column('is_premium', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_avatars_id'), 'avatars', ['id'], unique=False)
    op.create_index(op.f('ix_avatars_category'), 'avatars', ['category'], unique=False)
    op.create_index(op.f('ix_avatars_required_rank'), 'avatars', ['required_rank'], unique=False)

    # Create user_profile_images table
    op.create_table('user_profile_images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('avatar_id', sa.Integer(), nullable=True),
        sa.Column('custom_image_url', sa.String(length=500), nullable=True),
        sa.Column('image_type', sa.String(length=20), nullable=False, server_default='avatar'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['avatar_id'], ['avatars.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_profile_images_id'), 'user_profile_images', ['id'], unique=False)
    op.create_index(op.f('ix_user_profile_images_user_id'), 'user_profile_images', ['user_id'], unique=True)

    # Note: Skipping users table columns as they already exist in this environment
    # last_login_at, login_count, failed_login_attempts are already present


def downgrade():
    # Drop tables in reverse order
    op.drop_table('user_profile_images')
    op.drop_table('avatars') 
    op.drop_table('user_mission_progress')
    op.drop_table('missions')
    
    # Note: Not removing users table columns as they might be used elsewhere
