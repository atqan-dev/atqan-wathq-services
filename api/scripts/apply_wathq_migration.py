#!/usr/bin/env python3
"""
Apply the wathq schema migration to create all tables.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def apply_wathq_migration():
    """Manually apply the wathq schema migration."""
    engine = create_engine(str(settings.DATABASE_URL))
    
    try:
        logger.info("=" * 70)
        logger.info("APPLYING WATHQ SCHEMA MIGRATION")
        logger.info("=" * 70)
        
        with engine.connect() as conn:
            # Check if schema exists
            result = conn.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'wathq'"))
            if not result.fetchone():
                logger.info("Creating wathq schema...")
                conn.execute(text("CREATE SCHEMA wathq"))
                conn.commit()
                logger.info("✓ Created wathq schema")
            else:
                logger.info("✓ Wathq schema already exists")
            
            # Check if tables exist
            result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'wathq'"))
            table_count = result.fetchone()[0]
            
            if table_count > 0:
                logger.info(f"✓ Wathq schema already has {table_count} tables")
                logger.info("\n" + "=" * 70)
                logger.info("WATHQ SCHEMA IS READY!")
                logger.info("=" * 70)
                return True
            
            logger.info("\nCreating wathq tables...")
            
            # Execute the migration SQL
            migration_sql = """
            -- Commercial Registrations table
            CREATE TABLE IF NOT EXISTS wathq.commercial_registrations (
                cr_number VARCHAR(20) PRIMARY KEY,
                cr_national_number VARCHAR(20),
                version_no INTEGER,
                name VARCHAR(255),
                name_lang_id INTEGER,
                name_lang_desc VARCHAR(50),
                cr_capital NUMERIC(15, 2),
                company_duration INTEGER,
                is_main BOOLEAN,
                issue_date_gregorian DATE,
                issue_date_hijri VARCHAR(10),
                main_cr_national_number VARCHAR(20),
                main_cr_number VARCHAR(20),
                in_liquidation_process BOOLEAN,
                has_ecommerce BOOLEAN,
                headquarter_city_id INTEGER,
                headquarter_city_name VARCHAR(100),
                is_license_based BOOLEAN,
                license_issuer_national_number VARCHAR(20),
                license_issuer_name VARCHAR(100),
                partners_nationality_id INTEGER,
                partners_nationality_name VARCHAR(100),
                entity_type_id INTEGER,
                entity_type_name VARCHAR(100),
                entity_form_id INTEGER,
                entity_form_name VARCHAR(100),
                status_id INTEGER,
                status_name VARCHAR(50),
                confirmation_date_gregorian DATE,
                confirmation_date_hijri VARCHAR(10),
                reactivation_date_gregorian DATE,
                reactivation_date_hijri VARCHAR(10),
                suspension_date_gregorian DATE,
                suspension_date_hijri VARCHAR(10),
                deletion_date_gregorian DATE,
                deletion_date_hijri VARCHAR(10),
                contact_phone VARCHAR(20),
                contact_mobile VARCHAR(20),
                contact_email VARCHAR(255),
                contact_website VARCHAR(255),
                fiscal_is_first BOOLEAN,
                fiscal_calendar_type_id INTEGER,
                fiscal_calendar_type_name VARCHAR(50),
                fiscal_end_month INTEGER,
                fiscal_end_day INTEGER,
                fiscal_end_year INTEGER,
                mgmt_structure_id INTEGER,
                mgmt_structure_name VARCHAR(100)
            );

            -- Capital Info table
            CREATE TABLE IF NOT EXISTS wathq.capital_info (
                cr_number VARCHAR(20) PRIMARY KEY REFERENCES wathq.commercial_registrations(cr_number),
                currency_id INTEGER,
                currency_name VARCHAR(50),
                contrib_type_id INTEGER,
                contrib_type_name VARCHAR(50),
                contrib_cash NUMERIC(15, 2),
                contrib_in_kind NUMERIC(15, 2),
                contrib_value NUMERIC(15, 2),
                total_cash_contribution NUMERIC(15, 2),
                total_in_kind_contribution NUMERIC(15, 2),
                stock_type_id INTEGER,
                stock_type_name VARCHAR(50),
                stock_capital NUMERIC(15, 2),
                stock_announced_capital NUMERIC(15, 2),
                stock_paid_capital NUMERIC(15, 2),
                stock_cash_capital NUMERIC(15, 2),
                stock_in_kind_capital NUMERIC(15, 2)
            );

            -- CR Entity Characters table
            CREATE TABLE IF NOT EXISTS wathq.cr_entity_characters (
                id SERIAL PRIMARY KEY,
                cr_number VARCHAR(20) REFERENCES wathq.commercial_registrations(cr_number),
                character_id INTEGER,
                character_name VARCHAR(100)
            );

            -- CR Activities table
            CREATE TABLE IF NOT EXISTS wathq.cr_activities (
                id SERIAL PRIMARY KEY,
                cr_number VARCHAR(20) REFERENCES wathq.commercial_registrations(cr_number),
                activity_id VARCHAR(20),
                activity_name VARCHAR(255)
            );

            -- CR Stocks table
            CREATE TABLE IF NOT EXISTS wathq.cr_stocks (
                id SERIAL PRIMARY KEY,
                cr_number VARCHAR(20) REFERENCES wathq.commercial_registrations(cr_number),
                stock_count INTEGER,
                stock_value NUMERIC(15, 2),
                type_id INTEGER,
                type_name VARCHAR(50),
                class_reference_id INTEGER,
                class_name VARCHAR(50)
            );

            -- CR Estores table
            CREATE TABLE IF NOT EXISTS wathq.cr_estores (
                id SERIAL PRIMARY KEY,
                cr_number VARCHAR(20) REFERENCES wathq.commercial_registrations(cr_number),
                auth_platform_url VARCHAR(255),
                store_url VARCHAR(255)
            );

            -- CR Estore Activities table
            CREATE TABLE IF NOT EXISTS wathq.cr_estore_activities (
                id SERIAL PRIMARY KEY,
                estore_id INTEGER REFERENCES wathq.cr_estores(id),
                activity_id VARCHAR(20),
                activity_name VARCHAR(255)
            );

            -- CR Parties table
            CREATE TABLE IF NOT EXISTS wathq.cr_parties (
                id SERIAL PRIMARY KEY,
                cr_number VARCHAR(20) REFERENCES wathq.commercial_registrations(cr_number),
                name VARCHAR(255),
                type_id INTEGER,
                type_name VARCHAR(100),
                identity_id VARCHAR(50),
                identity_type_id INTEGER,
                identity_type_name VARCHAR(50),
                share_cash_count INTEGER,
                share_in_kind_count INTEGER,
                share_total_count INTEGER
            );

            -- CR Party Partnerships table
            CREATE TABLE IF NOT EXISTS wathq.cr_party_partnerships (
                id SERIAL PRIMARY KEY,
                party_id INTEGER REFERENCES wathq.cr_parties(id),
                partnership_id INTEGER,
                partnership_name VARCHAR(100)
            );

            -- CR Managers table
            CREATE TABLE IF NOT EXISTS wathq.cr_managers (
                id SERIAL PRIMARY KEY,
                cr_number VARCHAR(20) REFERENCES wathq.commercial_registrations(cr_number),
                name VARCHAR(255),
                type_id INTEGER,
                type_name VARCHAR(100),
                is_licensed BOOLEAN,
                identity_id VARCHAR(50),
                identity_type_id INTEGER,
                identity_type_name VARCHAR(50),
                nationality_id INTEGER,
                nationality_name VARCHAR(100)
            );

            -- CR Manager Positions table
            CREATE TABLE IF NOT EXISTS wathq.cr_manager_positions (
                id SERIAL PRIMARY KEY,
                manager_id INTEGER REFERENCES wathq.cr_managers(id),
                position_id INTEGER,
                position_name VARCHAR(100)
            );

            -- CR Liquidators table
            CREATE TABLE IF NOT EXISTS wathq.cr_liquidators (
                id SERIAL PRIMARY KEY,
                cr_number VARCHAR(20) REFERENCES wathq.commercial_registrations(cr_number),
                name VARCHAR(255),
                type_id INTEGER,
                type_name VARCHAR(100),
                identity_id VARCHAR(50),
                identity_type_id INTEGER,
                identity_type_name VARCHAR(50),
                nationality_id INTEGER,
                nationality_name VARCHAR(100)
            );

            -- CR Liquidator Positions table
            CREATE TABLE IF NOT EXISTS wathq.cr_liquidator_positions (
                id SERIAL PRIMARY KEY,
                liquidator_id INTEGER REFERENCES wathq.cr_liquidators(id),
                position_id INTEGER,
                position_name VARCHAR(100)
            );
            """
            
            # Execute all statements
            for statement in migration_sql.split(';'):
                if statement.strip():
                    conn.execute(text(statement))
            
            conn.commit()
            logger.info("✓ Created all wathq tables")
            
            # Verify
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'wathq' ORDER BY table_name"))
            tables = [row[0] for row in result.fetchall()]
            
            logger.info(f"\n✓ Created {len(tables)} tables:")
            for table in tables:
                logger.info(f"  - {table}")
            
            logger.info("\n" + "=" * 70)
            logger.info("✓ WATHQ SCHEMA MIGRATION COMPLETED!")
            logger.info("=" * 70)
            logger.info("\nYou can now use the wathq API endpoints:")
            logger.info("  GET  /api/v1/wathq/cr-data/")
            logger.info("  GET  /api/v1/wathq/cr-data/{cr_number}")
            logger.info("  POST /api/v1/wathq/cr-data/")
            logger.info("=" * 70)
            
        return True
        
    except Exception as e:
        logger.error(f"\n✗ Error: {e}", exc_info=True)
        return False
    finally:
        engine.dispose()


if __name__ == "__main__":
    success = apply_wathq_migration()
    sys.exit(0 if success else 1)
