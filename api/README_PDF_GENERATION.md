# WATHQ PDF Generation System

This document describes the enhanced PDF generation system for WATHQ external API calls, allowing you to export API responses as professional PDF documents.

## Overview

The PDF generation system provides:
- **Professional Arabic document templates** with company branding
- **Multi-page support** with repeating headers and footers
- **Flexible content structure** with sections, tables, and info boxes
- **Integration with WATHQ APIs** for automatic data export
- **Customizable templates** and styling

## Files Structure

```
api/
├── templates/
│   └── wathq-document-template.html     # Main Jinja2 template
├── app/
│   ├── models/
│   │   └── wathq_pdf_data.py           # Pydantic models for PDF data
│   ├── services/
│   │   └── wathq_pdf_service.py        # PDF generation service
│   └── api/v1/endpoints/
│       └── wathq_pdf_export.py         # API endpoints for PDF export
├── examples/
│   └── pdf_generation_examples.py      # Usage examples
└── utils/
    └── wcr_pdf_helpers.py              # Helper functions
```

## Template Features

The main template (`wathq-document-template.html`) includes:

### Design Elements
- **Professional Arabic layout** (RTL support)
- **Blue and orange color scheme** matching the provided design
- **Company logo and branding** in header
- **Contact information** in footer
- **Watermark support** for document authenticity

### Multi-page Support
- **Fixed header** that repeats on every page
- **Fixed footer** with contact details
- **Page break controls** for sections
- **Page numbering** (optional)

### Content Components
- **Document title** with professional styling
- **Main content area** with rich HTML support
- **Data tables** with alternating row colors
- **Info boxes** for structured information
- **Signature sections** for approvals
- **Multi-column layouts** (optional)

## API Endpoints

### Commercial Registration PDF Export
```http
POST /api/v1/wathq/pdf/commercial-registration/{cr_id}/pdf
```

**Parameters:**
- `cr_id`: Commercial Registration ID
- `language`: ar|en (default: ar)
- `template`: Custom template name (optional)
- `include_full_info`: Include full CR details (default: true)
- `include_owners`: Include owners information (default: false)
- `include_managers`: Include managers information (default: false)
- `include_branches`: Include branches information (default: false)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/wathq/pdf/commercial-registration/1010123456/pdf?include_owners=true" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o "cr_document.pdf"
```

### Custom Document Creation
```http
POST /api/v1/wathq/pdf/custom-document/pdf
```

**Request Body:**
```json
{
  "document_title": "تقرير شهري",
  "main_content": "<p>محتوى الوثيقة...</p>",
  "show_table": true,
  "table_headers": ["العمود 1", "العمود 2"],
  "table_data": [["قيمة 1", "قيمة 2"]],
  "show_signature": true,
  "signature_label_1": "المدير",
  "signature_label_2": "المستلم"
}
```

### HTML Preview
```http
GET /api/v1/wathq/pdf/preview/commercial-registration/{cr_id}
POST /api/v1/wathq/pdf/preview/custom-document
```

### Generic WATHQ Data Export
```http
POST /api/v1/wathq/pdf/wathq-data/{service_type}/{identifier}/pdf
```

Supported service types:
- `commercial-registration`
- `real-estate` (planned)
- `employee` (planned)
- `attorney` (planned)

## Usage Examples

### Basic Document
```python
from app.models.wathq_pdf_data import WathqPDFData
from app.services.wathq_pdf_service import pdf_service

pdf_data = WathqPDFData(
    document_title="تقرير شهري",
    main_content="<p>محتوى التقرير...</p>",
    show_signature=True
)

pdf_bytes = pdf_service.generate_pdf_bytes(pdf_data)
```

### Commercial Registration Document
```python
# Sample CR data from WATHQ API
cr_data = {
    "cr_number": "1010123456",
    "company_name": "شركة الأعمال المتقدمة",
    "legal_form": "شركة ذات مسؤولية محدودة",
    "capital": "1,000,000 ريال"
}

pdf_data = pdf_service.create_commercial_registration_pdf(cr_data)
pdf_bytes = pdf_service.generate_pdf_bytes(pdf_data)
```

### Document with Table
```python
pdf_data = WathqPDFData(
    document_title="تقرير المبيعات",
    main_content="<p>تقرير المبيعات الشهرية</p>",
    show_table=True,
    table_headers=["المنتج", "الكمية", "السعر"],
    table_data=[
        ["منتج أ", "100", "50 ريال"],
        ["منتج ب", "75", "80 ريال"]
    ]
)
```

### Multi-Section Document
```python
sections_data = [
    {
        "title": "المقدمة",
        "content": "<p>مقدمة الوثيقة</p>",
        "page_break": False
    },
    {
        "title": "التفاصيل",
        "content": "<p>تفاصيل الموضوع</p>",
        "page_break": True
    }
]

