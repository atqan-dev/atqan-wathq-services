"""
WATHQ PDF Export API endpoints
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core.config import settings
from app.core.wathq_utils import get_tenant_wathq_key_by_slug
from app.models.wathq_pdf_data import WathqPDFData
from app.services.wathq_pdf_service import pdf_service
from app.wathq.commercial_registration.client import WathqClient

router = APIRouter()


def get_wathq_client_for_user(
    service_slug: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User | models.ManagementUser = Depends(
        deps.get_current_active_user_or_management
    ),
) -> WathqClient:
    """Get Wathq client instance for current user"""

    if isinstance(current_user, models.ManagementUser):
        # Management user - use global API key
        return WathqClient(
            api_key=settings.WATHQ_API_KEY, db=db, tenant_id=None, user_id=None
        )
    else:
        # Tenant user - use tenant-specific API key
        api_key = get_tenant_wathq_key_by_slug(
            db=db, tenant_id=current_user.tenant_id, service_slug=service_slug
        )

        # Fallback to system API key if tenant doesn't have specific key
        if not api_key:
            api_key = settings.WATHQ_API_KEY

        return WathqClient(
            api_key=api_key,
            db=db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
        )


@router.get("/commercial-registration/{cr_id}/pdf")
async def export_commercial_registration_pdf(
    cr_id: str,
    language: str = Query("ar", regex="^(ar|en)$"),
    template: Optional[str] = Query(None, description="Custom template name"),
    include_full_info: bool = Query(True, description="Include full CR info"),
    include_owners: bool = Query(False, description="Include owners info"),
    include_managers: bool = Query(False, description="Include managers info"),
    include_branches: bool = Query(False, description="Include branches info"),
    db: Session = Depends(deps.get_db),
    current_user: models.User | models.ManagementUser = Depends(
        deps.get_current_active_user_or_management
    ),
) -> Response:
    """
    Export Commercial Registration data as PDF
    """
    try:
        client = get_wathq_client_for_user("commercial-registration", db, current_user)

        # Fetch CR data
        if include_full_info:
            cr_data = await client.get_full_info(cr_id, language)
        else:
            cr_data = await client.get_basic_info(cr_id, language)

        # Fetch additional data if requested
        additional_sections = []

        if include_owners:
            try:
                owners_data = await client.get_owners(cr_id, language)
                if owners_data.get("owners"):
                    owners_content = pdf_service.create_table_from_wathq_data(
                        {"owners": owners_data["owners"]},
                        {"headers": ["الاسم", "الجنسية", "رقم الهوية", "النسبة"]},
                    )
                    additional_sections.append(
                        {
                            "title": "المالكون",
                            "content": f"<table class='data-table'>{owners_content[1]}</table>",
                            "page_break": True,
                        }
                    )
            except Exception:
                pass  # Continue if owners data not available

        if include_managers:
            try:
                managers_data = await client.get_managers(cr_id, language)
                if managers_data.get("managers"):
                    managers_content = pdf_service.create_table_from_wathq_data(
                        {"managers": managers_data["managers"]},
                        {"headers": ["الاسم", "المنصب", "رقم الهوية"]},
                    )
                    additional_sections.append(
                        {
                            "title": "المديرون",
                            "content": f"<table class='data-table'>{managers_content[1]}</table>",
                            "page_break": True,
                        }
                    )
            except Exception:
                pass

        if include_branches:
            try:
                branches_data = await client.get_branches(cr_id, language)
                if branches_data.get("branches"):
                    branches_content = pdf_service.create_table_from_wathq_data(
                        {"branches": branches_data["branches"]},
                        {"headers": ["اسم الفرع", "العنوان", "النشاط"]},
                    )
                    additional_sections.append(
                        {
                            "title": "الفروع",
                            "content": f"<table class='data-table'>{branches_content[1]}</table>",
                            "page_break": True,
                        }
                    )
            except Exception:
                pass

        # Create PDF data model
        pdf_data = pdf_service.create_commercial_registration_pdf(
            cr_data=cr_data, additional_content=None
        )

        # Add additional sections if any
        if additional_sections:
            if not pdf_data.sections:
                pdf_data.sections = []
            pdf_data.sections.extend(
                [
                    {
                        "title": section["title"],
                        "content": section["content"],
                        "page_break": section.get("page_break", False),
                    }
                    for section in additional_sections
                ]
            )

        # Generate and return PDF
        filename = f"commercial_registration_{cr_id}.pdf"
        return pdf_service.generate_pdf_response(
            pdf_data, filename=filename, template_name=template
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate CR PDF: {str(e)}"
        )


@router.post("/custom-document/pdf")
async def create_custom_pdf(
    pdf_data: WathqPDFData,
    template: Optional[str] = Query(None, description="Custom template name"),
    current_user: models.User | models.ManagementUser = Depends(
        deps.get_current_active_user_or_management
    ),
) -> Response:
    """
    Create custom PDF document from provided data
    """
    try:
        filename = f"{pdf_data.document_title or 'document'}.pdf"
        return pdf_service.generate_pdf_response(
            pdf_data, filename=filename, template_name=template
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate custom PDF: {str(e)}"
        )


@router.get("/preview/commercial-registration/{cr_id}")
async def preview_commercial_registration_html(
    cr_id: str,
    language: str = Query("ar", regex="^(ar|en)$"),
    template: Optional[str] = Query(None, description="Custom template name"),
    db: Session = Depends(deps.get_db),
    current_user: models.User | models.ManagementUser = Depends(
        deps.get_current_active_user_or_management
    ),
) -> Response:
    """
    Preview Commercial Registration HTML before PDF generation
    """
    try:
        client = get_wathq_client_for_user("commercial-registration", db, current_user)

        # Fetch CR data
        cr_data = await client.get_basic_info(cr_id, language)

        # Create PDF data model
        pdf_data = pdf_service.create_commercial_registration_pdf(cr_data)

        # Generate HTML preview
        html_content = pdf_service.preview_html(pdf_data, template_name=template)

        return Response(content=html_content, media_type="text/html")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate preview: {str(e)}"
        )


@router.post("/preview/custom-document")
async def preview_custom_document_html(
    pdf_data: WathqPDFData,
    template: Optional[str] = Query(None, description="Custom template name"),
    current_user: models.User | models.ManagementUser = Depends(
        deps.get_current_active_user_or_management
    ),
) -> Response:
    """
    Preview custom document HTML before PDF generation
    """
    try:
        html_content = pdf_service.preview_html(pdf_data, template_name=template)
        return Response(content=html_content, media_type="text/html")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate preview: {str(e)}"
        )


@router.post("/wathq-data/{service_type}/{identifier}/pdf")
async def export_wathq_data_pdf(
    service_type: str,
    identifier: str,
    language: str = Query("ar", regex="^(ar|en)$"),
    template: Optional[str] = Query(None, description="Custom template name"),
    custom_title: Optional[str] = Query(None, description="Custom document title"),
    db: Session = Depends(deps.get_db),
    current_user: models.User | models.ManagementUser = Depends(
        deps.get_current_active_user_or_management
    ),
) -> Response:
    """
    Generic endpoint to export any WATHQ service data as PDF

    Supported service types:
    - commercial-registration
    - real-estate
    - employee
    - attorney
    - company-contract
    """
    try:
        # This would need to be expanded based on available WATHQ services
        if service_type == "commercial-registration":
            return await export_commercial_registration_pdf(
                cr_id=identifier,
                language=language,
                template=template,
                db=db,
                current_user=current_user,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Service type '{service_type}' not supported for PDF export",
            )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to export {service_type} PDF: {str(e)}"
        )


@router.get("/templates")
async def list_available_templates(
    current_user: models.User | models.ManagementUser = Depends(
        deps.get_current_active_user_or_management
    ),
) -> Dict[str, Any]:
    """
    List available PDF templates
    """
    try:
        templates_dir = pdf_service.templates_dir
        templates = []

        if templates_dir.exists():
            for template_file in templates_dir.glob("*.html"):
                templates.append(
                    {
                        "name": template_file.stem,
                        "filename": template_file.name,
                        "path": str(template_file),
                    }
                )

        return {
            "templates": templates,
            "default_template": pdf_service.default_template,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list templates: {str(e)}"
        )
