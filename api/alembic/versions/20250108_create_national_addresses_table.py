"""create_national_addresses_table

Revision ID: 20250108_addresses
Revises: 20250108_deeds
Create Date: 2025-01-08 13:44:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250108_addresses'
down_revision = '20250108_deeds'
branch_labels = None
depends_on = None


def upgrade():
    # Create addresses table
    op.create_table(
        'addresses',
        sa.Column('pk_address_id', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('address2', sa.Text(), nullable=True),
        sa.Column('latitude', sa.Numeric(11, 8), nullable=True),
        sa.Column('longitude', sa.Numeric(11, 8), nullable=True),
        sa.Column('building_number', sa.String(length=50), nullable=True),
        sa.Column('street', sa.String(length=255), nullable=True),
        sa.Column('district', sa.String(length=255), nullable=True),
        sa.Column('district_id', sa.String(length=50), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('city_id', sa.String(length=50), nullable=True),
        sa.Column('post_code', sa.String(length=20), nullable=True),
        sa.Column('additional_number', sa.String(length=50), nullable=True),
        sa.Column('region_name', sa.String(length=100), nullable=True),
        sa.Column('region_id', sa.String(length=50), nullable=True),
        sa.Column('is_primary_address', sa.Boolean(), nullable=True),
        sa.Column('unit_number', sa.String(length=50), nullable=True),
        sa.Column('restriction', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('request_body', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        
        sa.PrimaryKeyConstraint('pk_address_id'),
        schema='wathq'
    )
    
    # Create indexes on frequently queried fields
    op.create_index('ix_wathq_addresses_city', 'addresses', ['city'], schema='wathq')
    op.create_index('ix_wathq_addresses_region_id', 'addresses', ['region_id'], schema='wathq')
    op.create_index('ix_wathq_addresses_post_code', 'addresses', ['post_code'], schema='wathq')
    op.create_index('ix_wathq_addresses_is_primary', 'addresses', ['is_primary_address'], schema='wathq')


def downgrade():
    # Drop indexes
    op.drop_index('ix_wathq_addresses_is_primary', table_name='addresses', schema='wathq')
    op.drop_index('ix_wathq_addresses_post_code', table_name='addresses', schema='wathq')
    op.drop_index('ix_wathq_addresses_region_id', table_name='addresses', schema='wathq')
    op.drop_index('ix_wathq_addresses_city', table_name='addresses', schema='wathq')
    
    # Drop table
    op.drop_table('addresses', schema='wathq')
