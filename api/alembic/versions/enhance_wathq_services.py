"""enhance services with wathq integration and permissions

Revision ID: enhance_wathq_services
Revises: 136a3a1d06df
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'enhance_wathq_services'
down_revision = '54f1bb055baf'
branch_labels = None
depends_on = None


def upgrade():
    # Create user_service_permissions table
    op.create_table('user_service_permissions',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('service_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'service_id')
    )
    
    # Modify services table
    op.add_column('services', sa.Column('slug', sa.String(), nullable=True))
    op.add_column('services', sa.Column('category', sa.String(), nullable=False, server_default='wathq'))
    op.add_column('services', sa.Column('requires_approval', sa.Boolean(), nullable=True, server_default='true'))
    
    # Change services.id to UUID
    op.execute("ALTER TABLE services ADD COLUMN new_id UUID DEFAULT gen_random_uuid()")
    op.execute("UPDATE services SET new_id = gen_random_uuid()")
    op.execute("ALTER TABLE tenant_services DROP CONSTRAINT tenant_services_service_id_fkey")
    op.execute("ALTER TABLE tenant_services ADD COLUMN new_service_id UUID")
    op.execute("UPDATE tenant_services SET new_service_id = services.new_id FROM services WHERE tenant_services.service_id = services.id")
    op.execute("ALTER TABLE services DROP COLUMN id")
    op.execute("ALTER TABLE services RENAME COLUMN new_id TO id")
    op.execute("ALTER TABLE services ADD PRIMARY KEY (id)")
    op.execute("ALTER TABLE tenant_services DROP COLUMN service_id")
    op.execute("ALTER TABLE tenant_services RENAME COLUMN new_service_id TO service_id")
    op.execute("ALTER TABLE tenant_services ALTER COLUMN service_id SET NOT NULL")
    op.execute("ALTER TABLE tenant_services ADD CONSTRAINT tenant_services_service_id_fkey FOREIGN KEY (service_id) REFERENCES services(id)")
    
    # Update services table constraints
    op.create_unique_constraint(None, 'services', ['slug'])
    op.create_index(op.f('ix_services_slug'), 'services', ['slug'], unique=False)
    
    # Modify tenant_services table
    op.add_column('tenant_services', sa.Column('is_approved', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('tenant_services', sa.Column('max_users', sa.Integer(), nullable=True, server_default='10'))
    op.add_column('tenant_services', sa.Column('usage_count', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('tenant_services', sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tenant_services', sa.Column('approved_by', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'tenant_services', 'users', ['approved_by'], ['id'])
    
    # Modify permissions table
    op.add_column('permissions', sa.Column('service_slug', sa.String(), nullable=True))
    
    # Insert WATHQ services
    services_data = [
        ('commercial-registration', 'Commercial Registration', 'WATHQ Commercial Registration Service'),
        ('real-estate', 'Real Estate', 'WATHQ Real Estate Verification Service'),
        ('employee-verification', 'Employee Verification', 'WATHQ Employee Verification Service'),
        ('company-contract', 'Company Contract', 'WATHQ Company Contract Service'),
        ('attorney-services', 'Attorney Services', 'WATHQ Attorney Services'),
        ('national-address', 'National Address', 'WATHQ National Address Service'),
    ]
    
    for slug, name, description in services_data:
        op.execute(f"""
            INSERT INTO services (id, name, slug, description, category, price, requires_approval)
            VALUES (gen_random_uuid(), '{name}', '{slug}', '{description}', 'wathq', 0.00, true)
        """)
    
    # Insert WATHQ-specific permissions
    permissions_data = [
        ('use_commercial_registration', 'Use Commercial Registration Service', 'wathq_service', 'use', 'service', 'commercial-registration'),
        ('use_real_estate', 'Use Real Estate Service', 'wathq_service', 'use', 'service', 'real-estate'),
        ('use_employee_verification', 'Use Employee Verification Service', 'wathq_service', 'use', 'service', 'employee-verification'),
        ('use_company_contract', 'Use Company Contract Service', 'wathq_service', 'use', 'service', 'company-contract'),
        ('use_attorney_services', 'Use Attorney Services', 'wathq_service', 'use', 'service', 'attorney-services'),
        ('use_national_address', 'Use National Address Service', 'wathq_service', 'use', 'service', 'national-address'),
        ('manage_tenant_services', 'Manage Tenant Services', 'tenant_service', 'manage', 'tenant', None),
        ('approve_service_requests', 'Approve Service Requests', 'tenant_service', 'approve', 'tenant', None),
        ('assign_user_services', 'Assign Services to Users', 'user_service', 'assign', 'tenant', None),
    ]
    
    for name, description, resource, action, scope, service_slug in permissions_data:
        service_slug_value = f"'{service_slug}'" if service_slug else 'NULL'
        op.execute(f"""
            INSERT INTO permissions (name, description, resource, action, scope, service_slug)
            VALUES ('{name}', '{description}', '{resource}', '{action}', '{scope}', {service_slug_value})
        """)


def downgrade():
    # Remove added columns and tables
    op.drop_table('user_service_permissions')
    op.drop_constraint(None, 'tenant_services', type_='foreignkey')
    op.drop_column('tenant_services', 'approved_by')
    op.drop_column('tenant_services', 'approved_at')
    op.drop_column('tenant_services', 'usage_count')
    op.drop_column('tenant_services', 'max_users')
    op.drop_column('tenant_services', 'is_approved')
    op.drop_column('permissions', 'service_slug')
    op.drop_index(op.f('ix_services_slug'), table_name='services')
    op.drop_constraint(None, 'services', type_='unique')
    op.drop_column('services', 'requires_approval')
    op.drop_column('services', 'category')
    op.drop_column('services', 'slug')