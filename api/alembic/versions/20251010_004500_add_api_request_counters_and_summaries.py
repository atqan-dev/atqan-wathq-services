"""add api request counters and summaries tables

Revision ID: 20251010_004500
Revises: da7d3d5d85fe
Create Date: 2025-10-10 00:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '20251010_004500'
down_revision = '934073d84685'
branch_labels = None
depends_on = None


def upgrade():
    # Create api_request_counters table
    op.create_table('api_request_counters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('request_type', sa.String(), nullable=False),
        sa.Column('endpoint', sa.String(), nullable=False),
        sa.Column('method', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('management_user_id', sa.Integer(), nullable=True),
        sa.Column('service_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('service_slug', sa.String(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('request_params', sa.JSON(), nullable=True),
        sa.Column('request_size', sa.Integer(), nullable=True),
        sa.Column('response_status', sa.Integer(), nullable=False),
        sa.Column('response_time_ms', sa.Integer(), nullable=False),
        sa.Column('response_size', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('is_successful', sa.Boolean(), nullable=True),
        sa.Column('is_cached', sa.Boolean(), nullable=True),
        sa.Column('is_rate_limited', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['management_user_id'], ['management_users.id'], ),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create api_request_summaries table
    op.create_table('api_request_summaries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_type', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('endpoint', sa.String(), nullable=True),
        sa.Column('service_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('total_requests', sa.Integer(), nullable=True),
        sa.Column('successful_requests', sa.Integer(), nullable=True),
        sa.Column('failed_requests', sa.Integer(), nullable=True),
        sa.Column('cached_requests', sa.Integer(), nullable=True),
        sa.Column('external_requests', sa.Integer(), nullable=True),
        sa.Column('internal_requests', sa.Integer(), nullable=True),
        sa.Column('avg_response_time_ms', sa.Numeric(10, 2), nullable=True),
        sa.Column('max_response_time_ms', sa.Integer(), nullable=True),
        sa.Column('min_response_time_ms', sa.Integer(), nullable=True),
        sa.Column('total_response_size_bytes', sa.Integer(), nullable=True),
        sa.Column('rate_limited_requests', sa.Integer(), nullable=True),
        sa.Column('unique_users', sa.Integer(), nullable=True),
        sa.Column('unique_ips', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for api_request_counters
    op.create_index(op.f('ix_api_request_counters_id'), 'api_request_counters', ['id'], unique=False)
    op.create_index(op.f('ix_api_request_counters_request_type'), 'api_request_counters', ['request_type'], unique=False)
    op.create_index(op.f('ix_api_request_counters_endpoint'), 'api_request_counters', ['endpoint'], unique=False)
    op.create_index(op.f('ix_api_request_counters_user_id'), 'api_request_counters', ['user_id'], unique=False)
    op.create_index(op.f('ix_api_request_counters_tenant_id'), 'api_request_counters', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_api_request_counters_management_user_id'), 'api_request_counters', ['management_user_id'], unique=False)
    op.create_index(op.f('ix_api_request_counters_service_id'), 'api_request_counters', ['service_id'], unique=False)
    op.create_index(op.f('ix_api_request_counters_service_slug'), 'api_request_counters', ['service_slug'], unique=False)
    op.create_index(op.f('ix_api_request_counters_created_at'), 'api_request_counters', ['created_at'], unique=False)

    # Create indexes for api_request_summaries
    op.create_index(op.f('ix_api_request_summaries_id'), 'api_request_summaries', ['id'], unique=False)
    op.create_index(op.f('ix_api_request_summaries_period_start'), 'api_request_summaries', ['period_start'], unique=False)
    op.create_index(op.f('ix_api_request_summaries_period_end'), 'api_request_summaries', ['period_end'], unique=False)
    op.create_index(op.f('ix_api_request_summaries_tenant_id'), 'api_request_summaries', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_api_request_summaries_user_id'), 'api_request_summaries', ['user_id'], unique=False)
    op.create_index(op.f('ix_api_request_summaries_endpoint'), 'api_request_summaries', ['endpoint'], unique=False)
    op.create_index(op.f('ix_api_request_summaries_service_id'), 'api_request_summaries', ['service_id'], unique=False)


def downgrade():
    # Drop indexes for api_request_summaries
    op.drop_index(op.f('ix_api_request_summaries_service_id'), table_name='api_request_summaries')
    op.drop_index(op.f('ix_api_request_summaries_endpoint'), table_name='api_request_summaries')
    op.drop_index(op.f('ix_api_request_summaries_user_id'), table_name='api_request_summaries')
    op.drop_index(op.f('ix_api_request_summaries_tenant_id'), table_name='api_request_summaries')
    op.drop_index(op.f('ix_api_request_summaries_period_end'), table_name='api_request_summaries')
    op.drop_index(op.f('ix_api_request_summaries_period_start'), table_name='api_request_summaries')
    op.drop_index(op.f('ix_api_request_summaries_id'), table_name='api_request_summaries')

    # Drop indexes for api_request_counters
    op.drop_index(op.f('ix_api_request_counters_created_at'), table_name='api_request_counters')
    op.drop_index(op.f('ix_api_request_counters_service_slug'), table_name='api_request_counters')
    op.drop_index(op.f('ix_api_request_counters_service_id'), table_name='api_request_counters')
    op.drop_index(op.f('ix_api_request_counters_management_user_id'), table_name='api_request_counters')
    op.drop_index(op.f('ix_api_request_counters_tenant_id'), table_name='api_request_counters')
    op.drop_index(op.f('ix_api_request_counters_user_id'), table_name='api_request_counters')
    op.drop_index(op.f('ix_api_request_counters_endpoint'), table_name='api_request_counters')
    op.drop_index(op.f('ix_api_request_counters_request_type'), table_name='api_request_counters')
    op.drop_index(op.f('ix_api_request_counters_id'), table_name='api_request_counters')

    # Drop tables
    op.drop_table('api_request_summaries')
    op.drop_table('api_request_counters')
