# PDF Dependencies Installation Guide

## Issue Identified
The 500 Internal Server Error occurs because **WeasyPrint** and related PDF generation dependencies are missing from the system.

## Root Cause
The PDF service imports WeasyPrint but it's not installed:
```python
from weasyprint import HTML  # ModuleNotFoundError: No module named 'weasyprint'
```

## Solution: Install Required Dependencies

### Option 1: Using pip (if available)
```bash
# Navigate to API directory
cd /home/aziztech/Desktop/atqan-apps-2025/atqan-wathq-services-fixing/api

# Install PDF dependencies
pip install weasyprint>=61.0 Pillow>=10.0.0 jinja2>=3.1.0

# Or install from requirements file
pip install -r requirements/requirements-dev.txt
```

### Option 2: Using conda (if available)
```bash
conda install -c conda-forge weasyprint pillow jinja2
```

### Option 3: Using system package manager (Ubuntu/Debian)
```bash
# Install system dependencies first
sudo apt-get update
sudo apt-get install python3-pip python3-dev python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0

# Then install Python packages
pip3 install weasyprint Pillow jinja2
```

### Option 4: Using Docker (recommended for production)
Add to Dockerfile:
```dockerfile
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    && pip install weasyprint Pillow jinja2
```

## Dependencies Added to requirements-dev.txt
```
# PDF generation dependencies
weasyprint>=61.0
Pillow>=10.0.0
jinja2>=3.1.0
```

## Verification Steps

### 1. Test WeasyPrint Installation
```bash
python3 -c "from weasyprint import HTML; print('WeasyPrint installed successfully')"
```

### 2. Test PDF Generation
```bash
cd /home/aziztech/Desktop/atqan-apps-2025/atqan-wathq-services-fixing/api
python3 -c "
from weasyprint import HTML
html = '<html><body><h1>Test</h1></body></html>'
pdf = HTML(string=html).write_pdf()
print(f'PDF generated: {len(pdf)} bytes')
"
```

### 3. Test Template Rendering
```bash
cd /home/aziztech/Desktop/atqan-apps-2025/atqan-wathq-services-fixing/api
python3 -c "
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('wathq-modern-template.html')
print('Template loaded successfully')
"
```

## After Installation

1. **Restart the API server** to load the new dependencies
2. **Test the PDF export** from the commercial registration page
3. **Verify both PDF export and preview** functions work

## Expected Results After Fix

✅ **PDF Export**: Should download PDF file successfully  
✅ **PDF Preview**: Should open HTML preview in new window  
✅ **No 500 Errors**: API should respond with 200 OK  
✅ **Modern Template**: PDF should use new branding design  

## Troubleshooting

### If WeasyPrint installation fails:
1. Install system dependencies first (see Option 3)
2. Use virtual environment
3. Check Python version compatibility (3.8+)

### If PDF generation still fails:
1. Check server logs for detailed error messages
2. Verify template file exists and is readable
3. Test with minimal HTML first

### Common Issues:
- **Cairo/Pango libraries missing**: Install system dependencies
- **Permission errors**: Use virtual environment or sudo
- **Memory issues**: Increase server memory allocation

## Alternative Solutions

If WeasyPrint continues to cause issues, consider:
1. **wkhtmltopdf**: Alternative PDF generator
2. **ReportLab**: Python-native PDF library
3. **Puppeteer**: Headless Chrome for PDF generation
4. **External PDF service**: Use cloud-based PDF API

## Next Steps

1. Install the dependencies using one of the methods above
2. Restart the API server
3. Test the PDF functionality
4. If issues persist, check server logs for specific error messages
