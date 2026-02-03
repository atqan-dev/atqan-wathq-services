"""Add log_id and fetched_at columns to deeds table

Revision ID: 20250203_add_log_id_deeds
Revises: 20250203_add_log_id_poa
Create Date: 2025-02-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250203_add_log_id_deeds'
down_revision = '20250203_add_log_id_poa'
branch_labels = None
depends_on = None


def upgrade():
    # Add log_id column with foreign key to wathq_call_logs
    op.add_column(
        'deeds',
        sa.Column('log_id', postgresql.UUID(as_uuid=True), nullable=True),
        schema='wathq'
    )
    
    # Add fetched_at column
    op.add_column(
        'deeds',
        sa.Column('fetched_at', sa.DateTime(timezone=True), nullable=True),
        schema='wathq'
    )
    
    # Create index on log_id for faster lookups
    op.create_index(
        'ix_wathq_deeds_log_id',
        'deeds',
        ['log_id'],
        schema='wathq'
    )
    
    # Add foreign key constraint to wathq_call_logs
    op.create_foreign_key(
        'fk_deeds_log_id',
        'deeds',
        'wathq_call_logs',
        ['log_id'],
        ['id'],
        source_schema='wathq',
        referent_schema='public'
    )


def downgrade():
    # Drop foreign key constraint
    op.drop_constraint(
        'fk_deeds_log_id',
        'deeds',
        schema='wathq',
        type_='foreignkey'
    )
    
    # Drop index
    op.drop_index(
        'ix_wathq_deeds_log_id',
        table_name='deeds',
        schema='wathq'
    )
    
    # Drop columns
    op.drop_column('deeds', 'fetched_at', schema='wathq')
    op.drop_column('deeds', 'log_id', schema='wathq')
