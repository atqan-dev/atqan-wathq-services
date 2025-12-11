# PDF Template Designer with GrapesJS

A comprehensive PDF template management system built with GrapesJS for visual design and WeasyPrint for PDF generation.

## Features

### 🎨 Visual Template Design
- **GrapesJS Editor**: Drag-and-drop visual editor for designing PDF templates
- **Responsive Design**: Preview templates in desktop, tablet, and mobile views
- **Component Library**: Pre-built blocks and components for quick design
- **Code Editor**: Switch between visual and code modes (HTML/CSS)
- **Live Preview**: Real-time preview of template changes

### 📄 Template Management
- **CRUD Operations**: Create, read, update, and delete templates
- **Version Control**: Automatic version tracking for template changes
- **Categories**: Organize templates by category (invoice, certificate, report, etc.)
- **Template Duplication**: Clone existing templates for quick variations
- **Search & Filter**: Find templates by name, category, or status

### 🔧 Dynamic Data Mapping
- **JSON Data Mapping**: Define how data fields map to template variables
- **Sample Data**: Provide sample data for testing and previewing
- **Variable Syntax**: Use `{{ variable_name }}` syntax in templates
- **Nested Data**: Support for nested JSON structures

### 📊 PDF Generation
- **On-Demand Generation**: Generate PDFs from templates with custom data
- **Version Support**: Generate PDFs from specific template versions
- **Multiple Page Sizes**: Support for A4, Letter, Legal, A3, A5
- **Orientation Options**: Portrait and landscape orientations
- **Download Tracking**: Track PDF downloads and usage statistics

### 📈 Analytics & History
- **Usage Statistics**: Track how many times each template is used
- **Generation History**: View all generated PDFs with metadata
- **Version History**: Complete audit trail of template changes
- **Download Counts**: Monitor PDF download activity

## Architecture

### Backend (FastAPI)

#### Models (`api/app/models/pdf_template.py`)
- **PdfTemplate**: Main template model with GrapesJS data
- **PdfTemplateVersion**: Version control for templates
- **GeneratedPdf**: Tracks generated PDF files

#### Schemas (`api/app/schemas/pdf_template.py`)
- Pydantic models for request/response validation
- Type-safe data structures
- Comprehensive validation rules

#### CRUD Operations (`api/app/crud/crud_pdf_template.py`)
- **CRUDPdfTemplate**: Template management operations
- **CRUDPdfTemplateVersion**: Version management
- **CRUDGeneratedPdf**: Generated PDF tracking

#### Services (`api/app/services/pdf_generator.py`)
- **PdfGeneratorService**: PDF generation with WeasyPrint
- Template rendering with Jinja2
- Fallback HTML generation if WeasyPrint unavailable

#### API Endpoints (`api/app/api/v1/endpoints/pdf_templates.py`)
- `GET /pdf-templates/templates` - List templates
- `POST /pdf-templates/templates` - Create template
- `GET /pdf-templates/templates/{id}` - Get template details
- `PUT /pdf-templates/templates/{id}` - Update template
- `DELETE /pdf-templates/templates/{id}` - Delete template
- `POST /pdf-templates/templates/{id}/duplicate` - Duplicate template
- `GET /pdf-templates/templates/{id}/versions` - List versions
- `POST /pdf-templates/templates/{id}/generate` - Generate PDF
- `GET /pdf-templates/downloads/{pdf_id}` - Download PDF

### Frontend (Nuxt 3 + Vue 3)

#### Composables (`dashboard/composables/usePdfTemplates.ts`)
- Type-safe API client
- Reusable template management functions
- Error handling and response parsing

#### Components (`dashboard/components/PdfEditor/`)
- **GrapesJsEditor.vue**: Wrapper component for GrapesJS
  - Custom configuration for PDF design
  - Responsive device preview
  - Event handling and data synchronization
  - Style customization

#### Pages (`dashboard/pages/pdf-templates/`)
- **index.vue**: Template list and management
  - Grid view with thumbnails
  - Search and filtering
  - Inline actions (edit, duplicate, delete)
  - Pagination

- **create.vue**: Template creation and editing
  - Form for template metadata
  - GrapesJS visual editor
  - Code editor mode
  - Data mapping configuration
  - Live preview

- **[id].vue**: Template details and PDF generation
  - Template preview
  - Version history
  - Generated PDFs list
  - PDF generation modal
  - Download functionality

## Installation

### Backend Dependencies

