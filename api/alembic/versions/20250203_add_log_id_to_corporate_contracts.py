"""Add log_id and fetched_at columns to corporate_contracts table

Revision ID: 20250203_add_log_id_cc
Revises: 030f3032b865
Create Date: 2025-02-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250203_add_log_id_cc'
down_revision = '030f3032b865'
branch_labels = None
depends_on = None


def upgrade():
    # Add log_id column with foreign key to wathq_call_logs
    op.add_column(
        'corporate_contracts',
        sa.Column('log_id', postgresql.UUID(as_uuid=True), nullable=True),
        schema='wathq'
    )
    
    # Add fetched_at column
    op.add_column(
        'corporate_contracts',
        sa.Column('fetched_at', sa.DateTime(timezone=True), nullable=True),
        schema='wathq'
    )
    
    # Create index on log_id for faster lookups
    op.create_index(
        'ix_wathq_corporate_contracts_log_id',
        'corporate_contracts',
        ['log_id'],
        schema='wathq'
    )
    
    # Add foreign key constraint to wathq_call_logs
    op.create_foreign_key(
        'fk_corporate_contracts_log_id',
        'corporate_contracts',
        'wathq_call_logs',
        ['log_id'],
        ['id'],
        source_schema='wathq',
        referent_schema='public'
    )


def downgrade():
    # Drop foreign key constraint
    op.drop_constraint(
        'fk_corporate_contracts_log_id',
        'corporate_contracts',
        schema='wathq',
        type_='foreignkey'
    )
    
    # Drop index
    op.drop_index(
        'ix_wathq_corporate_contracts_log_id',
        table_name='corporate_contracts',
        schema='wathq'
    )
    
    # Drop columns
    op.drop_column('corporate_contracts', 'fetched_at', schema='wathq')
    op.drop_column('corporate_contracts', 'log_id', schema='wathq')
