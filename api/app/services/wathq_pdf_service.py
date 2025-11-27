"""
Enhanced WATHQ PDF Generation Service
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from app.models.wathq_pdf_data import (
    DocumentSection,
    InfoBox,
    InfoBoxItem,
    WathqCommercialRegistrationPDF,
    WathqPDFData,
)
from fastapi import HTTPException
from fastapi.responses import Response
from jinja2 import Environment, FileSystemLoader, Template
from utils.wcr_pdf_helpers import PDFHelper
from weasyprint import HTML


class WathqPDFService:
    """Enhanced service for generating WATHQ PDF documents"""

    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir), autoescape=True
        )
        self.default_template = "wathq-document-template.html"

    def load_template(self, template_name: Optional[str] = None) -> Template:
        """Load Jinja2 template from file"""
        template_name = template_name or self.default_template
        template_path = self.templates_dir / template_name

        if not template_path.exists():
            raise HTTPException(
                status_code=404, detail=f"Template {template_name} not found"
            )

        return self.env.get_template(template_name)

    def generate_pdf_bytes(
        self, data: WathqPDFData, template_name: Optional[str] = None
    ) -> bytes:
        """Generate PDF bytes from template and data"""
        try:
            # Load template
            template = self.load_template(template_name)

            # Render HTML
            html_content = template.render(**data.dict())

            # Generate PDF with WeasyPrint
            pdf_bytes = HTML(string=html_content, encoding="utf-8").write_pdf(
                **data.pdf_options
            )

            return pdf_bytes

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"PDF generation failed: {str(e)}"
            )

    def generate_pdf_response(
        self,
        data: WathqPDFData,
        filename: Optional[str] = None,
        template_name: Optional[str] = None,
    ) -> Response:
        """Generate PDF and return as FastAPI Response"""
        pdf_bytes = self.generate_pdf_bytes(data, template_name)

        filename = filename or f"{data.document_title}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes)),
            },
        )

    def preview_html(
        self, data: WathqPDFData, template_name: Optional[str] = None
    ) -> str:
        """Generate HTML preview without converting to PDF"""
        template = self.load_template(template_name)
        return template.render(**data.dict())

    def create_commercial_registration_pdf(
        self, cr_data: Dict[str, Any], additional_content: Optional[str] = None
    ) -> WathqCommercialRegistrationPDF:
        """Create PDF data model for Commercial Registration document"""

        # Build main content
        content_parts = []

        if cr_data.get("cr_number"):
            content_parts.append(
                PDFHelper.create_styled_paragraph(
                    f"رقم السجل التجاري: {cr_data['cr_number']}", "highlight"
                )
            )

        if cr_data.get("company_name"):
            content_parts.append(
                PDFHelper.create_styled_paragraph(
                    f"اسم الشركة: {cr_data['company_name']}", "title"
                )
            )

        # Create info boxes
        info_boxes = []

        # Company details box
        company_items = []
        if cr_data.get("legal_form"):
            company_items.append(
                InfoBoxItem(label="الشكل القانوني", value=cr_data["legal_form"])
            )
        if cr_data.get("capital"):
            company_items.append(
                InfoBoxItem(label="رأس المال", value=cr_data["capital"])
            )
        if cr_data.get("main_activity"):
            company_items.append(
                InfoBoxItem(label="النشاط الرئيسي", value=cr_data["main_activity"])
            )

        if company_items:
            info_boxes.append(InfoBox(title="تفاصيل الشركة", items=company_items))

        # Dates box
        date_items = []
        if cr_data.get("establishment_date"):
            date_items.append(
                InfoBoxItem(
                    label="تاريخ التأسيس",
                    value=PDFHelper.format_arabic_date(cr_data["establishment_date"]),
                )
            )
        if cr_data.get("expiry_date"):
            date_items.append(
                InfoBoxItem(
                    label="تاريخ الانتهاء",
                    value=PDFHelper.format_arabic_date(cr_data["expiry_date"]),
                )
            )

        if date_items:
            info_boxes.append(InfoBox(title="التواريخ المهمة", items=date_items))

        # Add additional content if provided
        if additional_content:
            content_parts.append(additional_content)

        main_content = "\n".join(content_parts)

        # Helper function to safely convert values to strings
        def safe_str(value):
            if value is None:
                return None
            if isinstance(value, str):
                return value
            if isinstance(value, dict):
                # If it's a dict, try to extract meaningful value
                if "value" in value:
                    return str(value["value"])
                elif "amount" in value:
                    return str(value["amount"])
                elif "text" in value:
                    return str(value["text"])
                else:
                    # Return a formatted representation of the dict
                    return ", ".join(
                        f"{k}: {v}" for k, v in value.items() if v is not None
                    )
            return str(value)

        return WathqCommercialRegistrationPDF(
            main_content=main_content,
            info_boxes=info_boxes if info_boxes else None,
            show_signature=True,
            cr_number=safe_str(cr_data.get("cr_number")),
            company_name=safe_str(cr_data.get("company_name")),
            establishment_date=safe_str(cr_data.get("establishment_date")),
            expiry_date=safe_str(cr_data.get("expiry_date")),
            capital=safe_str(cr_data.get("capital")),
            legal_form=safe_str(cr_data.get("legal_form")),
            main_activity=safe_str(cr_data.get("main_activity")),
            address=safe_str(cr_data.get("address")),
        )

    def create_table_from_wathq_data(
        self,
        wathq_response: Dict[str, Any],
        table_config: Optional[Dict[str, Any]] = None,
    ) -> tuple:
        """Convert WATHQ API response to table format"""

        if not table_config:
            # Default table configuration
            table_config = {
                "headers": ["الحقل", "القيمة"],
                "exclude_fields": ["id", "created_at", "updated_at"],
            }

        headers = table_config.get("headers", ["الحقل", "القيمة"])
        exclude_fields = table_config.get("exclude_fields", [])

        table_data = []

        def flatten_dict(d, parent_key="", sep="_"):
            """Flatten nested dictionary"""
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                elif isinstance(v, list) and v and isinstance(v[0], dict):
                    for i, item in enumerate(v):
                        items.extend(
                            flatten_dict(item, f"{new_key}_{i}", sep=sep).items()
                        )
                else:
                    items.append((new_key, v))
            return dict(items)

        flattened = flatten_dict(wathq_response)

        for key, value in flattened.items():
            if key not in exclude_fields and value is not None:
                # Translate common field names to Arabic
                arabic_key = self._translate_field_name(key)
                table_data.append([arabic_key, str(value)])

        return headers, table_data

    def _translate_field_name(self, field_name: str) -> str:
        """Translate common field names to Arabic"""
        translations = {
            "cr_number": "رقم السجل التجاري",
            "company_name": "اسم الشركة",
            "legal_form": "الشكل القانوني",
            "capital": "رأس المال",
            "main_activity": "النشاط الرئيسي",
            "establishment_date": "تاريخ التأسيس",
            "expiry_date": "تاريخ الانتهاء",
            "address": "العنوان",
            "status": "الحالة",
            "owners": "المالكون",
            "managers": "المديرون",
            "branches": "الفروع",
            "name": "الاسم",
            "nationality": "الجنسية",
            "id_number": "رقم الهوية",
            "position": "المنصب",
            "phone": "الهاتف",
            "email": "البريد الإلكتروني",
        }

        return translations.get(field_name, field_name)

    def add_logo_from_file(self, data: WathqPDFData, logo_path: str) -> WathqPDFData:
        """Add logo to PDF data from file path"""
        if Path(logo_path).exists():
            data.logo_base64 = PDFHelper.image_to_base64(logo_path, resize=(200, 80))
        return data

    def create_multi_section_document(
        self, sections_data: List[Dict[str, Any]], document_title: str, **kwargs
    ) -> WathqPDFData:
        """Create a multi-section document"""

        sections = []
        main_content_parts = []

        for i, section_data in enumerate(sections_data):
            section = DocumentSection(
                title=section_data.get("title"),
                content=section_data.get("content", ""),
                page_break=section_data.get(
                    "page_break", i > 0
                ),  # Page break after first section
                no_break=section_data.get("no_break", False),
            )
            sections.append(section)

            # Also add to main content for simple rendering
            if section.title:
                main_content_parts.append(f"<h2>{section.title}</h2>")
            main_content_parts.append(section.content)

        return WathqPDFData(
            document_title=document_title,
            main_content="\n".join(main_content_parts),
            sections=sections,
            **kwargs,
        )


# Global service instance
pdf_service = WathqPDFService()
