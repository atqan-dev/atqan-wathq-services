"""Merge multiple heads

Revision ID: 2e1058b70502
Revises: 20250105_create_wathq_schema, make_wathq_nullable
Create Date: 2026-01-05 10:29:50.939406

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e1058b70502'
down_revision = ('20250105_create_wathq_schema', 'make_wathq_nullable')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
