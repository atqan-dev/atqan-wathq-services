"""
Pydantic models for WATHQ PDF generation
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class InfoBoxItem(BaseModel):
    """Individual item in an info box"""

    label: str
    value: str


class InfoBox(BaseModel):
    """Info box with title and items"""

    title: str
    items: List[InfoBoxItem]


class DocumentSection(BaseModel):
    """Document section with optional title and content"""

    title: Optional[str] = None
    content: str
    page_break: Optional[bool] = False
    no_break: Optional[bool] = False


class WathqPDFData(BaseModel):
    """Enhanced model for WATHQ PDF generation"""

    # Document metadata
    document_title: Optional[str] = Field(
        default="وثيقة رسمية", description="Main document title"
    )
    document_type: Optional[str] = Field(
        default="wathq_document", description="Document type identifier"
    )

    # Company/Organization information
    company_name_ar: Optional[str] = Field(
        default="شركة مجموعة توثيق العدل", description="Arabic company name"
    )
    company_name_en: Optional[str] = Field(
        default="Notarization Justice Group for Real Estate Development and Investment Company",
        description="English company name",
    )

    # Logo configuration
    logo_base64: Optional[str] = Field(
        default=None, description="Base64 encoded logo image"
    )
    logo_url: Optional[str] = Field(default=None, description="URL to logo image")

    # Content
    main_content: str = Field(..., description="Main document content (HTML)")

    # Watermark
    show_watermark: Optional[bool] = Field(default=True, description="Show watermark")
    watermark_text: Optional[str] = Field(
        default="وثيقة رسمية", description="Watermark text"
    )

    # Table data
    show_table: Optional[bool] = Field(default=False, description="Show data table")
    table_title: Optional[str] = Field(default=None, description="Table title")
    table_headers: Optional[List[str]] = Field(
        default=None, description="Table column headers"
    )
    table_data: Optional[List[List[str]]] = Field(
        default=None, description="Table row data"
    )

    # Info boxes
    info_boxes: Optional[List[InfoBox]] = Field(
        default=None, description="Information boxes"
    )

    # Document sections
    sections: Optional[List[DocumentSection]] = Field(
        default=None, description="Additional document sections"
    )

    # Signature section
    show_signature: Optional[bool] = Field(
        default=False, description="Show signature section"
    )
    signature_label_1: Optional[str] = Field(
        default="المدير العام", description="First signature label"
    )
    signature_label_2: Optional[str] = Field(
        default="المستلم", description="Second signature label"
    )
    signature_label_3: Optional[str] = Field(
        default=None, description="Third signature label (optional)"
    )

    # Page numbering
    show_page_numbers: Optional[bool] = Field(
        default=True, description="Show page numbers"
    )
    page_number: Optional[str] = Field(default="01", description="Page number")

    # Footer contact information
    phone_number: Optional[str] = Field(
        default="0112322022", description="Phone number"
    )
    email: Optional[str] = Field(
        default="info@tawthiq.com.sa", description="Email address"
    )
    location: Optional[str] = Field(
        default="المملكة العربية السعودية - الرياض", description="Location"
    )
    website: Optional[str] = Field(default=None, description="Website URL")

    # WATHQ data for modern template
    wathq_data: Optional[Dict[str, Any]] = Field(
        default=None, description="Raw WATHQ API response data"
    )
    show_raw_data: Optional[bool] = Field(
        default=False, description="Show raw JSON data in document"
    )
    raw_json_data: Optional[Dict[str, Any]] = Field(
        default=None, description="Raw JSON data for debugging"
    )

    # PDF generation options
    pdf_options: Optional[Dict[str, Any]] = Field(
        default={
            "page_size": "A4",
            "orientation": "portrait",
            "margin_top": "0mm",
            "margin_bottom": "0mm",
            "margin_left": "0mm",
            "margin_right": "0mm",
            "encoding": "UTF-8",
            "no_outline": None,
        },
        description="PDF generation options for WeasyPrint",
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class WathqCommercialRegistrationPDF(WathqPDFData):
    """Specialized model for Commercial Registration documents"""

    # Basic Information
    cr_number: Optional[str] = Field(
        default=None, description="Commercial Registration number"
    )
    cr_national_number: Optional[str] = Field(
        default=None, description="CR National number"
    )
    name: Optional[str] = Field(default=None, description="Company name")
    name_lang_desc: Optional[str] = Field(
        default=None, description="Company name language description"
    )
    cr_capital: Optional[str] = Field(default=None, description="CR Capital")
    company_duration: Optional[str] = Field(
        default=None, description="Company duration"
    )
    version_no: Optional[str] = Field(default=None, description="Version number")

    # Dates
    issue_date_gregorian: Optional[str] = Field(
        default=None, description="Issue date (Gregorian)"
    )
    issue_date_hijri: Optional[str] = Field(
        default=None, description="Issue date (Hijri)"
    )

    # Status (as dictionary)
    status: Optional[Dict[str, Any]] = Field(
        default=None, description="Status information"
    )

    # Location
    headquarter_city_name: Optional[str] = Field(
        default=None, description="Headquarter city name"
    )
    headquarter_city_id: Optional[str] = Field(
        default=None, description="Headquarter city ID"
    )

    # Entity Type (as dictionary)
    entity_type: Optional[Dict[str, Any]] = Field(
        default=None, description="Entity type information"
    )

    # Contact Information (as dictionary)
    contact_info: Optional[Dict[str, Any]] = Field(
        default=None, description="Contact information"
    )

    # Capital Details (as dictionary)
    capital: Optional[Dict[str, Any]] = Field(
        default=None, description="Capital details"
    )

    # Partners/Parties (as list of dictionaries)
    parties: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Partners and parties"
    )

    # Management (as dictionary)
    management: Optional[Dict[str, Any]] = Field(
        default=None, description="Management information"
    )

    # Activities (as list of dictionaries)
    activities: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Business activities"
    )

    # Additional Information
    is_main: Optional[bool] = Field(default=None, description="Is main CR")
    main_cr_number: Optional[str] = Field(default=None, description="Main CR number")
    main_cr_national_number: Optional[str] = Field(
        default=None, description="Main CR national number"
    )
    in_liquidation_process: Optional[bool] = Field(
        default=None, description="In liquidation process"
    )
    has_ecommerce: Optional[bool] = Field(default=None, description="Has e-commerce")
    is_license_based: Optional[bool] = Field(
        default=None, description="Is license based"
    )
    license_issuer_name: Optional[str] = Field(
        default=None, description="License issuer name"
    )
    partners_nationality_name: Optional[str] = Field(
        default=None, description="Partners nationality name"
    )

    # Legacy fields for backward compatibility
    company_name: Optional[str] = Field(
        default=None, description="Company name from CR"
    )
    establishment_date: Optional[str] = Field(
        default=None, description="Establishment date"
    )
    expiry_date: Optional[str] = Field(default=None, description="Expiry date")
    legal_form: Optional[str] = Field(default=None, description="Legal form")
    main_activity: Optional[str] = Field(
        default=None, description="Main business activity"
    )
    address: Optional[str] = Field(default=None, description="Company address")

    def __init__(self, **data):
        # Set default document title for CR documents
        if "document_title" not in data:
            data["document_title"] = "شهادة السجل التجاري"

        # Set default watermark for CR documents
        if "watermark_text" not in data:
            data["watermark_text"] = "السجل التجاري"

        super().__init__(**data)


class WathqRealEstatePDF(WathqPDFData):
    """Specialized model for Real Estate documents"""

    # Real estate specific fields
    property_id: Optional[str] = Field(default=None, description="Property ID")
    property_type: Optional[str] = Field(default=None, description="Property type")
    area: Optional[str] = Field(default=None, description="Property area")
    location: Optional[str] = Field(default=None, description="Property location")
    owner_name: Optional[str] = Field(default=None, description="Owner name")
    deed_number: Optional[str] = Field(default=None, description="Deed number")

    def __init__(self, **data):
        # Set default document title for real estate documents
        if "document_title" not in data:
            data["document_title"] = "وثيقة عقارية"

        # Set default watermark for real estate documents
        if "watermark_text" not in data:
            data["watermark_text"] = "عقاري"

        super().__init__(**data)


class WathqEmployeePDF(WathqPDFData):
    """Specialized model for Employee documents"""

    # Employee specific fields
    employee_id: Optional[str] = Field(default=None, description="Employee ID")
    employee_name: Optional[str] = Field(default=None, description="Employee name")
    position: Optional[str] = Field(default=None, description="Job position")
    department: Optional[str] = Field(default=None, description="Department")
    hire_date: Optional[str] = Field(default=None, description="Hire date")
    salary: Optional[str] = Field(default=None, description="Salary")

    def __init__(self, **data):
        # Set default document title for employee documents
        if "document_title" not in data:
            data["document_title"] = "شهادة عمل"

        # Set default watermark for employee documents
        if "watermark_text" not in data:
            data["watermark_text"] = "موظف"

        super().__init__(**data)
