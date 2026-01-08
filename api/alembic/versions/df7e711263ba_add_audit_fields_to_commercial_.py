"""add_audit_fields_to_commercial_registrations

Revision ID: df7e711263ba
Revises: eb849cd4799a
Create Date: 2026-01-06 11:52:04.540807

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df7e711263ba'
down_revision = 'eb849cd4799a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add audit fields to commercial_registrations table
    op.add_column('commercial_registrations',
                  sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
                  schema='wathq')
    op.add_column('commercial_registrations',
                  sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
                  schema='wathq')
    op.add_column('commercial_registrations',
                  sa.Column('created_by', sa.Integer(), nullable=True),
                  schema='wathq')
    op.add_column('commercial_registrations',
                  sa.Column('updated_by', sa.Integer(), nullable=True),
                  schema='wathq')
    op.add_column('commercial_registrations',
                  sa.Column('request_body', sa.JSON(), nullable=True),
                  schema='wathq')


def downgrade() -> None:
    # Drop audit fields from commercial_registrations table
    op.drop_column('commercial_registrations', 'request_body', schema='wathq')
    op.drop_column('commercial_registrations', 'updated_by', schema='wathq')
    op.drop_column('commercial_registrations', 'created_by', schema='wathq')
    op.drop_column('commercial_registrations', 'updated_at', schema='wathq')
    op.drop_column('commercial_registrations', 'created_at', schema='wathq')
