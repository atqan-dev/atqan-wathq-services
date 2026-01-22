"""merge_heads

Revision ID: f4b678f7d405
Revises: 20250111_cr_requests, 20250121_cr_history
Create Date: 2026-01-21 16:18:27.304949

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4b678f7d405'
down_revision = ('20250111_cr_requests', '20250121_cr_history')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
