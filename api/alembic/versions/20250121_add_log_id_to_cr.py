"""add_log_id_to_commercial_registrations

Revision ID: 20250121_add_log_id
Revises: 20250121_fix_pk
Create Date: 2026-01-21 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '20250121_add_log_id'
down_revision = '20250121_fix_pk'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add log_id column to link CR records to wathq_call_logs
    op.add_column('commercial_registrations',
                  sa.Column('log_id', UUID(as_uuid=True), nullable=True),
                  schema='wathq')
    
    # Create foreign key constraint (wathq_call_logs is in public schema)
    op.create_foreign_key('fk_commercial_registrations_log_id',
                          'commercial_registrations',
                          'wathq_call_logs',
                          ['log_id'],
                          ['id'],
                          source_schema='wathq',
                          referent_schema='public',
                          ondelete='SET NULL')
    
    # Create index on log_id for efficient lookups
    op.create_index('ix_commercial_registrations_log_id',
                    'commercial_registrations',
                    ['log_id'],
                    schema='wathq')
    
    # Create unique constraint on log_id to ensure one CR record per call log
    op.create_unique_constraint('uq_commercial_registrations_log_id',
                                'commercial_registrations',
                                ['log_id'],
                                schema='wathq')


def downgrade() -> None:
    # Drop unique constraint
    op.drop_constraint('uq_commercial_registrations_log_id',
                       'commercial_registrations',
                       schema='wathq',
                       type_='unique')
    
    # Drop index
    op.drop_index('ix_commercial_registrations_log_id',
                  table_name='commercial_registrations',
                  schema='wathq')
    
    # Drop foreign key
    op.drop_constraint('fk_commercial_registrations_log_id',
                       'commercial_registrations',
                       schema='wathq',
                       type_='foreignkey')
    
    # Drop column
    op.drop_column('commercial_registrations', 'log_id', schema='wathq')
