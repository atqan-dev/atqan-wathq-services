"""
Pydantic schemas for PDF template operations with GrapesJS integration.
"""

from datetime import datetime
from uuid import UUID
from typing import Any, Dict, List

from pydantic import BaseModel, Field


# PDF Template schemas
class PdfTemplateBase(BaseModel):
    """Base schema for PDF templates."""
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    category: str | None = "general"
    is_active: bool | None = True
    is_public: bool | None = False
    page_size: str | None = "A4"
    page_orientation: str | None = "portrait"


class GrapesJsData(BaseModel):
    """Schema for GrapesJS editor data."""
    components: List[Dict[str, Any]] = Field(default_factory=list)
    styles: List[Dict[str, Any]] = Field(default_factory=list)
    assets: List[Dict[str, Any]] = Field(default_factory=list)
    pages: List[Dict[str, Any]] = Field(default_factory=list)


class PdfTemplateCreate(BaseModel):
    """Schema for creating a PDF template."""
    name: str
    slug: str
    description: str | None = None
    grapesjs_data: Dict[str, Any]
    grapesjs_html: str
    grapesjs_css: str | None = None
    category: str = "general"
    thumbnail: str | None = None
    data_mapping: Dict[str, Any] | None = None
    sample_data: Dict[str, Any] | None = None
    is_public: bool = False
    page_size: str = "A4"
    page_orientation: str = "portrait"
    tenant_id: int | None = None


class PdfTemplateUpdate(BaseModel):
    """Schema for updating a PDF template."""
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    grapesjs_data: Dict[str, Any] | None = None
    grapesjs_html: str | None = None
    grapesjs_css: str | None = None
    category: str | None = None
    thumbnail: str | None = None
    data_mapping: Dict[str, Any] | None = None
    sample_data: Dict[str, Any] | None = None
    is_active: bool | None = None
    is_public: bool | None = None
    page_size: str | None = None
    page_orientation: str | None = None


class PdfTemplateInDBBase(PdfTemplateBase):
    """Base schema for PDF template in database."""
    id: UUID
    grapesjs_data: Dict[str, Any]
    grapesjs_html: str
    grapesjs_css: str | None = None
    thumbnail: str | None = None
    data_mapping: Dict[str, Any] | None = None
    sample_data: Dict[str, Any] | None = None
    created_by: int
    tenant_id: int | None = None
    created_at: datetime
    updated_at: datetime | None = None
    last_used_at: datetime | None = None
    usage_count: int = 0

    class Config:
        from_attributes = True


class PdfTemplate(PdfTemplateInDBBase):
    """Schema for PDF template response."""
    pass


class PdfTemplateDetail(PdfTemplateInDBBase):
    """Detailed schema for PDF template with relationships."""
    creator_name: str | None = None
    tenant_name: str | None = None
    version_count: int = 0
    latest_version: int | None = None


class PdfTemplateList(BaseModel):
    """Schema for listing PDF templates."""
    id: UUID
    name: str
    slug: str
    description: str | None = None
    category: str
    thumbnail: str | None = None
    is_active: bool
    is_public: bool
    created_at: datetime
    updated_at: datetime | None = None
    usage_count: int
    creator_name: str | None = None

    class Config:
        from_attributes = True


# PDF Template Version schemas
class PdfTemplateVersionCreate(BaseModel):
    """Schema for creating a template version."""
    version_name: str | None = None
    change_description: str | None = None


class PdfTemplateVersion(BaseModel):
    """Schema for PDF template version response."""
    id: UUID
    template_id: UUID
    version_number: int
    version_name: str | None = None
    grapesjs_data: Dict[str, Any]
    grapesjs_html: str
    grapesjs_css: str | None = None
    data_mapping: Dict[str, Any] | None = None
    change_description: str | None = None
    created_by: int
    created_at: datetime
    creator_name: str | None = None

    class Config:
        from_attributes = True


class PdfTemplateVersionList(BaseModel):
    """Schema for listing template versions."""
    id: UUID
    version_number: int
    version_name: str | None = None
    change_description: str | None = None
    created_by: int
    created_at: datetime
    creator_name: str | None = None

    class Config:
        from_attributes = True


# Generated PDF schemas
class GeneratePdfRequest(BaseModel):
    """Schema for PDF generation request."""
    data: Dict[str, Any]
    filename: str | None = None
    use_version: int | None = None  # Specific version number
    expires_in_days: int | None = 30


class GeneratedPdfCreate(BaseModel):
    """Schema for creating a generated PDF record."""
    template_id: UUID
    template_version_id: UUID | None = None
    filename: str
    file_path: str
    file_size: int | None = None
    input_data: Dict[str, Any]
    generation_time: int | None = None
    tenant_id: int | None = None
    is_public: bool = False


class GeneratedPdf(BaseModel):
    """Schema for generated PDF response."""
    id: UUID
    template_id: UUID
    template_version_id: UUID | None = None
    filename: str
    file_path: str
    file_size: int | None = None
    input_data: Dict[str, Any]
    generation_time: int | None = None
    generated_by: int
    tenant_id: int | None = None
    is_public: bool
    download_count: int
    created_at: datetime
    expires_at: datetime | None = None
    last_accessed_at: datetime | None = None

    class Config:
        from_attributes = True


class GeneratedPdfResponse(BaseModel):
    """Schema for PDF generation response."""
    pdf: GeneratedPdf
    download_url: str
    expires_at: datetime | None = None


class GeneratedPdfList(BaseModel):
    """Schema for listing generated PDFs."""
    id: UUID
    template_id: UUID
    template_name: str
    filename: str
    file_size: int | None = None
    download_count: int
    created_at: datetime
    expires_at: datetime | None = None

    class Config:
        from_attributes = True


# Response schemas
class PdfTemplateListResponse(BaseModel):
    """Response schema for template list."""
    templates: List[PdfTemplateList]
    total: int
    page: int
    page_size: int


class PdfTemplateVersionListResponse(BaseModel):
    """Response schema for version list."""
    versions: List[PdfTemplateVersionList]
    total: int


class GeneratedPdfListResponse(BaseModel):
    """Response schema for generated PDF list."""
    pdfs: List[GeneratedPdfList]
    total: int
    page: int
    page_size: int


class TemplateDataMappingRequest(BaseModel):
    """Schema for updating template data mapping."""
    data_mapping: Dict[str, Any]
    sample_data: Dict[str, Any] | None = None


class TemplateDuplicateRequest(BaseModel):
    """Schema for duplicating a template."""
    new_name: str
    new_slug: str
    include_versions: bool = False
