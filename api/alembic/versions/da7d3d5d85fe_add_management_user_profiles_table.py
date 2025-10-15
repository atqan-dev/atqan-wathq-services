"""add_management_user_profiles_table

Revision ID: da7d3d5d85fe
Revises: 0e1bee57ba30
Create Date: 2025-10-06 10:18:53.091683

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'da7d3d5d85fe'
down_revision = '0e1bee57ba30'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create management_user_profiles table
    op.create_table('management_user_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('management_user_id', sa.Integer(), nullable=False),
        sa.Column('fullname', sa.String(), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('mobile', sa.String(), nullable=True),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('company_name', sa.String(), nullable=True),
        sa.Column('commercial_registration_number', sa.String(), nullable=True),
        sa.Column('entity_number', sa.String(), nullable=True),
        sa.Column('full_info', sa.JSON(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('whatsapp_number', sa.String(), nullable=True),
        sa.Column('avatar_image_url', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['management_user_id'], ['management_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_management_user_profiles_id'), 'management_user_profiles', ['id'], unique=False)


def downgrade() -> None:
    # Drop management_user_profiles table
    op.drop_index(op.f('ix_management_user_profiles_id'), table_name='management_user_profiles')
    op.drop_table('management_user_profiles')
