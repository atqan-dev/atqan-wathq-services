"""add pdf templates

Revision ID: 20251019_add_pdf_templates
Revises: 20251010_004500_add_api_request_counters_and_summaries
Create Date: 2025-10-19 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251019_add_pdf_templates'
down_revision = 'add_logo_name_ar'
branch_labels = None
depends_on = None


def upgrade():
    # Create pdf_templates table
    op.create_table(
        'pdf_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), unique=True, nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('grapesjs_data', postgresql.JSON(), nullable=False),
        sa.Column('grapesjs_html', sa.Text(), nullable=False),
        sa.Column('grapesjs_css', sa.Text(), nullable=True),
        sa.Column('category', sa.String(), nullable=True, server_default='general'),
        sa.Column('thumbnail', sa.Text(), nullable=True),
        sa.Column('data_mapping', postgresql.JSON(), nullable=True),
        sa.Column('sample_data', postgresql.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_public', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('page_size', sa.String(), nullable=True, server_default='A4'),
        sa.Column('page_orientation', sa.String(), nullable=True, server_default='portrait'),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True, server_default='0'),
        sa.ForeignKeyConstraint(['created_by'], ['management_users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
    )
    op.create_index(op.f('ix_pdf_templates_id'), 'pdf_templates', ['id'], unique=False)
    op.create_index(op.f('ix_pdf_templates_name'), 'pdf_templates', ['name'], unique=False)
    op.create_index(op.f('ix_pdf_templates_slug'), 'pdf_templates', ['slug'], unique=True)

    # Create pdf_template_versions table
    op.create_table(
        'pdf_template_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('version_name', sa.String(), nullable=True),
        sa.Column('grapesjs_data', postgresql.JSON(), nullable=False),
        sa.Column('grapesjs_html', sa.Text(), nullable=False),
        sa.Column('grapesjs_css', sa.Text(), nullable=True),
        sa.Column('data_mapping', postgresql.JSON(), nullable=True),
        sa.Column('change_description', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['template_id'], ['pdf_templates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['management_users.id'], ),
    )
    op.create_index(op.f('ix_pdf_template_versions_id'), 'pdf_template_versions', ['id'], unique=False)

    # Create generated_pdfs table
    op.create_table(
        'generated_pdfs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_version_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('input_data', postgresql.JSON(), nullable=False),
        sa.Column('generation_time', sa.Integer(), nullable=True),
        sa.Column('generated_by', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('download_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], ['pdf_templates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['template_version_id'], ['pdf_template_versions.id'], ),
        sa.ForeignKeyConstraint(['generated_by'], ['management_users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
    )
    op.create_index(op.f('ix_generated_pdfs_id'), 'generated_pdfs', ['id'], unique=False)


def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_generated_pdfs_id'), table_name='generated_pdfs')
    op.drop_table('generated_pdfs')
    
    op.drop_index(op.f('ix_pdf_template_versions_id'), table_name='pdf_template_versions')
    op.drop_table('pdf_template_versions')
    
    op.drop_index(op.f('ix_pdf_templates_slug'), table_name='pdf_templates')
    op.drop_index(op.f('ix_pdf_templates_name'), table_name='pdf_templates')
    op.drop_index(op.f('ix_pdf_templates_id'), table_name='pdf_templates')
    op.drop_table('pdf_templates')
