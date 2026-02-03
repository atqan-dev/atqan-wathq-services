"""merge_corporate_contracts_log_id

Revision ID: 37526dbec8d0
Revises: 20250121_add_log_id, 20250203_add_log_id_cc
Create Date: 2026-02-03 14:49:06.457050

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37526dbec8d0'
down_revision = ('20250121_add_log_id', '20250203_add_log_id_cc')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
