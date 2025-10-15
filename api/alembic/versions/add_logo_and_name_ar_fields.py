"""add logo and name_ar fields

Revision ID: add_logo_name_ar
Revises: 20251010_004500
Create Date: 2025-10-13

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_logo_name_ar'
down_revision = '20251010_004500'
branch_labels = None
depends_on = None


def upgrade():
    # Add name_ar and logo to tenants table
    op.add_column('tenants', sa.Column('name_ar', sa.String(), nullable=True))
    op.add_column('tenants', sa.Column('logo', sa.String(), nullable=True))
    
    # Add name_ar and logo to users table
    op.add_column('users', sa.Column('name_ar', sa.String(), nullable=True))
    op.add_column('users', sa.Column('logo', sa.String(), nullable=True))
    
    # Add name_ar and logo to management_users table
    op.add_column('management_users', sa.Column('name_ar', sa.String(), nullable=True))
    op.add_column('management_users', sa.Column('logo', sa.String(), nullable=True))


def downgrade():
    # Remove columns in reverse order
    op.drop_column('management_users', 'logo')
    op.drop_column('management_users', 'name_ar')
    
    op.drop_column('users', 'logo')
    op.drop_column('users', 'name_ar')
    
    op.drop_column('tenants', 'logo')
    op.drop_column('tenants', 'name_ar')
