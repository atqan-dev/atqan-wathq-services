"""Add TOTP fields to management_users table

Revision ID: add_totp_fields
Revises: 20251019_add_pdf_templates
Create Date: 2025-01-01 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_totp_fields"
down_revision: Union[str, None] = "20251019_add_pdf_templates"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add TOTP-related columns to management_users table."""
    # Add TOTP columns
    op.add_column(
        "management_users",
        sa.Column("totp_enabled", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "management_users", sa.Column("totp_secret", sa.Text(), nullable=True)
    )
    op.add_column(
        "management_users", sa.Column("totp_backup_codes", sa.JSON(), nullable=True)
    )
    op.add_column(
        "management_users",
        sa.Column("totp_verified_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "management_users",
        sa.Column("totp_last_used_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "management_users",
        sa.Column(
            "totp_failed_attempts", sa.Integer(), nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "management_users",
        sa.Column("totp_locked_until", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Remove TOTP-related columns from management_users table."""
    op.drop_column("management_users", "totp_locked_until")
    op.drop_column("management_users", "totp_failed_attempts")
    op.drop_column("management_users", "totp_last_used_at")
    op.drop_column("management_users", "totp_verified_at")
    op.drop_column("management_users", "totp_backup_codes")
    op.drop_column("management_users", "totp_secret")
    op.drop_column("management_users", "totp_enabled")
