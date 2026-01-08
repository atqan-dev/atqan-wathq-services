"""create_power_of_attorney_tables

Revision ID: 20250108_poa
Revises: 030f3032b865
Create Date: 2025-01-08 10:41:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250108_poa'
down_revision = '030f3032b865'
branch_labels = None
depends_on = None


def upgrade():
    # Create power_of_attorney master table
    op.create_table(
        'power_of_attorney',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('code', sa.String(length=50), nullable=False, unique=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('issue_hijri_date', sa.String(length=20), nullable=True),
        sa.Column('issue_greg_date', sa.Date(), nullable=True),
        sa.Column('expiry_hijri_date', sa.String(length=20), nullable=True),
        sa.Column('expiry_greg_date', sa.Date(), nullable=True),
        sa.Column('attorney_type', sa.String(length=100), nullable=True),
        sa.Column('location_id', sa.Integer(), nullable=True),
        sa.Column('location_name', sa.String(length=255), nullable=True),
        sa.Column('agents_behavior_ar', sa.String(length=50), nullable=True),
        sa.Column('agents_behavior_en', sa.String(length=50), nullable=True),
        sa.Column('document_text', sa.Text(), nullable=True),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('request_body', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        schema='wathq'
    )
    
    # Create index on code for faster lookups
    op.create_index('ix_wathq_power_of_attorney_code', 'power_of_attorney', ['code'], unique=True, schema='wathq')

    # Create poa_allowed_actors table
    op.create_table(
        'poa_allowed_actors',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('poa_id', sa.Integer(), nullable=False),
        sa.Column('identity_no', sa.String(length=50), nullable=True),
        sa.Column('social_type_id', sa.Integer(), nullable=True),
        sa.Column('social_type_name', sa.String(length=100), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('type_id', sa.Integer(), nullable=True),
        sa.Column('type_name', sa.String(length=100), nullable=True),
        sa.Column('type_name_en', sa.String(length=100), nullable=True),
        sa.Column('sefa_id', sa.Integer(), nullable=True),
        sa.Column('sefa_name', sa.String(length=100), nullable=True),
        sa.Column('national_number', sa.String(length=50), nullable=True),
        sa.Column('cr_number', sa.String(length=50), nullable=True),
        sa.Column('karar_number', sa.Integer(), nullable=True),
        sa.Column('malaki_number', sa.Integer(), nullable=True),
        sa.Column('document_type_name', sa.String(length=100), nullable=True),
        sa.Column('company_represent_type_id', sa.Integer(), nullable=True),
        sa.Column('company_represent_type_name', sa.String(length=100), nullable=True),
        sa.Column('sakk_number', sa.Integer(), nullable=True),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['poa_id'], ['wathq.power_of_attorney.id'], ondelete='CASCADE'),
        schema='wathq'
    )
    
    # Create index on poa_id for faster joins
    op.create_index('ix_wathq_poa_allowed_actors_poa_id', 'poa_allowed_actors', ['poa_id'], schema='wathq')

    # Create poa_principals table
    op.create_table(
        'poa_principals',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('poa_id', sa.Integer(), nullable=False),
        sa.Column('principal_identity_id', sa.String(length=50), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('birthday', sa.DateTime(), nullable=True),
        sa.Column('sefa_id', sa.Integer(), nullable=True),
        sa.Column('sefa_name', sa.String(length=100), nullable=True),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['poa_id'], ['wathq.power_of_attorney.id'], ondelete='CASCADE'),
        schema='wathq'
    )
    
    # Create index on poa_id for faster joins
    op.create_index('ix_wathq_poa_principals_poa_id', 'poa_principals', ['poa_id'], schema='wathq')

    # Create poa_agents table
    op.create_table(
        'poa_agents',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('poa_id', sa.Integer(), nullable=False),
        sa.Column('agent_identity_id', sa.String(length=50), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('birthday', sa.DateTime(), nullable=True),
        sa.Column('sefa_id', sa.Integer(), nullable=True),
        sa.Column('sefa_name', sa.String(length=100), nullable=True),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['poa_id'], ['wathq.power_of_attorney.id'], ondelete='CASCADE'),
        schema='wathq'
    )
    
    # Create index on poa_id for faster joins
    op.create_index('ix_wathq_poa_agents_poa_id', 'poa_agents', ['poa_id'], schema='wathq')

    # Create poa_text_list_items table
    op.create_table(
        'poa_text_list_items',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('poa_id', sa.Integer(), nullable=False),
        sa.Column('list_item_id', sa.Integer(), nullable=True),
        sa.Column('text_content', sa.Text(), nullable=True),
        sa.Column('item_type', sa.String(length=100), nullable=True),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['poa_id'], ['wathq.power_of_attorney.id'], ondelete='CASCADE'),
        schema='wathq'
    )
    
    # Create index on poa_id for faster joins
    op.create_index('ix_wathq_poa_text_list_items_poa_id', 'poa_text_list_items', ['poa_id'], schema='wathq')


def downgrade():
    # Drop tables in reverse order (child tables first)
    op.drop_index('ix_wathq_poa_text_list_items_poa_id', table_name='poa_text_list_items', schema='wathq')
    op.drop_table('poa_text_list_items', schema='wathq')
    
    op.drop_index('ix_wathq_poa_agents_poa_id', table_name='poa_agents', schema='wathq')
    op.drop_table('poa_agents', schema='wathq')
    
    op.drop_index('ix_wathq_poa_principals_poa_id', table_name='poa_principals', schema='wathq')
    op.drop_table('poa_principals', schema='wathq')
    
    op.drop_index('ix_wathq_poa_allowed_actors_poa_id', table_name='poa_allowed_actors', schema='wathq')
    op.drop_table('poa_allowed_actors', schema='wathq')
    
    op.drop_index('ix_wathq_power_of_attorney_code', table_name='power_of_attorney', schema='wathq')
    op.drop_table('power_of_attorney', schema='wathq')
