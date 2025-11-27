from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, List
from jinja2 import Template
import base64
from pathlib import Path
import weasyprint  # For HTML to PDF conversion
# Alternative: import pdfkit  # Another option

app = FastAPI()


class PDFData(BaseModel):
    """Model for PDF generation data"""

    # Document metadata
    document_title: Optional[str] = "توثيق العدل"
    content_title: Optional[str] = None

    # Company information
    company_name_ar: Optional[str] = "شركة مجموعة توثيق العدل"
    company_name_en: Optional[str] = (
        "Notarization Justice Group for Real Estate Development and Investment Company"
    )

    # Logo (either base64 or URL)
    logo_base64: Optional[str] = None
    logo_url: Optional[str] = None

    # Main content
    main_content: str
    watermark_text: Optional[str] = "توثيق"

    # Table data
    show_table: Optional[bool] = False
    table_headers: Optional[List[str]] = None
    table_data: Optional[List[List[str]]] = None

    # Signature section
    show_signature: Optional[bool] = False
    signature_label_1: Optional[str] = "المدير"
    signature_label_2: Optional[str] = "المستلم"

    # Footer contact information
    phone_number: Optional[str] = "0112322022"
    email: Optional[str] = "info@tawthiq.com.sa"
    location: Optional[str] = "Saudi Arabia - Riyadh"


def load_template() -> Template:
    """Load the Jinja2 template from file"""
    template_path = Path("templates/wcr-pdf_template.html")

    # If template file doesn't exist, use inline template
    if not template_path.exists():
        # You would paste the template content here
        template_content = """
        <!-- Paste the full template here or load from file -->
        """
        return Template(template_content)

    with open(template_path, "r", encoding="utf-8") as f:
        return Template(f.read())


def image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


@app.post("/generate-pdf/")
async def generate_pdf(data: PDFData):
    """
    Generate PDF from template with provided data

    Example usage:
    ```python
    import requests

    data = {
        "content_title": "تقرير الأداء السنوي",
        "main_content": "<p>هذا نص تجريبي للمحتوى...</p>",
        "show_table": True,
        "table_headers": ["الاسم", "القسم", "التاريخ"],
        "table_data": [
            ["أحمد محمد", "المبيعات", "2024-01-15"],
            ["سارة علي", "التسويق", "2024-01-16"]
        ]
    }

    response = requests.post("http://localhost:8000/generate-pdf/", json=data)
    with open("output.pdf", "wb") as f:
        f.write(response.content)
    ```
    """
    try:
        # Load template
        template = load_template()

        # Render HTML with data
        html_content = template.render(
            document_title=data.document_title,
            content_title=data.content_title,
            company_name_ar=data.company_name_ar,
            company_name_en=data.company_name_en,
            logo_base64=data.logo_base64,
            logo_url=data.logo_url,
            main_content=data.main_content,
            watermark_text=data.watermark_text,
            show_table=data.show_table,
            table_headers=data.table_headers,
            table_data=data.table_data,
            show_signature=data.show_signature,
            signature_label_1=data.signature_label_1,
            signature_label_2=data.signature_label_2,
            phone_number=data.phone_number,
            email=data.email,
            location=data.location,
        )

        # Convert HTML to PDF using WeasyPrint
        pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()

        # Return PDF as response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={data.document_title}.pdf"
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.post("/generate-pdf-with-image/")
async def generate_pdf_with_image(data: PDFData, logo_path: Optional[str] = None):
    """
    Generate PDF with logo from local file path
    """
    if logo_path:
        data.logo_base64 = image_to_base64(logo_path)

    return await generate_pdf(data)


@app.get("/preview-html/")
async def preview_html(
    content: str = "<p>محتوى تجريبي</p>", title: Optional[str] = "معاينة"
):
    """
    Preview HTML template before generating PDF
    """
    template = load_template()

    html_content = template.render(
        content_title=title, main_content=content, show_signature=True
    )

    return Response(content=html_content, media_type="text/html")
