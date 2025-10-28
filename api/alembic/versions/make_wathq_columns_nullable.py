"""Make WATHQ table columns nullable for management users

Revision ID: make_wathq_nullable
Revises: add_logo_name_ar
Create Date: 2025-10-28 10:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'make_wathq_nullable'
down_revision = 'add_logo_name_ar'
branch_labels = None
depends_on = None


def upgrade():
    # Alter wathq_call_logs table
    # Make tenant_id and user_id nullable
    try:
        op.alter_column('wathq_call_logs', 'tenant_id',
                        existing_type=sa.Integer(),
                        nullable=True)
    except Exception:
        pass

    try:
        op.alter_column('wathq_call_logs', 'user_id',
                        existing_type=sa.Integer(),
                        nullable=True)
    except Exception:
        pass

    # Add foreign key and index for management_user_id if not exists
    try:
        op.create_foreign_key('fk_wathq_call_logs_management_user_id',
                              'wathq_call_logs', 'management_users',
                              ['management_user_id'], ['id'])
    except Exception:
        pass

    try:
        op.create_index(op.f('ix_wathq_call_logs_management_user_id'),
                        'wathq_call_logs', ['management_user_id'],
                        unique=False)
    except Exception:
        pass

    # Alter wathq_offline_data table
    # Make tenant_id and fetched_by nullable
    try:
        op.alter_column('wathq_offline_data', 'tenant_id',
                        existing_type=sa.Integer(),
                        nullable=True)
    except Exception:
        pass

    try:
        op.alter_column('wathq_offline_data', 'fetched_by',
                        existing_type=sa.Integer(),
                        nullable=True)
    except Exception:
        pass

    # Add foreign key and index for management_user_id if not exists
    try:
        op.create_foreign_key('fk_wathq_offline_data_management_user_id',
                              'wathq_offline_data', 'management_users',
                              ['management_user_id'], ['id'])
    except Exception:
        pass

    try:
        op.create_index(op.f('ix_wathq_offline_data_management_user_id'),
                        'wathq_offline_data', ['management_user_id'],
                        unique=False)
    except Exception:
        pass


def downgrade():
    # Drop indexes if they exist
    try:
        op.drop_index(op.f('ix_wathq_offline_data_management_user_id'),
                      table_name='wathq_offline_data')
    except Exception:
        pass

    try:
        op.drop_index(op.f('ix_wathq_call_logs_management_user_id'),
                      table_name='wathq_call_logs')
    except Exception:
        pass

    # Drop foreign keys if they exist
    try:
        op.drop_constraint('fk_wathq_offline_data_management_user_id',
                           'wathq_offline_data', type_='foreignkey')
    except Exception:
        pass

    try:
        op.drop_constraint('fk_wathq_call_logs_management_user_id',
                           'wathq_call_logs', type_='foreignkey')
    except Exception:
        pass

    # Revert nullable changes
    op.alter_column('wathq_offline_data', 'fetched_by',
                    existing_type=sa.Integer(),
                    nullable=False)
    op.alter_column('wathq_offline_data', 'tenant_id',
                    existing_type=sa.Integer(),
                    nullable=False)
    op.alter_column('wathq_call_logs', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=False)
    op.alter_column('wathq_call_logs', 'tenant_id',
                    existing_type=sa.Integer(),
                    nullable=False)
