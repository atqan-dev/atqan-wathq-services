"""create_corporate_contracts_tables

Revision ID: 030f3032b865
Revises: df7e711263ba
Create Date: 2026-01-07 10:54:27.038191

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '030f3032b865'
down_revision = 'df7e711263ba'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create corporate_contracts master table
    op.create_table(
        'corporate_contracts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=True),
        sa.Column('contract_copy_number', sa.Integer(), nullable=True),
        sa.Column('contract_date', sa.Date(), nullable=True),
        # Entity Details
        sa.Column('cr_national_number', sa.String(50), nullable=True),
        sa.Column('cr_number', sa.String(50), nullable=True),
        sa.Column('entity_name', sa.String(255), nullable=True),
        sa.Column('entity_name_lang_desc', sa.String(50), nullable=True),
        sa.Column('company_duration', sa.Integer(), nullable=True),
        sa.Column('headquarter_city_name', sa.String(100), nullable=True),
        sa.Column('is_license_based', sa.Boolean(), nullable=True),
        sa.Column('entity_type_name', sa.String(100), nullable=True),
        sa.Column('entity_form_name', sa.String(100), nullable=True),
        # Fiscal Year
        sa.Column('fiscal_calendar_type', sa.String(50), nullable=True),
        sa.Column('fiscal_year_end_month', sa.Integer(), nullable=True),
        sa.Column('fiscal_year_end_day', sa.Integer(), nullable=True),
        sa.Column('fiscal_year_end_year', sa.Integer(), nullable=True),
        # Capital Summary
        sa.Column('currency_name', sa.String(50), nullable=True),
        sa.Column('total_capital', sa.Numeric(15, 2), nullable=True),
        sa.Column('paid_capital', sa.Numeric(15, 2), nullable=True),
        sa.Column('cash_capital', sa.Numeric(15, 2), nullable=True),
        sa.Column('in_kind_capital', sa.Numeric(15, 2), nullable=True),
        # Set Aside / Profit Allocation
        sa.Column('is_set_aside_enabled', sa.Boolean(), nullable=True),
        sa.Column('profit_allocation_percentage', sa.Numeric(5, 2), nullable=True),
        sa.Column('profit_allocation_purpose', sa.Text(), nullable=True),
        sa.Column('additional_decision_text', sa.Text(), nullable=True),
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('request_body', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='wathq'
    )
    op.create_index('ix_wathq_corporate_contracts_cr_number', 'corporate_contracts', ['cr_number'], schema='wathq')
    
    # Create contract_stocks table
    op.create_table(
        'contract_stocks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('stock_type_name', sa.String(100), nullable=True),
        sa.Column('stock_count', sa.Integer(), nullable=True),
        sa.Column('stock_value', sa.Numeric(15, 2), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['wathq.corporate_contracts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='wathq'
    )
    
    # Create contract_parties table
    op.create_table(
        'contract_parties',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('type_name', sa.String(100), nullable=True),
        sa.Column('identity_number', sa.String(50), nullable=True),
        sa.Column('identity_type', sa.String(50), nullable=True),
        sa.Column('nationality', sa.String(100), nullable=True),
        # Guardian Info
        sa.Column('guardian_name', sa.String(255), nullable=True),
        sa.Column('guardian_identity_number', sa.String(50), nullable=True),
        sa.Column('is_father_guardian', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['wathq.corporate_contracts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='wathq'
    )
    
    # Create contract_managers table
    op.create_table(
        'contract_managers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('type_name', sa.String(100), nullable=True),
        sa.Column('is_licensed', sa.Boolean(), nullable=True),
        sa.Column('identity_number', sa.String(50), nullable=True),
        sa.Column('nationality', sa.String(100), nullable=True),
        sa.Column('position_name', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['wathq.corporate_contracts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='wathq'
    )
    
    # Create contract_management_config table
    op.create_table(
        'contract_management_config',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('structure_name', sa.String(100), nullable=True),
        sa.Column('meeting_quorum_name', sa.String(100), nullable=True),
        sa.Column('can_delegate_attendance', sa.Boolean(), nullable=True),
        sa.Column('term_years', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['wathq.corporate_contracts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='wathq'
    )
    
    # Create contract_activities table
    op.create_table(
        'contract_activities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('activity_id', sa.String(50), nullable=True),
        sa.Column('activity_name', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['wathq.corporate_contracts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='wathq'
    )
    
    # Create contract_articles table
    op.create_table(
        'contract_articles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('original_id', sa.Integer(), nullable=True),
        sa.Column('article_text', sa.Text(), nullable=True),
        sa.Column('part_name', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['wathq.corporate_contracts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='wathq'
    )
    
    # Create contract_decisions table
    op.create_table(
        'contract_decisions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('decision_name', sa.Text(), nullable=True),
        sa.Column('approve_percentage', sa.Numeric(5, 2), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['wathq.corporate_contracts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='wathq'
    )
    
    # Create notification_channels table
    op.create_table(
        'notification_channels',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('channel_name', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['wathq.corporate_contracts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='wathq'
    )


def downgrade() -> None:
    op.drop_table('notification_channels', schema='wathq')
    op.drop_table('contract_decisions', schema='wathq')
    op.drop_table('contract_articles', schema='wathq')
    op.drop_table('contract_activities', schema='wathq')
    op.drop_table('contract_management_config', schema='wathq')
    op.drop_table('contract_managers', schema='wathq')
    op.drop_table('contract_parties', schema='wathq')
    op.drop_table('contract_stocks', schema='wathq')
    op.drop_index('ix_wathq_corporate_contracts_cr_number', 'corporate_contracts', schema='wathq')
    op.drop_table('corporate_contracts', schema='wathq')
