"""add wathq offline data table

Revision ID: add_wathq_offline_data
Revises: add_wathq_api_key_to_tenant_services
Create Date: 2024-01-01 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_wathq_offline_data'
down_revision = 'add_wathq_api_key_to_tenant_services'
branch_labels = None
depends_on = None


def upgrade():
    # Create wathq_offline_data table
    op.create_table('wathq_offline_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('service_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('fetched_by', sa.Integer(), nullable=True),
        sa.Column('management_user_id', sa.Integer(), nullable=True),
        sa.Column('full_external_url', sa.Text(), nullable=False),
        sa.Column('response_body', sa.JSON(), nullable=False),
        sa.Column('fetched_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['fetched_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['management_user_id'], ['management_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index(op.f('ix_wathq_offline_data_id'), 'wathq_offline_data',
                    ['id'], unique=False)
    op.create_index(op.f('ix_wathq_offline_data_service_id'),
                    'wathq_offline_data', ['service_id'], unique=False)
    op.create_index(op.f('ix_wathq_offline_data_tenant_id'),
                    'wathq_offline_data', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_wathq_offline_data_fetched_by'),
                    'wathq_offline_data', ['fetched_by'], unique=False)
    op.create_index(op.f('ix_wathq_offline_data_management_user_id'),
                    'wathq_offline_data', ['management_user_id'], unique=False)
    op.create_index(op.f('ix_wathq_offline_data_fetched_at'),
                    'wathq_offline_data', ['fetched_at'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_wathq_offline_data_fetched_at'),
                  table_name='wathq_offline_data')
    op.drop_index(op.f('ix_wathq_offline_data_management_user_id'),
                  table_name='wathq_offline_data')
    op.drop_index(op.f('ix_wathq_offline_data_fetched_by'),
                  table_name='wathq_offline_data')
    op.drop_index(op.f('ix_wathq_offline_data_tenant_id'),
                  table_name='wathq_offline_data')
    op.drop_index(op.f('ix_wathq_offline_data_service_id'),
                  table_name='wathq_offline_data')
    op.drop_index(op.f('ix_wathq_offline_data_id'),
                  table_name='wathq_offline_data')

    # Drop table
    op.drop_table('wathq_offline_data')