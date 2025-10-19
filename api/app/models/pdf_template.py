"""
PDF Template database models for GrapesJS integration.
"""

import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class PdfTemplate(Base):
    """
    PDF Template model for managing GrapesJS templates.
    """

    __tablename__ = "pdf_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # GrapesJS specific fields
    grapesjs_data = Column(JSON, nullable=False)  # Full GrapesJS editor state
    grapesjs_html = Column(Text, nullable=False)  # Compiled HTML from GrapesJS
    grapesjs_css = Column(Text, nullable=True)  # Compiled CSS from GrapesJS
    
    # Template metadata
    category = Column(String, nullable=True, default="general")  # 'certificate', 'invoice', 'report', etc.
    thumbnail = Column(Text, nullable=True)  # Base64 or URL to template thumbnail
    
    # Data mapping configuration
    data_mapping = Column(JSON, nullable=True)  # Maps JSON fields to template variables
    sample_data = Column(JSON, nullable=True)  # Sample data for preview
    
    # Template settings
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)  # Can be used by all tenants
    page_size = Column(String, default="A4")  # A4, Letter, etc.
    page_orientation = Column(String, default="portrait")  # portrait or landscape
    
    # Ownership and access control
    created_by = Column(Integer, ForeignKey("management_users.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)  # Null for global templates
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    
    # Relationships
    creator = relationship("ManagementUser", foreign_keys=[created_by])
    tenant = relationship("Tenant", foreign_keys=[tenant_id])
    versions = relationship("PdfTemplateVersion", back_populates="template", cascade="all, delete-orphan")
    generated_pdfs = relationship("GeneratedPdf", back_populates="template", cascade="all, delete-orphan")


class PdfTemplateVersion(Base):
    """
    PDF Template Version model for version control.
    """

    __tablename__ = "pdf_template_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("pdf_templates.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    version_name = Column(String, nullable=True)
    
    # Versioned content
    grapesjs_data = Column(JSON, nullable=False)
    grapesjs_html = Column(Text, nullable=False)
    grapesjs_css = Column(Text, nullable=True)
    data_mapping = Column(JSON, nullable=True)
    
    # Version metadata
    change_description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("management_users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    template = relationship("PdfTemplate", back_populates="versions")
    creator = relationship("ManagementUser", foreign_keys=[created_by])


class GeneratedPdf(Base):
    """
    Generated PDF model for tracking PDF generation history.
    """

    __tablename__ = "generated_pdfs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("pdf_templates.id"), nullable=False)
    template_version_id = Column(UUID(as_uuid=True), ForeignKey("pdf_template_versions.id"), nullable=True)
    
    # PDF metadata
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # Storage path or URL
    file_size = Column(Integer, nullable=True)  # Size in bytes
    
    # Generation data
    input_data = Column(JSON, nullable=False)  # Data used to generate the PDF
    generation_time = Column(Integer, nullable=True)  # Time in milliseconds
    
    # Access control
    generated_by = Column(Integer, ForeignKey("management_users.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    
    # Status and access
    is_public = Column(Boolean, default=False)
    download_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    template = relationship("PdfTemplate", back_populates="generated_pdfs")
    template_version = relationship("PdfTemplateVersion", foreign_keys=[template_version_id])
    generator = relationship("ManagementUser", foreign_keys=[generated_by])
    tenant = relationship("Tenant", foreign_keys=[tenant_id])
