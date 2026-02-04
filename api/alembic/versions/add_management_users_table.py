"""add management users table

Revision ID: add_management_users
Revises: enhance_wathq_services
Create Date: 2024-01-01 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_management_users'
down_revision = 'enhance_wathq_services'
branch_labels = None
depends_on = None


def upgrade():
    # Create management_users table
    op.create_table('management_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('name_ar', sa.String(), nullable=True),
        sa.Column('logo', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_super_admin', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('totp_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('totp_secret', sa.Text(), nullable=True),
        sa.Column('totp_backup_codes', sa.JSON(), nullable=True),
        sa.Column('totp_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('totp_last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('totp_failed_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('totp_locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_management_users_id'), 'management_users', ['id'], unique=False)
    op.create_index(op.f('ix_management_users_email'), 'management_users', ['email'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_management_users_email'), table_name='management_users')
    op.drop_index(op.f('ix_management_users_id'), table_name='management_users')
    op.drop_table('management_users')
