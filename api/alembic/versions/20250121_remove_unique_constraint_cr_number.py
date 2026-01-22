"""remove_unique_constraint_from_cr_number_add_fetched_at

Revision ID: 20250121_cr_history
Revises: df7e711263ba
Create Date: 2026-01-21 16:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250121_cr_history'
down_revision = 'df7e711263ba'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the unique constraint on cr_number to allow historical records (if it exists)
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Check if constraint exists before dropping
    constraints = inspector.get_unique_constraints('commercial_registrations', schema='wathq')
    constraint_names = [c['name'] for c in constraints]
    
    if 'commercial_registrations_cr_number_key' in constraint_names:
        op.drop_constraint('commercial_registrations_cr_number_key', 'commercial_registrations', schema='wathq', type_='unique')
    
    # Add fetched_at column to track when data was fetched from Wathq
    op.add_column('commercial_registrations',
                  sa.Column('fetched_at', sa.DateTime(timezone=True), nullable=True),
                  schema='wathq')
    
    # Create a composite index on (cr_number, fetched_at) for efficient queries
    op.create_index('ix_commercial_registrations_cr_number_fetched_at',
                    'commercial_registrations',
                    ['cr_number', 'fetched_at'],
                    schema='wathq')


def downgrade() -> None:
    # Drop the composite index
    op.drop_index('ix_commercial_registrations_cr_number_fetched_at',
                  table_name='commercial_registrations',
                  schema='wathq')
    
    # Drop the fetched_at column
    op.drop_column('commercial_registrations', 'fetched_at', schema='wathq')
    
    # Restore the unique constraint on cr_number
    op.create_unique_constraint('commercial_registrations_cr_number_key',
                                'commercial_registrations',
                                ['cr_number'],
                                schema='wathq')
