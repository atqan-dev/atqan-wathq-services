"""create cr_requests table

Revision ID: 20250111_cr_requests
Revises: 20250108_employees
Create Date: 2025-01-11 10:57:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
import uuid

# revision identifiers, used by Alembic.
revision = '20250111_cr_requests'
down_revision = '20250108_employees'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'cr_requests',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('cr_number', sa.String(50), nullable=False),
        sa.Column('language', sa.String(10), nullable=False),
        sa.Column('response', JSONB, nullable=True),
        sa.Column('status_number', sa.Integer, nullable=True),
        sa.Column('status_text', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.Column('updated_by', sa.String(100), nullable=True),
    )
    
    # Create indexes for better query performance
    op.create_index('ix_cr_requests_cr_number', 'cr_requests', ['cr_number'])
    op.create_index('ix_cr_requests_created_at', 'cr_requests', ['created_at'])
    op.create_index('ix_cr_requests_status_number', 'cr_requests', ['status_number'])


def downgrade():
    op.drop_index('ix_cr_requests_status_number', table_name='cr_requests')
    op.drop_index('ix_cr_requests_created_at', table_name='cr_requests')
    op.drop_index('ix_cr_requests_cr_number', table_name='cr_requests')
    op.drop_table('cr_requests')
