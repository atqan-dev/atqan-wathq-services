"""add_auto_id_to_cr_tables

Revision ID: eb849cd4799a
Revises: 2e1058b70502
Create Date: 2026-01-06 10:55:42.005445

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb849cd4799a'
down_revision = '2e1058b70502'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Add auto-incrementing id column to commercial_registrations table
    # First add as nullable to allow existing rows
    op.add_column('commercial_registrations', 
                  sa.Column('id', sa.Integer(), nullable=True),
                  schema='wathq')
    
    # Create a sequence for auto-incrementing
    op.execute('CREATE SEQUENCE IF NOT EXISTS wathq.commercial_registrations_id_seq')
    
    # Populate id values for existing rows using the sequence
    op.execute("""
        UPDATE wathq.commercial_registrations
        SET id = nextval('wathq.commercial_registrations_id_seq')
        WHERE id IS NULL
    """)
    
    # Now make the column NOT NULL
    op.alter_column('commercial_registrations', 'id', nullable=False, schema='wathq')
    
    # Set the sequence as the default for the column
    op.execute("""
        ALTER TABLE wathq.commercial_registrations 
        ALTER COLUMN id SET DEFAULT nextval('wathq.commercial_registrations_id_seq')
    """)
    
    # Set the sequence ownership to the column
    op.execute("""
        ALTER SEQUENCE wathq.commercial_registrations_id_seq 
        OWNED BY wathq.commercial_registrations.id
    """)
    
    # Create a unique constraint on the new id column
    op.create_unique_constraint('uq_commercial_registrations_id', 'commercial_registrations', ['id'], schema='wathq')
    
    # Step 2: Add cr_id foreign key column to related tables
    
    # capital_info - this has a 1-to-1 relationship, so we'll add cr_id
    op.add_column('capital_info',
                  sa.Column('cr_id', sa.Integer(), nullable=True),
                  schema='wathq')
    
    # Update cr_id values based on cr_number
    op.execute("""
        UPDATE wathq.capital_info ci
        SET cr_id = cr.id
        FROM wathq.commercial_registrations cr
        WHERE ci.cr_number = cr.cr_number
    """)
    
    # Make cr_id NOT NULL after populating
    op.alter_column('capital_info', 'cr_id', nullable=False, schema='wathq')
    
    # Create foreign key constraint
    op.create_foreign_key('fk_capital_info_cr_id', 'capital_info', 'commercial_registrations',
                         ['cr_id'], ['id'], source_schema='wathq', referent_schema='wathq')
    
    # cr_entity_characters
    op.add_column('cr_entity_characters',
                  sa.Column('cr_id', sa.Integer(), nullable=True),
                  schema='wathq')
    
    op.execute("""
        UPDATE wathq.cr_entity_characters cec
        SET cr_id = cr.id
        FROM wathq.commercial_registrations cr
        WHERE cec.cr_number = cr.cr_number
    """)
    
    op.alter_column('cr_entity_characters', 'cr_id', nullable=False, schema='wathq')
    op.create_foreign_key('fk_cr_entity_characters_cr_id', 'cr_entity_characters', 'commercial_registrations',
                         ['cr_id'], ['id'], source_schema='wathq', referent_schema='wathq')
    
    # cr_activities
    op.add_column('cr_activities',
                  sa.Column('cr_id', sa.Integer(), nullable=True),
                  schema='wathq')
    
    op.execute("""
        UPDATE wathq.cr_activities ca
        SET cr_id = cr.id
        FROM wathq.commercial_registrations cr
        WHERE ca.cr_number = cr.cr_number
    """)
    
    op.alter_column('cr_activities', 'cr_id', nullable=False, schema='wathq')
    op.create_foreign_key('fk_cr_activities_cr_id', 'cr_activities', 'commercial_registrations',
                         ['cr_id'], ['id'], source_schema='wathq', referent_schema='wathq')
    
    # cr_stocks
    op.add_column('cr_stocks',
                  sa.Column('cr_id', sa.Integer(), nullable=True),
                  schema='wathq')
    
    op.execute("""
        UPDATE wathq.cr_stocks cs
        SET cr_id = cr.id
        FROM wathq.commercial_registrations cr
        WHERE cs.cr_number = cr.cr_number
    """)
    
    op.alter_column('cr_stocks', 'cr_id', nullable=False, schema='wathq')
    op.create_foreign_key('fk_cr_stocks_cr_id', 'cr_stocks', 'commercial_registrations',
                         ['cr_id'], ['id'], source_schema='wathq', referent_schema='wathq')
    
    # cr_estores
    op.add_column('cr_estores',
                  sa.Column('cr_id', sa.Integer(), nullable=True),
                  schema='wathq')
    
    op.execute("""
        UPDATE wathq.cr_estores ce
        SET cr_id = cr.id
        FROM wathq.commercial_registrations cr
        WHERE ce.cr_number = cr.cr_number
    """)
    
    op.alter_column('cr_estores', 'cr_id', nullable=False, schema='wathq')
    op.create_foreign_key('fk_cr_estores_cr_id', 'cr_estores', 'commercial_registrations',
                         ['cr_id'], ['id'], source_schema='wathq', referent_schema='wathq')
    
    # cr_parties
    op.add_column('cr_parties',
                  sa.Column('cr_id', sa.Integer(), nullable=True),
                  schema='wathq')
    
    op.execute("""
        UPDATE wathq.cr_parties cp
        SET cr_id = cr.id
        FROM wathq.commercial_registrations cr
        WHERE cp.cr_number = cr.cr_number
    """)
    
    op.alter_column('cr_parties', 'cr_id', nullable=False, schema='wathq')
    op.create_foreign_key('fk_cr_parties_cr_id', 'cr_parties', 'commercial_registrations',
                         ['cr_id'], ['id'], source_schema='wathq', referent_schema='wathq')
    
    # cr_managers
    op.add_column('cr_managers',
                  sa.Column('cr_id', sa.Integer(), nullable=True),
                  schema='wathq')
    
    op.execute("""
        UPDATE wathq.cr_managers cm
        SET cr_id = cr.id
        FROM wathq.commercial_registrations cr
        WHERE cm.cr_number = cr.cr_number
    """)
    
    op.alter_column('cr_managers', 'cr_id', nullable=False, schema='wathq')
    op.create_foreign_key('fk_cr_managers_cr_id', 'cr_managers', 'commercial_registrations',
                         ['cr_id'], ['id'], source_schema='wathq', referent_schema='wathq')
    
    # cr_liquidators
    op.add_column('cr_liquidators',
                  sa.Column('cr_id', sa.Integer(), nullable=True),
                  schema='wathq')
    
    op.execute("""
        UPDATE wathq.cr_liquidators cl
        SET cr_id = cr.id
        FROM wathq.commercial_registrations cr
        WHERE cl.cr_number = cr.cr_number
    """)
    
    op.alter_column('cr_liquidators', 'cr_id', nullable=False, schema='wathq')
    op.create_foreign_key('fk_cr_liquidators_cr_id', 'cr_liquidators', 'commercial_registrations',
                         ['cr_id'], ['id'], source_schema='wathq', referent_schema='wathq')
    
    # Step 3: Drop old foreign key constraints on cr_number
    op.drop_constraint('capital_info_cr_number_fkey', 'capital_info', schema='wathq', type_='foreignkey')
    op.drop_constraint('cr_entity_characters_cr_number_fkey', 'cr_entity_characters', schema='wathq', type_='foreignkey')
    op.drop_constraint('cr_activities_cr_number_fkey', 'cr_activities', schema='wathq', type_='foreignkey')
    op.drop_constraint('cr_stocks_cr_number_fkey', 'cr_stocks', schema='wathq', type_='foreignkey')
    op.drop_constraint('cr_estores_cr_number_fkey', 'cr_estores', schema='wathq', type_='foreignkey')
    op.drop_constraint('cr_parties_cr_number_fkey', 'cr_parties', schema='wathq', type_='foreignkey')
    op.drop_constraint('cr_managers_cr_number_fkey', 'cr_managers', schema='wathq', type_='foreignkey')
    op.drop_constraint('cr_liquidators_cr_number_fkey', 'cr_liquidators', schema='wathq', type_='foreignkey')
    
    # Step 4: Keep cr_number columns for reference but they're no longer foreign keys
    # The cr_number columns remain in the tables for data integrity and reference


def downgrade() -> None:
    # Restore old foreign key constraints on cr_number
    op.create_foreign_key('capital_info_cr_number_fkey', 'capital_info', 'commercial_registrations',
                         ['cr_number'], ['cr_number'], source_schema='wathq', referent_schema='wathq')
    op.create_foreign_key('cr_entity_characters_cr_number_fkey', 'cr_entity_characters', 'commercial_registrations',
                         ['cr_number'], ['cr_number'], source_schema='wathq', referent_schema='wathq')
    op.create_foreign_key('cr_activities_cr_number_fkey', 'cr_activities', 'commercial_registrations',
                         ['cr_number'], ['cr_number'], source_schema='wathq', referent_schema='wathq')
    op.create_foreign_key('cr_stocks_cr_number_fkey', 'cr_stocks', 'commercial_registrations',
                         ['cr_number'], ['cr_number'], source_schema='wathq', referent_schema='wathq')
    op.create_foreign_key('cr_estores_cr_number_fkey', 'cr_estores', 'commercial_registrations',
                         ['cr_number'], ['cr_number'], source_schema='wathq', referent_schema='wathq')
    op.create_foreign_key('cr_parties_cr_number_fkey', 'cr_parties', 'commercial_registrations',
                         ['cr_number'], ['cr_number'], source_schema='wathq', referent_schema='wathq')
    op.create_foreign_key('cr_managers_cr_number_fkey', 'cr_managers', 'commercial_registrations',
                         ['cr_number'], ['cr_number'], source_schema='wathq', referent_schema='wathq')
    op.create_foreign_key('cr_liquidators_cr_number_fkey', 'cr_liquidators', 'commercial_registrations',
                         ['cr_number'], ['cr_number'], source_schema='wathq', referent_schema='wathq')
    
    # Drop new foreign key constraints
    op.drop_constraint('fk_capital_info_cr_id', 'capital_info', schema='wathq', type_='foreignkey')
    op.drop_constraint('fk_cr_entity_characters_cr_id', 'cr_entity_characters', schema='wathq', type_='foreignkey')
    op.drop_constraint('fk_cr_activities_cr_id', 'cr_activities', schema='wathq', type_='foreignkey')
    op.drop_constraint('fk_cr_stocks_cr_id', 'cr_stocks', schema='wathq', type_='foreignkey')
    op.drop_constraint('fk_cr_estores_cr_id', 'cr_estores', schema='wathq', type_='foreignkey')
    op.drop_constraint('fk_cr_parties_cr_id', 'cr_parties', schema='wathq', type_='foreignkey')
    op.drop_constraint('fk_cr_managers_cr_id', 'cr_managers', schema='wathq', type_='foreignkey')
    op.drop_constraint('fk_cr_liquidators_cr_id', 'cr_liquidators', schema='wathq', type_='foreignkey')
    
    # Drop cr_id columns
    op.drop_column('cr_liquidators', 'cr_id', schema='wathq')
    op.drop_column('cr_managers', 'cr_id', schema='wathq')
    op.drop_column('cr_parties', 'cr_id', schema='wathq')
    op.drop_column('cr_estores', 'cr_id', schema='wathq')
    op.drop_column('cr_stocks', 'cr_id', schema='wathq')
    op.drop_column('cr_activities', 'cr_id', schema='wathq')
    op.drop_column('cr_entity_characters', 'cr_id', schema='wathq')
    op.drop_column('capital_info', 'cr_id', schema='wathq')
    
    # Drop unique constraint and id column from commercial_registrations
    op.drop_constraint('uq_commercial_registrations_id', 'commercial_registrations', schema='wathq', type_='unique')
    op.drop_column('commercial_registrations', 'id', schema='wathq')
    
    # Drop the sequence (will be automatically dropped if owned by column, but explicit for clarity)
    op.execute('DROP SEQUENCE IF EXISTS wathq.commercial_registrations_id_seq')
