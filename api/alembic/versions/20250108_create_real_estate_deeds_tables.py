"""create_real_estate_deeds_tables

Revision ID: 20250108_deeds
Revises: 20250108_poa
Create Date: 2025-01-08 13:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250108_deeds'
down_revision = '20250108_poa'
branch_labels = None
depends_on = None


def upgrade():
    # Create deeds master table
    op.create_table(
        'deeds',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('deed_number', sa.String(length=50), nullable=True),
        sa.Column('deed_serial', sa.String(length=50), nullable=True),
        sa.Column('deed_date', sa.String(length=20), nullable=True),
        sa.Column('deed_text', sa.Text(), nullable=True),
        sa.Column('deed_source', sa.String(length=255), nullable=True),
        sa.Column('deed_city', sa.String(length=100), nullable=True),
        sa.Column('deed_status', sa.String(length=50), nullable=True),
        sa.Column('deed_area', sa.Numeric(10, 2), nullable=True),
        sa.Column('deed_area_text', sa.Text(), nullable=True),
        sa.Column('is_real_estate_constrained', sa.Boolean(), nullable=True),
        sa.Column('is_real_estate_halted', sa.Boolean(), nullable=True),
        sa.Column('is_real_estate_mortgaged', sa.Boolean(), nullable=True),
        sa.Column('is_real_estate_testamented', sa.Boolean(), nullable=True),
        
        # North limit
        sa.Column('limit_north_name', sa.String(length=100), nullable=True),
        sa.Column('limit_north_description', sa.Text(), nullable=True),
        sa.Column('limit_north_length', sa.Numeric(10, 2), nullable=True),
        sa.Column('limit_north_length_char', sa.Text(), nullable=True),
        
        # South limit
        sa.Column('limit_south_name', sa.String(length=100), nullable=True),
        sa.Column('limit_south_description', sa.Text(), nullable=True),
        sa.Column('limit_south_length', sa.Numeric(10, 2), nullable=True),
        sa.Column('limit_south_length_char', sa.Text(), nullable=True),
        
        # East limit
        sa.Column('limit_east_name', sa.String(length=100), nullable=True),
        sa.Column('limit_east_description', sa.Text(), nullable=True),
        sa.Column('limit_east_length', sa.Numeric(10, 2), nullable=True),
        sa.Column('limit_east_length_char', sa.Text(), nullable=True),
        
        # West limit
        sa.Column('limit_west_name', sa.String(length=100), nullable=True),
        sa.Column('limit_west_description', sa.Text(), nullable=True),
        sa.Column('limit_west_length', sa.Numeric(10, 2), nullable=True),
        sa.Column('limit_west_length_char', sa.Text(), nullable=True),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('request_body', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        schema='wathq'
    )
    
    # Create indexes on frequently queried fields
    op.create_index('ix_wathq_deeds_deed_number', 'deeds', ['deed_number'], schema='wathq')
    op.create_index('ix_wathq_deeds_deed_serial', 'deeds', ['deed_serial'], schema='wathq')

    # Create deed_owners table
    op.create_table(
        'deed_owners',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('deed_id', sa.Integer(), nullable=False),
        sa.Column('owner_name', sa.String(length=255), nullable=True),
        sa.Column('birth_date', sa.String(length=20), nullable=True),
        sa.Column('id_number', sa.String(length=50), nullable=True),
        sa.Column('id_type', sa.String(length=10), nullable=True),
        sa.Column('id_type_text', sa.String(length=50), nullable=True),
        sa.Column('owner_type', sa.String(length=50), nullable=True),
        sa.Column('nationality', sa.String(length=100), nullable=True),
        sa.Column('owning_area', sa.Numeric(10, 3), nullable=True),
        sa.Column('owning_amount', sa.Numeric(10, 2), nullable=True),
        sa.Column('constrained', sa.Integer(), nullable=True),
        sa.Column('halt', sa.Integer(), nullable=True),
        sa.Column('pawned', sa.Integer(), nullable=True),
        sa.Column('testament', sa.Integer(), nullable=True),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['deed_id'], ['wathq.deeds.id'], ondelete='CASCADE'),
        schema='wathq'
    )
    
    # Create index on deed_id for faster joins
    op.create_index('ix_wathq_deed_owners_deed_id', 'deed_owners', ['deed_id'], schema='wathq')

    # Create deed_real_estates table
    op.create_table(
        'deed_real_estates',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('deed_id', sa.Integer(), nullable=False),
        sa.Column('deed_serial', sa.String(length=50), nullable=True),
        sa.Column('region_code', sa.String(length=10), nullable=True),
        sa.Column('region_name', sa.String(length=100), nullable=True),
        sa.Column('city_code', sa.Integer(), nullable=True),
        sa.Column('city_name', sa.String(length=100), nullable=True),
        sa.Column('real_estate_type_name', sa.String(length=100), nullable=True),
        sa.Column('land_number', sa.String(length=50), nullable=True),
        sa.Column('plan_number', sa.String(length=100), nullable=True),
        sa.Column('area', sa.Numeric(10, 2), nullable=True),
        sa.Column('area_text', sa.Text(), nullable=True),
        sa.Column('district_code', sa.Integer(), nullable=True),
        sa.Column('district_name', sa.String(length=100), nullable=True),
        sa.Column('location_description', sa.Text(), nullable=True),
        sa.Column('constrained', sa.Integer(), nullable=True),
        sa.Column('halt', sa.Integer(), nullable=True),
        sa.Column('pawned', sa.Integer(), nullable=True),
        sa.Column('testament', sa.Integer(), nullable=True),
        sa.Column('is_north_riyadh_exceptioned', sa.Integer(), nullable=True),
        
        # Border descriptions
        sa.Column('border_north_description', sa.Text(), nullable=True),
        sa.Column('border_north_length', sa.Numeric(10, 2), nullable=True),
        sa.Column('border_north_length_char', sa.Text(), nullable=True),
        sa.Column('border_south_description', sa.Text(), nullable=True),
        sa.Column('border_south_length', sa.Numeric(10, 2), nullable=True),
        sa.Column('border_south_length_char', sa.Text(), nullable=True),
        sa.Column('border_east_description', sa.Text(), nullable=True),
        sa.Column('border_east_length', sa.String(length=50), nullable=True),  # VARCHAR due to mixed input like '22ز6'
        sa.Column('border_east_length_char', sa.Text(), nullable=True),
        sa.Column('border_west_description', sa.Text(), nullable=True),
        sa.Column('border_west_length', sa.Numeric(10, 2), nullable=True),
        sa.Column('border_west_length_char', sa.Text(), nullable=True),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['deed_id'], ['wathq.deeds.id'], ondelete='CASCADE'),
        schema='wathq'
    )
    
    # Create index on deed_id for faster joins
    op.create_index('ix_wathq_deed_real_estates_deed_id', 'deed_real_estates', ['deed_id'], schema='wathq')


def downgrade():
    # Drop tables in reverse order (child tables first)
    op.drop_index('ix_wathq_deed_real_estates_deed_id', table_name='deed_real_estates', schema='wathq')
    op.drop_table('deed_real_estates', schema='wathq')
    
    op.drop_index('ix_wathq_deed_owners_deed_id', table_name='deed_owners', schema='wathq')
    op.drop_table('deed_owners', schema='wathq')
    
    op.drop_index('ix_wathq_deeds_deed_serial', table_name='deeds', schema='wathq')
    op.drop_index('ix_wathq_deeds_deed_number', table_name='deeds', schema='wathq')
    op.drop_table('deeds', schema='wathq')
