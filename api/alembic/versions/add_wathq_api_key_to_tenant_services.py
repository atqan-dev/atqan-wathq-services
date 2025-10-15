"""add wathq_api_key to tenant_services

Revision ID: add_wathq_api_key_to_tenant_services
Revises: add_wathq_call_logs
Create Date: 2024-01-01 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_wathq_api_key_to_tenant_services'
down_revision = 'add_wathq_call_logs'
branch_labels = None
depends_on = None


def upgrade():
    # Add wathq_api_key column to tenant_services table
    op.add_column('tenant_services', sa.Column('wathq_api_key', sa.String(), nullable=True))


def downgrade():
    # Remove wathq_api_key column from tenant_services table
    op.drop_column('tenant_services', 'wathq_api_key')