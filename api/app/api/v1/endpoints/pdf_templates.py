"""
PDF Template management endpoints with GrapesJS integration.
"""

from typing import Any, List, Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import pdf_template, pdf_template_version, generated_pdf
from app.models import ManagementUser
from app.schemas import pdf_template as schemas
from app.services.pdf_generator import pdf_generator

router = APIRouter()


@router.get("/templates", response_model=schemas.PdfTemplateListResponse)
def list_templates(
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_public: Optional[bool] = None,
    search: Optional[str] = None,
) -> Any:
    """
    List PDF templates with filters and pagination.
    """
    templates, total = pdf_template.get_multi_with_filters(
        db,
        skip=skip,
        limit=limit,
        category=category,
        is_active=is_active,
        is_public=is_public,
        search=search,
    )

    # Convert to list response
    template_list = []
    for template in templates:
        template_data = schemas.PdfTemplateList.model_validate(template)
        template_data.creator_name = (
            f"{template.creator.first_name} {template.creator.last_name}"
            if template.creator
            else None
        )
        template_list.append(template_data)

    return {
        "templates": template_list,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
    }


@router.post("/templates", response_model=schemas.PdfTemplate, status_code=status.HTTP_201_CREATED)
def create_template(
    *,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(deps.get_current_active_user),
    template_in: schemas.PdfTemplateCreate,
) -> Any:
    """
    Create new PDF template.
    """
    # Check if slug already exists
    existing = pdf_template.get_by_slug(db, slug=template_in.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template with this slug already exists",
        )

    template = pdf_template.create_with_creator(
        db, obj_in=template_in, creator_id=current_user.id
    )

    return template


@router.get("/templates/{template_id}", response_model=schemas.PdfTemplateDetail)
def get_template(
    template_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get PDF template by ID with details.
    """
    template = pdf_template.get(db, id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    # Get version count and latest version
    versions, version_count = pdf_template_version.get_by_template(
        db, template_id=template_id, skip=0, limit=1
    )
    latest_version = versions[0] if versions else None

    # Build response
    template_data = schemas.PdfTemplateDetail.model_validate(template)
    template_data.creator_name = (
        f"{template.creator.first_name} {template.creator.last_name}"
        if template.creator
        else None
    )
    template_data.tenant_name = template.tenant.name if template.tenant else None
    template_data.version_count = version_count
    template_data.latest_version = (
        latest_version.version_number if latest_version else None
    )

    return template_data


@router.put("/templates/{template_id}", response_model=schemas.PdfTemplate)
def update_template(
    template_id: UUID,
    template_in: schemas.PdfTemplateUpdate,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(deps.get_current_active_user),
    create_version: bool = Query(True, description="Create version on update"),
) -> Any:
    """
    Update PDF template.
    """
    template = pdf_template.get(db, id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    # Check slug uniqueness if updating slug
    if template_in.slug and template_in.slug != template.slug:
        existing = pdf_template.get_by_slug(db, slug=template_in.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Template with this slug already exists",
            )

    updated_template = pdf_template.update_template(
        db,
        db_obj=template,
        obj_in=template_in,
        creator_id=current_user.id,
        create_version=create_version,
    )

    return updated_template


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(deps.get_current_active_user),
) -> None:
    """
    Delete PDF template.
    """
    template = pdf_template.get(db, id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    db.delete(template)
    db.commit()


@router.post("/templates/{template_id}/duplicate", response_model=schemas.PdfTemplate)
def duplicate_template(
    template_id: UUID,
    duplicate_req: schemas.TemplateDuplicateRequest,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(deps.get_current_active_user),
) -> Any:
    """
    Duplicate an existing template.
    """
    # Check if new slug already exists
    existing = pdf_template.get_by_slug(db, slug=duplicate_req.new_slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template with this slug already exists",
        )

    duplicated = pdf_template.duplicate(
        db,
        template_id=template_id,
        new_name=duplicate_req.new_name,
        new_slug=duplicate_req.new_slug,
        creator_id=current_user.id,
        include_versions=duplicate_req.include_versions,
    )

    if not duplicated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    return duplicated


@router.get("/templates/{template_id}/versions", response_model=schemas.PdfTemplateVersionListResponse)
def list_template_versions(
    template_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> Any:
    """
    List versions of a template.
    """
    template = pdf_template.get(db, id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    versions, total = pdf_template_version.get_by_template(
        db, template_id=template_id, skip=skip, limit=limit
    )

    # Convert to list response
    version_list = []
    for version in versions:
        version_data = schemas.PdfTemplateVersionList.model_validate(version)
        version_data.creator_name = (
            f"{version.creator.first_name} {version.creator.last_name}"
            if version.creator
            else None
        )
        version_list.append(version_data)

    return {"versions": version_list, "total": total}


@router.get("/templates/{template_id}/versions/{version_number}", response_model=schemas.PdfTemplateVersion)
def get_template_version(
    template_id: UUID,
    version_number: int,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get specific version of a template.
    """
    version = pdf_template_version.get_version_by_number(
        db, template_id=template_id, version_number=version_number
    )

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found",
        )

    version_data = schemas.PdfTemplateVersion.model_validate(version)
    version_data.creator_name = (
        f"{version.creator.first_name} {version.creator.last_name}"
        if version.creator
        else None
    )

    return version_data


