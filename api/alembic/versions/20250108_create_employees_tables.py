"""create_employees_tables

Revision ID: 20250108_employees
Revises: 20250108_addresses
Create Date: 2025-01-08 14:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250108_employees'
down_revision = '20250108_addresses'
branch_labels = None
depends_on = None


def upgrade():
    # Create employees master table
    op.create_table(
        'employees',
        sa.Column('employee_id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('nationality', sa.String(length=100), nullable=True),
        sa.Column('working_months', sa.Integer(), nullable=True),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('request_body', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        
        sa.PrimaryKeyConstraint('employee_id'),
        schema='wathq'
    )
    
    # Create indexes on frequently queried fields
    op.create_index('ix_wathq_employees_name', 'employees', ['name'], schema='wathq')
    op.create_index('ix_wathq_employees_nationality', 'employees', ['nationality'], schema='wathq')

    # Create employment_details table
    op.create_table(
        'employment_details',
        sa.Column('employment_id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('employer', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('basic_wage', sa.Numeric(12, 2), nullable=True),
        sa.Column('housing_allowance', sa.Numeric(12, 2), nullable=True),
        sa.Column('other_allowance', sa.Numeric(12, 2), nullable=True),
        sa.Column('full_wage', sa.Numeric(12, 2), nullable=True),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('employment_id'),
        sa.ForeignKeyConstraint(['employee_id'], ['wathq.employees.employee_id'], ondelete='CASCADE'),
        schema='wathq'
    )
    
    # Create index on employee_id for faster joins
    op.create_index('ix_wathq_employment_details_employee_id', 'employment_details', ['employee_id'], schema='wathq')


def downgrade():
    # Drop tables in reverse order (child tables first)
    op.drop_index('ix_wathq_employment_details_employee_id', table_name='employment_details', schema='wathq')
    op.drop_table('employment_details', schema='wathq')
    
    op.drop_index('ix_wathq_employees_nationality', table_name='employees', schema='wathq')
    op.drop_index('ix_wathq_employees_name', table_name='employees', schema='wathq')
    op.drop_table('employees', schema='wathq')
