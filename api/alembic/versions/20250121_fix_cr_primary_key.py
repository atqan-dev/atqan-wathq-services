"""fix_commercial_registrations_primary_key

Revision ID: 20250121_fix_pk
Revises: f4b678f7d405
Create Date: 2026-01-21 16:25:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250121_fix_pk'
down_revision = 'f4b678f7d405'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the existing primary key constraint on cr_number
    op.drop_constraint('commercial_registrations_pkey', 'commercial_registrations', schema='wathq', type_='primary')
    
    # Add primary key constraint on id column
    op.create_primary_key('commercial_registrations_pkey', 'commercial_registrations', ['id'], schema='wathq')
    
    # Ensure id column is set to autoincrement if not already
    op.execute('ALTER TABLE wathq.commercial_registrations ALTER COLUMN id SET DEFAULT nextval(\'wathq.commercial_registrations_id_seq\'::regclass);')


def downgrade() -> None:
    # Drop the primary key on id
    op.drop_constraint('commercial_registrations_pkey', 'commercial_registrations', schema='wathq', type_='primary')
    
    # Restore primary key on cr_number
    op.create_primary_key('commercial_registrations_pkey', 'commercial_registrations', ['cr_number'], schema='wathq')
    
    # Remove default from id
    op.execute('ALTER TABLE wathq.commercial_registrations ALTER COLUMN id DROP DEFAULT;')