```bash
cd api
uv sync  # or pip install -r requirements.txt
```

Required packages:
- `weasyprint>=62.0` - PDF generation
- `jinja2>=3.1.0` - Template rendering

### Frontend Dependencies

```bash
cd dashboard
pnpm install  # or npm install
```

Required packages:
- `grapesjs@^0.21.13` - Visual editor
- `grapesjs-preset-webpage@^1.0.3` - Webpage preset
- `grapesjs-blocks-basic@^1.0.2` - Basic blocks

## Database Migration

Run the migration to create the required tables:

```bash
cd api
alembic upgrade head
```

This creates:
- `pdf_templates` - Main template storage
- `pdf_template_versions` - Version history
- `generated_pdfs` - Generated PDF tracking

## Usage

### Creating a Template

1. Navigate to **PDF Templates** → **Create Template**
2. Fill in template metadata (name, slug, category, etc.)
3. Use the visual editor to design your template
4. Add data mapping if needed (JSON format)
5. Provide sample data for testing
6. Click **Save** to create the template

### Generating a PDF

1. Navigate to a template's detail page
2. Click **Generate PDF**
3. Provide data in JSON format
4. Click **Generate**
5. Download the generated PDF

### Using Variables in Templates

In your template HTML, use Jinja2 syntax:

```html
<h1>Hello, {{ customer_name }}!</h1>
<p>Invoice Number: {{ invoice_number }}</p>

<ul>
  {% for item in items %}
    <li>{{ item.name }}: ${{ item.price }}</li>
  {% endfor %}
</ul>
```

Then provide data when generating:

```json
{
  "customer_name": "John Doe",
  "invoice_number": "INV-001",
  "items": [
    {"name": "Product A", "price": 99.99},
    {"name": "Product B", "price": 149.99}
  ]
}
```

## API Examples

### Create a Template

```typescript
const template = await createTemplate({
  name: "Invoice Template",
  slug: "invoice-template",
  description: "Standard invoice template",
  category: "invoice",
  grapesjs_data: { components: [...], styles: [...] },
  grapesjs_html: "<div>...</div>",
  grapesjs_css: ".invoice { ... }",
  page_size: "A4",
  page_orientation: "portrait",
  is_active: true
})
```

### Generate a PDF

```typescript
const pdf = await generatePdf(templateId, {
  data: {
    customer_name: "John Doe",
    invoice_number: "INV-001",
    amount: 299.99
  },
  filename: "invoice-001.pdf"
})

// Download URL is returned
window.open(pdf.download_url, '_blank')
```

### List Templates

```typescript
const { templates, total } = await listTemplates({
  skip: 0,
  limit: 12,
  category: "invoice",
  is_active: true,
  search: "monthly"
})
```

## Configuration

### Page Sizes
- A4 (210mm × 297mm)
- Letter (8.5in × 11in)
- Legal (8.5in × 14in)
- A3 (297mm × 420mm)
- A5 (148mm × 210mm)

### Categories
- General
- Certificate
- Invoice
- Report
- Letter
- Contract

## Security Considerations

- All endpoints require authentication
- Templates are associated with tenants for multi-tenancy
- Generated PDFs can be set as public or private
- Optional expiration dates for generated PDFs
- File access control through API endpoints

## Performance Optimization

- **Template Caching**: Frequently used templates are cached
- **Lazy Loading**: Components load only when needed
- **Pagination**: Large lists are paginated
- **Thumbnail Generation**: Visual previews for quick browsing
- **Async PDF Generation**: Non-blocking PDF creation

## Troubleshooting

### WeasyPrint Installation Issues

WeasyPrint requires system dependencies:

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0
```

**macOS:**
```bash
brew install pango
```

**Windows:**
Follow the [WeasyPrint documentation](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation)

### GrapesJS Not Loading

Ensure GrapesJS is imported client-side only:

```vue
<ClientOnly>
  <PdfEditorGrapesJsEditor ... />
</ClientOnly>
```

## Future Enhancements

- [ ] Template marketplace/sharing
- [ ] Advanced typography options
- [ ] Image upload and management
- [ ] Custom fonts support
- [ ] Bulk PDF generation
- [ ] Email delivery integration
- [ ] Webhook notifications
- [ ] PDF password protection
- [ ] Digital signatures
- [ ] QR code generation

## License

This implementation is part of the Atqan Wathq Services project.

## Support

For issues or questions, please contact the development team or create an issue in the project repository.
