"""add_notifications_table

Revision ID: add_notifications_table
Revises: add_wathq_offline_data
Create Date: 2025-01-01 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_notifications_table"
down_revision = "add_wathq_offline_data"
branch_labels = None
depends_on = None


def upgrade():
    # Create notifications table
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "type",
            sa.Enum("info", "success", "warning", "error", name="notificationtype"),
            nullable=False,
        ),
        sa.Column(
            "category",
            sa.Enum(
                "system",
                "user_action",
                "security",
                "wathq_service",
                "tenant",
                "deployment",
                name="notificationcategory",
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("unread", "read", name="notificationstatus"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("management_user_id", sa.Integer(), nullable=True),
        sa.Column("action_url", sa.String(length=500), nullable=True),
        sa.Column("extra_data", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["management_user_id"],
            ["management_users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index(op.f("ix_notifications_id"), "notifications", ["id"], unique=False)
    op.create_index(
        op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_notifications_tenant_id"), "notifications", ["tenant_id"], unique=False
    )
    op.create_index(
        op.f("ix_notifications_management_user_id"),
        "notifications",
        ["management_user_id"],
        unique=False,
    )


def downgrade():
    # Drop indexes
    op.drop_index(
        op.f("ix_notifications_management_user_id"), table_name="notifications"
    )
    op.drop_index(op.f("ix_notifications_tenant_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_id"), table_name="notifications")

    # Drop table
    op.drop_table("notifications")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS notificationtype")
    op.execute("DROP TYPE IF EXISTS notificationcategory")
    op.execute("DROP TYPE IF EXISTS notificationstatus")
