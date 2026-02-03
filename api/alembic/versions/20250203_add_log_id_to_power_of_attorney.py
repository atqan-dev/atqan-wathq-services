"""Add log_id and fetched_at columns to power_of_attorney table

Revision ID: 20250203_add_log_id_poa
Revises: 37526dbec8d0
Create Date: 2025-02-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250203_add_log_id_poa'
down_revision = '37526dbec8d0'
branch_labels = None
depends_on = None


def upgrade():
    # Add log_id column with foreign key to wathq_call_logs
    op.add_column(
        'power_of_attorney',
        sa.Column('log_id', postgresql.UUID(as_uuid=True), nullable=True),
        schema='wathq'
    )
    
    # Add fetched_at column
    op.add_column(
        'power_of_attorney',
        sa.Column('fetched_at', sa.DateTime(timezone=True), nullable=True),
        schema='wathq'
    )
    
    # Create index on log_id for faster lookups
    op.create_index(
        'ix_wathq_power_of_attorney_log_id',
        'power_of_attorney',
        ['log_id'],
        schema='wathq'
    )
    
    # Add foreign key constraint to wathq_call_logs
    op.create_foreign_key(
        'fk_power_of_attorney_log_id',
        'power_of_attorney',
        'wathq_call_logs',
        ['log_id'],
        ['id'],
        source_schema='wathq',
        referent_schema='public'
    )
    
    # Drop unique constraint on code to allow repeated data
    op.drop_constraint('power_of_attorney_code_key', 'power_of_attorney', schema='wathq', type_='unique')


def downgrade():
    # Re-add unique constraint on code
    op.create_unique_constraint('power_of_attorney_code_key', 'power_of_attorney', ['code'], schema='wathq')
    
    # Drop foreign key constraint
    op.drop_constraint(
        'fk_power_of_attorney_log_id',
        'power_of_attorney',
        schema='wathq',
        type_='foreignkey'
    )
    
    # Drop index
    op.drop_index(
        'ix_wathq_power_of_attorney_log_id',
        table_name='power_of_attorney',
        schema='wathq'
    )
    
    # Drop columns
    op.drop_column('power_of_attorney', 'fetched_at', schema='wathq')
    op.drop_column('power_of_attorney', 'log_id', schema='wathq')