pdf_data = pdf_service.create_multi_section_document(
    sections_data=sections_data,
    document_title="وثيقة متعددة الأقسام"
)
```

## Customization

### Template Variables

The template accepts these variables:

**Document Structure:**
- `document_title`: Main document title
- `main_content`: HTML content
- `sections`: List of document sections
- `watermark_text`: Watermark text
- `show_watermark`: Show/hide watermark

**Company Branding:**
- `company_name_ar`: Arabic company name
- `company_name_en`: English company name
- `logo_base64`: Base64 encoded logo
- `logo_url`: Logo image URL

**Tables:**
- `show_table`: Show data table
- `table_title`: Table title
- `table_headers`: Column headers
- `table_data`: Row data

**Info Boxes:**
- `info_boxes`: List of info boxes with title and items

**Signatures:**
- `show_signature`: Show signature section
- `signature_label_1`: First signature label
- `signature_label_2`: Second signature label
- `signature_label_3`: Third signature label (optional)

**Footer:**
- `phone_number`: Contact phone
- `email`: Contact email
- `location`: Company location
- `website`: Company website

### Custom Templates

Create custom templates in the `templates/` directory:

1. Copy `wathq-document-template.html`
2. Modify the design and layout
3. Use the template name in API calls:
   ```http
   POST /api/v1/wathq/pdf/custom-document/pdf?template=my-custom-template
   ```

### Styling Customization

The template uses CSS classes for easy customization:

- `.header`: Document header
- `.footer`: Document footer
- `.content`: Main content area
- `.document-title`: Document title
- `.section-title`: Section titles
- `.data-table`: Data tables
- `.info-box`: Information boxes
- `.signature-section`: Signature area

## Dependencies

Required Python packages:
```bash
pip install weasyprint jinja2 pydantic fastapi pillow
```

For WeasyPrint on different systems:
- **Ubuntu/Debian:** `sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0`
- **macOS:** `brew install pango`
- **Windows:** Install GTK+ runtime

## Integration with WATHQ APIs

The PDF system automatically integrates with existing WATHQ services:

1. **Fetch data** from WATHQ APIs (Commercial Registration, Real Estate, etc.)
2. **Transform data** into PDF-friendly format
3. **Generate PDF** using the template system
4. **Return PDF** as downloadable response

### Authentication

PDF endpoints use the same authentication as other WATHQ endpoints:
- **Tenant users:** Use tenant-specific API keys
- **Management users:** Use global API keys
- **Fallback:** System default API key

## Error Handling

The system includes comprehensive error handling:
- **Template not found:** 404 error with clear message
- **PDF generation failure:** 500 error with details
- **WATHQ API errors:** Propagated with context
- **Invalid data:** Validation errors with field details

## Performance Considerations

- **Template caching:** Templates are cached after first load
- **Async support:** All endpoints are async-compatible
- **Memory management:** Large PDFs are streamed
- **Concurrent requests:** Service supports multiple simultaneous generations

## Future Enhancements

Planned features:
- **Additional WATHQ services** (Real Estate, Employee, Attorney)
- **Template management UI** for non-technical users
- **PDF digital signatures** for legal documents
- **Batch PDF generation** for multiple records
- **Email integration** for automatic document delivery
- **Document versioning** and audit trails

## Troubleshooting

### Common Issues

1. **WeasyPrint installation errors:**
   - Install system dependencies for your OS
   - Use virtual environment
   - Check Python version compatibility

2. **Arabic text not displaying:**
   - Ensure proper fonts are installed
   - Check UTF-8 encoding in templates
   - Verify RTL CSS properties

3. **Template not found:**
   - Check template file path
   - Verify file permissions
   - Ensure template syntax is valid

4. **PDF generation timeout:**
   - Reduce content size
   - Optimize images
   - Check server resources

### Debug Mode

Enable debug mode for detailed error information:
```python
pdf_service = WathqPDFService(debug=True)
```

## Support

For issues and questions:
1. Check the examples in `examples/pdf_generation_examples.py`
2. Review the template documentation
3. Test with the preview endpoints first
4. Check server logs for detailed error messages
