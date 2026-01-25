# WATHQ PDF Template Documentation

## Overview
A modern PDF template designed for WATHQ (وثق) live and offline data visualization. The template follows the company branding with blue and orange color scheme and supports Arabic content.

## Template Design
Based on the design from `dashboard/assets/images/simple_pdf_template.avif`, the template includes:
- **Header**: Company logo, Arabic/English company name, blue top line, orange accent section
- **Content Area**: Main document content with watermark background
- **Footer**: Contact information with colored bottom line

## Files Created

### Template File
- `api/templates/wathq-modern-template.html` - Main PDF template

### Assets
- `api/templates/assets/header_fixed_line.avif` - Blue header line
- `api/templates/assets/header_right_colored.avif` - Orange header section
- `api/templates/assets/header_logo_after_colored.avif` - Company logo
- `api/templates/assets/header_logo_text_after_logo.avif` - Company text logo
- `api/templates/assets/footer_fixed_line.avif` - Footer colored line

### Service Methods
New methods added to `WathqPDFService`:
- `create_wathq_data_pdf()` - Create PDF data model from WATHQ JSON
- `generate_wathq_pdf_bytes()` - Generate PDF bytes directly
- `generate_wathq_pdf_response()` - Generate FastAPI Response
- `preview_wathq_html()` - Generate HTML preview

## Usage Examples

### 1. Basic PDF Generation
```python
from app.services.wathq_pdf_service import pdf_service

# Sample WATHQ data
wathq_data = {
    "service_name": "السجل التجاري ( التشريعات الجديدة )",
    "cr_number": "1010711252",
    "company_name": "شركة مجموعة توثيق العدل",
    "description": "وثيقة السجل التجاري ( التشريعات الجديدة )"
}

# Generate PDF bytes
pdf_bytes = pdf_service.generate_wathq_pdf_bytes(
    wathq_data=wathq_data,
    document_title="السجل التجاري ( التشريعات الجديدة )",
    show_watermark=True,
    watermark_text="وثق"
)

# Save to file
with open("commercial_registration.pdf", "wb") as f:
    f.write(pdf_bytes)
```

### 2. HTML Preview
```python
# Generate HTML preview for browser display
html_content = pdf_service.preview_wathq_html(
    wathq_data=wathq_data,
    document_title="السجل التجاري ( التشريعات الجديدة )",
    show_watermark=True
)

# Save or return HTML
with open("preview.html", "w", encoding="utf-8") as f:
    f.write(html_content)
```

### 3. FastAPI Response
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/wathq/pdf/{service_id}")
async def generate_wathq_pdf(service_id: str):
    # Get WATHQ data from your service
    wathq_data = get_wathq_data(service_id)
    
    # Generate PDF response
    return pdf_service.generate_wathq_pdf_response(
        wathq_data=wathq_data,
        document_title=f"وثيقة {wathq_data.get('service_name', 'وثق')}",
        filename=f"wathq_{service_id}.pdf"
    )
```

## Template Features

### Supported Data Fields
The template automatically handles these common WATHQ fields:
- `service_name` - Service name (displayed in highlight box)
- `cr_number` - Commercial registration number
- `company_name` - Company name
- `description` - Document description
- `legal_form` - Legal form
- `capital` - Capital amount
- `main_activity` - Main business activity
- `establishment_date` - Establishment date
- `expiry_date` - Expiry date
- `address` - Company address
- `status` - Current status
- `owners` - List of owners
- `managers` - List of managers

### Template Options
- `show_watermark` (bool) - Show/hide watermark
- `watermark_text` (str) - Custom watermark text
- `show_signature` (bool) - Show/hide signature section
- `show_raw_data` (bool) - Show JSON data for debugging
- `company_name_ar` (str) - Arabic company name
- `company_name_en` (str) - English company name

### Styling Features
- **Arabic RTL Support** - Proper right-to-left layout
- **Responsive Design** - Adapts to different content sizes
- **Print Optimized** - Proper page breaks and print colors
- **Brand Colors** - Blue (#1e3a8a) and Orange (#f59e0b)
- **Professional Layout** - Clean, modern design

## Testing

Run the test script to verify template functionality:
```bash
cd api
python test_wathq_template.py
```

This will generate:
- `wathq_preview.html` - Full data HTML preview
- `wathq_sample.pdf` - Full data PDF
- `wathq_minimal_preview.html` - Minimal data with JSON

## Integration with Existing System

The new template integrates with the existing PDF system:
1. Uses the same `WathqPDFData` model
2. Compatible with existing endpoints
3. Supports all current PDF options
4. Can be used alongside existing templates

## Customization

To customize the template:
1. Edit `wathq-modern-template.html` for layout changes
2. Modify CSS styles for different colors/fonts
3. Add new template variables in the service methods
4. Update assets in `api/templates/assets/` for different branding

## Notes
- Template uses Tahoma font for better Arabic support
- WeasyPrint handles PDF generation from HTML/CSS
- All text content supports Arabic and English
- Images are embedded as base64 for portability
- Template is optimized for A4 page size
