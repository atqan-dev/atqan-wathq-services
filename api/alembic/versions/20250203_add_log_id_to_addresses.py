"""Add log_id and fetched_at columns to addresses table and change primary key

Revision ID: 20250203_add_log_id_addr
Revises: 20250203_add_log_id_deeds
Create Date: 2025-02-03

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20250203_add_log_id_addr"
down_revision = "20250203_add_log_id_deeds"
branch_labels = None
depends_on = None


def upgrade():
    # Drop the old primary key constraint on pk_address_id
    op.drop_constraint("addresses_pkey", "addresses", schema="wathq", type_="primary")

    # Create sequence for id
    op.execute("CREATE SEQUENCE IF NOT EXISTS wathq.addresses_id_seq")

    # Add new id column as nullable first
    op.add_column(
        "addresses", sa.Column("id", sa.Integer(), nullable=True), schema="wathq"
    )

    # Populate id for existing rows using the sequence
    op.execute(
        "UPDATE wathq.addresses SET id = nextval('wathq.addresses_id_seq') WHERE id IS NULL"
    )

    # Now make id NOT NULL
    op.alter_column("addresses", "id", nullable=False, schema="wathq")

    # Set default for future inserts
    op.execute(
        "ALTER TABLE wathq.addresses ALTER COLUMN id SET DEFAULT nextval('wathq.addresses_id_seq')"
    )

    # Add primary key constraint on id
    op.create_primary_key("addresses_pkey", "addresses", ["id"], schema="wathq")

    # Create index on id
    op.create_index("ix_wathq_addresses_id", "addresses", ["id"], schema="wathq")

    # Add log_id column with foreign key to wathq_call_logs
    op.add_column(
        "addresses",
        sa.Column("log_id", postgresql.UUID(as_uuid=True), nullable=True),
        schema="wathq",
    )

    # Add fetched_at column
    op.add_column(
        "addresses",
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=True),
        schema="wathq",
    )

    # Create index on log_id for faster lookups
    op.create_index(
        "ix_wathq_addresses_log_id", "addresses", ["log_id"], schema="wathq"
    )

    # Add foreign key constraint to wathq_call_logs
    op.create_foreign_key(
        "fk_addresses_log_id",
        "addresses",
        "wathq_call_logs",
        ["log_id"],
        ["id"],
        source_schema="wathq",
        referent_schema="public",
    )


def downgrade():
    # Drop foreign key constraint
    op.drop_constraint(
        "fk_addresses_log_id", "addresses", schema="wathq", type_="foreignkey"
    )

    # Drop index on log_id
    op.drop_index("ix_wathq_addresses_log_id", table_name="addresses", schema="wathq")

    # Drop columns
    op.drop_column("addresses", "fetched_at", schema="wathq")
    op.drop_column("addresses", "log_id", schema="wathq")

    # Drop index on id
    op.drop_index("ix_wathq_addresses_id", table_name="addresses", schema="wathq")

    # Drop primary key on id
    op.drop_constraint("addresses_pkey", "addresses", schema="wathq", type_="primary")

    # Drop id column
    op.drop_column("addresses", "id", schema="wathq")

    # Drop sequence
    op.execute("DROP SEQUENCE IF EXISTS wathq.addresses_id_seq")

    # Restore pk_address_id as primary key
    op.create_primary_key(
        "addresses_pkey", "addresses", ["pk_address_id"], schema="wathq"
    )
