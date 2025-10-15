"""add wathq call logs table

Revision ID: add_wathq_call_logs
Revises: enhance_wathq_services
Create Date: 2024-01-01 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_wathq_call_logs'
down_revision = 'enhance_wathq_services'
branch_labels = None
depends_on = None


def upgrade():
    # Create wathq_call_logs table
    op.create_table('wathq_call_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('service_slug', sa.String(), nullable=False),
        sa.Column('endpoint', sa.String(), nullable=False),
        sa.Column('method', sa.String(), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('request_data', sa.JSON(), nullable=True),
        sa.Column('response_body', sa.JSON(), nullable=False),
        sa.Column('fetched_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index(op.f('ix_wathq_call_logs_id'), 'wathq_call_logs', ['id'], unique=False)
    op.create_index(op.f('ix_wathq_call_logs_tenant_id'), 'wathq_call_logs', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_wathq_call_logs_user_id'), 'wathq_call_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_wathq_call_logs_service_slug'), 'wathq_call_logs', ['service_slug'], unique=False)
    op.create_index(op.f('ix_wathq_call_logs_fetched_at'), 'wathq_call_logs', ['fetched_at'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_wathq_call_logs_fetched_at'), table_name='wathq_call_logs')
    op.drop_index(op.f('ix_wathq_call_logs_service_slug'), table_name='wathq_call_logs')
    op.drop_index(op.f('ix_wathq_call_logs_user_id'), table_name='wathq_call_logs')
    op.drop_index(op.f('ix_wathq_call_logs_tenant_id'), table_name='wathq_call_logs')
    op.drop_index(op.f('ix_wathq_call_logs_id'), table_name='wathq_call_logs')
    
    # Drop table
    op.drop_table('wathq_call_logs')