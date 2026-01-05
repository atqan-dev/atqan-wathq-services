"""create wathq schema

Revision ID: 20250105_create_wathq_schema
Revises: 
Create Date: 2025-01-05 10:16:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '20250105_create_wathq_schema'
down_revision = 'add_totp_fields'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('CREATE SCHEMA IF NOT EXISTS wathq')
    
    op.create_table(
        'commercial_registrations',
        sa.Column('cr_number', sa.String(20), primary_key=True),
        sa.Column('cr_national_number', sa.String(20), nullable=True),
        sa.Column('version_no', sa.Integer, nullable=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('name_lang_id', sa.Integer, nullable=True),
        sa.Column('name_lang_desc', sa.String(50), nullable=True),
        sa.Column('cr_capital', sa.Numeric(15, 2), nullable=True),
        sa.Column('company_duration', sa.Integer, nullable=True),
        sa.Column('is_main', sa.Boolean, nullable=True),
        sa.Column('issue_date_gregorian', sa.Date, nullable=True),
        sa.Column('issue_date_hijri', sa.String(10), nullable=True),
        sa.Column('main_cr_national_number', sa.String(20), nullable=True),
        sa.Column('main_cr_number', sa.String(20), nullable=True),
        sa.Column('in_liquidation_process', sa.Boolean, nullable=True),
        sa.Column('has_ecommerce', sa.Boolean, nullable=True),
        sa.Column('headquarter_city_id', sa.Integer, nullable=True),
        sa.Column('headquarter_city_name', sa.String(100), nullable=True),
        sa.Column('is_license_based', sa.Boolean, nullable=True),
        sa.Column('license_issuer_national_number', sa.String(20), nullable=True),
        sa.Column('license_issuer_name', sa.String(100), nullable=True),
        sa.Column('partners_nationality_id', sa.Integer, nullable=True),
        sa.Column('partners_nationality_name', sa.String(100), nullable=True),
        sa.Column('entity_type_id', sa.Integer, nullable=True),
        sa.Column('entity_type_name', sa.String(100), nullable=True),
        sa.Column('entity_form_id', sa.Integer, nullable=True),
        sa.Column('entity_form_name', sa.String(100), nullable=True),
        sa.Column('status_id', sa.Integer, nullable=True),
        sa.Column('status_name', sa.String(50), nullable=True),
        sa.Column('confirmation_date_gregorian', sa.Date, nullable=True),
        sa.Column('confirmation_date_hijri', sa.String(10), nullable=True),
        sa.Column('reactivation_date_gregorian', sa.Date, nullable=True),
        sa.Column('reactivation_date_hijri', sa.String(10), nullable=True),
        sa.Column('suspension_date_gregorian', sa.Date, nullable=True),
        sa.Column('suspension_date_hijri', sa.String(10), nullable=True),
        sa.Column('deletion_date_gregorian', sa.Date, nullable=True),
        sa.Column('deletion_date_hijri', sa.String(10), nullable=True),
        sa.Column('contact_phone', sa.String(20), nullable=True),
        sa.Column('contact_mobile', sa.String(20), nullable=True),
        sa.Column('contact_email', sa.String(255), nullable=True),
        sa.Column('contact_website', sa.String(255), nullable=True),
        sa.Column('fiscal_is_first', sa.Boolean, nullable=True),
        sa.Column('fiscal_calendar_type_id', sa.Integer, nullable=True),
        sa.Column('fiscal_calendar_type_name', sa.String(50), nullable=True),
        sa.Column('fiscal_end_month', sa.Integer, nullable=True),
        sa.Column('fiscal_end_day', sa.Integer, nullable=True),
        sa.Column('fiscal_end_year', sa.Integer, nullable=True),
        sa.Column('mgmt_structure_id', sa.Integer, nullable=True),
        sa.Column('mgmt_structure_name', sa.String(100), nullable=True),
        schema='wathq'
    )
    
    op.create_table(
        'capital_info',
        sa.Column('cr_number', sa.String(20), primary_key=True),
        sa.Column('currency_id', sa.Integer, nullable=True),
        sa.Column('currency_name', sa.String(50), nullable=True),
        sa.Column('contrib_type_id', sa.Integer, nullable=True),
        sa.Column('contrib_type_name', sa.String(50), nullable=True),
        sa.Column('contrib_cash', sa.Numeric(15, 2), nullable=True),
        sa.Column('contrib_in_kind', sa.Numeric(15, 2), nullable=True),
        sa.Column('contrib_value', sa.Numeric(15, 2), nullable=True),
        sa.Column('total_cash_contribution', sa.Numeric(15, 2), nullable=True),
        sa.Column('total_in_kind_contribution', sa.Numeric(15, 2), nullable=True),
        sa.Column('stock_type_id', sa.Integer, nullable=True),
        sa.Column('stock_type_name', sa.String(50), nullable=True),
        sa.Column('stock_capital', sa.Numeric(15, 2), nullable=True),
        sa.Column('stock_announced_capital', sa.Numeric(15, 2), nullable=True),
        sa.Column('stock_paid_capital', sa.Numeric(15, 2), nullable=True),
        sa.Column('stock_cash_capital', sa.Numeric(15, 2), nullable=True),
        sa.Column('stock_in_kind_capital', sa.Numeric(15, 2), nullable=True),
        sa.ForeignKeyConstraint(['cr_number'], ['wathq.commercial_registrations.cr_number']),
        schema='wathq'
    )
    
    op.create_table(
        'cr_entity_characters',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('cr_number', sa.String(20), nullable=False),
        sa.Column('character_id', sa.Integer, nullable=True),
        sa.Column('character_name', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['cr_number'], ['wathq.commercial_registrations.cr_number']),
        schema='wathq'
    )
    
    op.create_table(
        'cr_activities',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('cr_number', sa.String(20), nullable=False),
        sa.Column('activity_id', sa.String(20), nullable=True),
        sa.Column('activity_name', sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(['cr_number'], ['wathq.commercial_registrations.cr_number']),
        schema='wathq'
    )
    
    op.create_table(
        'cr_stocks',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('cr_number', sa.String(20), nullable=False),
        sa.Column('stock_count', sa.Integer, nullable=True),
        sa.Column('stock_value', sa.Numeric(15, 2), nullable=True),
        sa.Column('type_id', sa.Integer, nullable=True),
        sa.Column('type_name', sa.String(50), nullable=True),
        sa.Column('class_reference_id', sa.Integer, nullable=True),
        sa.Column('class_name', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['cr_number'], ['wathq.commercial_registrations.cr_number']),
        schema='wathq'
    )
    
    op.create_table(
        'cr_estores',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('cr_number', sa.String(20), nullable=False),
        sa.Column('auth_platform_url', sa.String(255), nullable=True),
        sa.Column('store_url', sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(['cr_number'], ['wathq.commercial_registrations.cr_number']),
        schema='wathq'
    )
    
    op.create_table(
        'cr_estore_activities',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('estore_id', sa.Integer, nullable=False),
        sa.Column('activity_id', sa.String(20), nullable=True),
        sa.Column('activity_name', sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(['estore_id'], ['wathq.cr_estores.id']),
        schema='wathq'
    )
    
    op.create_table(
        'cr_parties',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('cr_number', sa.String(20), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('type_id', sa.Integer, nullable=True),
        sa.Column('type_name', sa.String(100), nullable=True),
        sa.Column('identity_id', sa.String(50), nullable=True),
        sa.Column('identity_type_id', sa.Integer, nullable=True),
        sa.Column('identity_type_name', sa.String(50), nullable=True),
        sa.Column('share_cash_count', sa.Integer, nullable=True),
        sa.Column('share_in_kind_count', sa.Integer, nullable=True),
        sa.Column('share_total_count', sa.Integer, nullable=True),
        sa.ForeignKeyConstraint(['cr_number'], ['wathq.commercial_registrations.cr_number']),
        schema='wathq'
    )
    
    op.create_table(
        'cr_party_partnerships',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('party_id', sa.Integer, nullable=False),
        sa.Column('partnership_id', sa.Integer, nullable=True),
        sa.Column('partnership_name', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['party_id'], ['wathq.cr_parties.id']),
        schema='wathq'
    )
    
    op.create_table(
        'cr_managers',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('cr_number', sa.String(20), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('type_id', sa.Integer, nullable=True),
        sa.Column('type_name', sa.String(100), nullable=True),
        sa.Column('is_licensed', sa.Boolean, nullable=True),
        sa.Column('identity_id', sa.String(50), nullable=True),
        sa.Column('identity_type_id', sa.Integer, nullable=True),
        sa.Column('identity_type_name', sa.String(50), nullable=True),
        sa.Column('nationality_id', sa.Integer, nullable=True),
        sa.Column('nationality_name', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['cr_number'], ['wathq.commercial_registrations.cr_number']),
        schema='wathq'
    )
    
    op.create_table(
        'cr_manager_positions',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('manager_id', sa.Integer, nullable=False),
        sa.Column('position_id', sa.Integer, nullable=True),
        sa.Column('position_name', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['manager_id'], ['wathq.cr_managers.id']),
        schema='wathq'
    )
    
    op.create_table(
        'cr_liquidators',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('cr_number', sa.String(20), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('type_id', sa.Integer, nullable=True),
        sa.Column('type_name', sa.String(100), nullable=True),
        sa.Column('identity_id', sa.String(50), nullable=True),
        sa.Column('identity_type_id', sa.Integer, nullable=True),
        sa.Column('identity_type_name', sa.String(50), nullable=True),
        sa.Column('nationality_id', sa.Integer, nullable=True),
        sa.Column('nationality_name', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['cr_number'], ['wathq.commercial_registrations.cr_number']),
        schema='wathq'
    )
    
    op.create_table(
        'cr_liquidator_positions',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('liquidator_id', sa.Integer, nullable=False),
        sa.Column('position_id', sa.Integer, nullable=True),
        sa.Column('position_name', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['liquidator_id'], ['wathq.cr_liquidators.id']),
        schema='wathq'
    )


def downgrade():
    op.drop_table('cr_liquidator_positions', schema='wathq')
    op.drop_table('cr_liquidators', schema='wathq')
    op.drop_table('cr_manager_positions', schema='wathq')
    op.drop_table('cr_managers', schema='wathq')
    op.drop_table('cr_party_partnerships', schema='wathq')
    op.drop_table('cr_parties', schema='wathq')
    op.drop_table('cr_estore_activities', schema='wathq')
    op.drop_table('cr_estores', schema='wathq')
    op.drop_table('cr_stocks', schema='wathq')
    op.drop_table('cr_activities', schema='wathq')
    op.drop_table('cr_entity_characters', schema='wathq')
    op.drop_table('capital_info', schema='wathq')
    op.drop_table('commercial_registrations', schema='wathq')
    op.execute('DROP SCHEMA IF EXISTS wathq CASCADE')