@router.post("/templates/{template_id}/generate", response_model=schemas.GeneratedPdfResponse)
def generate_pdf_from_template(
    template_id: UUID,
    generate_req: schemas.GeneratePdfRequest,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate PDF from template with provided data.
    """
    template = pdf_template.get(db, id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    # Get version if specified
    version = None
    if generate_req.use_version:
        version = pdf_template_version.get_version_by_number(
            db, template_id=template_id, version_number=generate_req.use_version
        )
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Version not found",
            )

    # Use version or current template
    html_content = version.grapesjs_html if version else template.grapesjs_html
    css_content = version.grapesjs_css if version else template.grapesjs_css

    # Generate PDF
    import time
    start_time = time.time()

    try:
        file_path, file_size, pdf_bytes = pdf_generator.generate_pdf(
            html_content=html_content,
            css_content=css_content,
            data=generate_req.data,
            filename=generate_req.filename,
            page_size=template.page_size,
            page_orientation=template.page_orientation,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}",
        )

    generation_time = int((time.time() - start_time) * 1000)  # milliseconds

    # Create generated PDF record
    pdf_create = schemas.GeneratedPdfCreate(
        template_id=template_id,
        template_version_id=version.id if version else None,
        filename=generate_req.filename or file_path.split("/")[-1],
        file_path=file_path,
        file_size=file_size,
        input_data=generate_req.data,
        generation_time=generation_time,
        tenant_id=template.tenant_id,
    )

    generated = generated_pdf.create_with_generator(
        db, obj_in=pdf_create, generator_id=current_user.id
    )

    # Increment template usage
    pdf_template.increment_usage(db, template_id=template_id)

    # Build download URL (adjust based on your file serving setup)
    download_url = f"/api/v1/pdf-templates/downloads/{generated.id}"

    return {
        "pdf": generated,
        "download_url": download_url,
        "expires_at": generated.expires_at,
    }


@router.get("/downloads/{pdf_id}")
def download_generated_pdf(
    pdf_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(deps.get_current_active_user),
) -> Response:
    """
    Download a generated PDF file.
    """
    pdf = generated_pdf.get(db, id=pdf_id)
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found",
        )

    # Check file exists
    from pathlib import Path

    file_path = Path(pdf.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not found on disk",
        )

    # Increment download count
    generated_pdf.increment_download(db, pdf_id=pdf_id)

    # Read and return file
    with open(file_path, "rb") as f:
        pdf_bytes = f.read()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{pdf.filename}"'
        },
    )


@router.get("/generated", response_model=schemas.GeneratedPdfListResponse)
def list_generated_pdfs(
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    template_id: Optional[UUID] = None,
) -> Any:
    """
    List generated PDFs.
    """
    if template_id:
        pdfs, total = generated_pdf.get_multi_by_template(
            db, template_id=template_id, skip=skip, limit=limit
        )
    else:
        pdfs, total = generated_pdf.get_multi_by_user(
            db, user_id=current_user.id, skip=skip, limit=limit
        )

    # Convert to list response
    pdf_list = []
    for pdf_item in pdfs:
        pdf_data = schemas.GeneratedPdfList.model_validate(pdf_item)
        pdf_data.template_name = pdf_item.template.name if pdf_item.template else "Unknown"
        pdf_list.append(pdf_data)

    return {
        "pdfs": pdf_list,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
    }


@router.get("/categories", response_model=List[str])
def list_categories(
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all template categories.
    """
    return pdf_template.get_categories(db)


@router.put("/templates/{template_id}/data-mapping")
def update_data_mapping(
    template_id: UUID,
    mapping_req: schemas.TemplateDataMappingRequest,
    db: Session = Depends(deps.get_db),
    current_user: ManagementUser = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update template data mapping configuration.
    """
    template = pdf_template.get(db, id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    template.data_mapping = mapping_req.data_mapping
    if mapping_req.sample_data:
        template.sample_data = mapping_req.sample_data

    db.commit()
    db.refresh(template)

    return {"message": "Data mapping updated successfully"}
