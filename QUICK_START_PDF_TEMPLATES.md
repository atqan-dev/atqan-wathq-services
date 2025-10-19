# Quick Start Guide - PDF Template Designer

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

#### Backend
```bash
cd api
uv sync
# If you don't have uv, use pip:
# pip install weasyprint jinja2
```

**Note**: WeasyPrint requires system libraries. Install them first:

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0
```

**macOS:**
```bash
brew install pango
```

#### Frontend
```bash
cd dashboard
pnpm install
# or: npm install
```

---

### Step 2: Run Database Migration

```bash
cd api
alembic upgrade head
```

This creates the required tables:
- `pdf_templates`
- `pdf_template_versions`
- `generated_pdfs`

---

### Step 3: Start the Services

#### Terminal 1 - Backend API
```bash
cd api
uvicorn app.main:app --reload
```
API will be available at: http://localhost:8000

#### Terminal 2 - Dashboard
```bash
cd dashboard
npm run dev
```
Dashboard will be available at: http://localhost:3001

---

### Step 4: Access the Features

1. **Navigate to PDF Templates**
   - URL: http://localhost:3001/pdf-templates
   - You should see the template list page

2. **Create Your First Template**
   - Click "Create Template" button
   - Fill in the form:
     - Name: "My First Invoice"
     - Slug: "my-first-invoice"
     - Category: "invoice"
   
3. **Design Your Template**
   - Use the visual editor (GrapesJS)
   - Drag components from the left panel
   - Edit styles in the right panel
   - Add dynamic variables like `{{ customer_name }}`

4. **Add Data Mapping (Optional)**
   ```json
   {
     "customer_name": "string",
     "invoice_number": "string",
     "amount": "number",
     "date": "string"
   }
   ```

5. **Add Sample Data (Optional)**
   ```json
   {
     "customer_name": "John Doe",
     "invoice_number": "INV-001",
     "amount": 299.99,
     "date": "2024-01-15"
   }
   ```

6. **Save Template**
   - Click "Save" button
   - Template is created with version 1

---

### Step 5: Generate Your First PDF

1. **Go to Template Details**
   - Click on your template in the list
   - You'll see the template preview

2. **Click "Generate PDF"**
   - A modal will appear

3. **Provide Data**
   ```json
   {
     "customer_name": "Jane Smith",
     "invoice_number": "INV-002",
     "amount": 499.99,
     "date": "2024-01-20"
   }
   ```

4. **Click "Generate"**
   - PDF is generated
   - Download automatically starts

5. **View Generated PDFs**
   - Scroll down to see generation history
   - Download count is tracked
   - Click "Download" to get PDF again

---

## 📝 Example Templates

### Simple Invoice Template

**HTML:**
```html
<div style="padding: 40px; font-family: Arial;">
  <h1 style="color: #2563eb;">Invoice</h1>
  
  <div style="margin: 20px 0;">
    <strong>Invoice Number:</strong> {{ invoice_number }}<br>
    <strong>Date:</strong> {{ date }}
  </div>
  
  <div style="margin: 20px 0;">
    <strong>Bill To:</strong><br>
    {{ customer_name }}<br>
    {{ customer_address }}
  </div>
  
  <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
    <thead>
      <tr style="background: #f3f4f6;">
        <th style="border: 1px solid #e5e7eb; padding: 10px;">Description</th>
        <th style="border: 1px solid #e5e7eb; padding: 10px;">Amount</th>
      </tr>
    </thead>
    <tbody>
      {% for item in items %}
      <tr>
        <td style="border: 1px solid #e5e7eb; padding: 10px;">{{ item.description }}</td>
        <td style="border: 1px solid #e5e7eb; padding: 10px; text-align: right;">${{ item.amount }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  
  <div style="text-align: right; margin-top: 20px;">
    <h2>Total: ${{ total }}</h2>
  </div>
</div>
```

**Sample Data:**
```json
{
  "invoice_number": "INV-001",
  "date": "2024-01-15",
  "customer_name": "Acme Corporation",
  "customer_address": "123 Main St, City, State 12345",
  "items": [
    {"description": "Web Development Services", "amount": 2500.00},
    {"description": "Hosting (Annual)", "amount": 500.00}
  ],
  "total": 3000.00
}
```

---

### Certificate Template

**HTML:**
```html
<div style="text-align: center; padding: 100px 50px; border: 10px double #d97706;">
  <h1 style="font-size: 48px; color: #d97706; margin: 40px 0;">
    Certificate of Achievement
  </h1>
  
  <p style="font-size: 20px; margin: 20px 0;">
    This is to certify that
  </p>
  
  <h2 style="font-size: 36px; color: #1e40af; margin: 30px 0;">
    {{ recipient_name }}
  </h2>
  
  <p style="font-size: 18px; margin: 20px 0;">
    has successfully completed
  </p>
  
  <h3 style="font-size: 28px; margin: 20px 0;">
    {{ course_name }}
  </h3>
  
  <p style="font-size: 16px; margin: 40px 0;">
    Awarded on {{ completion_date }}
  </p>
  
  <div style="margin-top: 60px;">
    <div style="display: inline-block; border-top: 2px solid #000; padding-top: 10px;">
      {{ instructor_name }}<br>
      <small>Instructor</small>
    </div>
  </div>
</div>
```

**Sample Data:**
```json
{
  "recipient_name": "John Doe",
  "course_name": "Advanced Web Development",
  "completion_date": "January 15, 2024",
  "instructor_name": "Dr. Jane Smith"
}
```

---

## 🎨 GrapesJS Tips

### Adding Components
1. **Drag from Blocks Panel** (left side)
2. **Click to add**: Text, Image, Video, Map, etc.
3. **Nest components**: Drag one inside another

### Styling
1. **Select component**: Click on it in canvas
2. **Edit in Style Manager** (right panel)
3. **Common properties**:
   - Typography: font-size, color, weight
   - Spacing: margin, padding
   - Dimensions: width, height
   - Background: color, image
   - Border: style, color, radius

### Using Variables
1. **Add text component**
2. **Double-click to edit**
3. **Type**: `{{ variable_name }}`
4. **Variables available from your data mapping**

### Responsive Design
1. **Click device icons** in toolbar
2. **Switch between**: Desktop, Tablet, Mobile
3. **Adjust styles per device**

---

## 🔧 API Endpoints

### Templates
- `GET /api/v1/pdf-templates/templates` - List
- `POST /api/v1/pdf-templates/templates` - Create
- `GET /api/v1/pdf-templates/templates/{id}` - Get
- `PUT /api/v1/pdf-templates/templates/{id}` - Update
- `DELETE /api/v1/pdf-templates/templates/{id}` - Delete

### Generation
- `POST /api/v1/pdf-templates/templates/{id}/generate` - Generate PDF
- `GET /api/v1/pdf-templates/downloads/{pdf_id}` - Download

### View Full API Documentation
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

---

## 🐛 Troubleshooting

### "WeasyPrint not found"
- Install system dependencies (see Step 1)
- Restart Python environment after installation

### "GrapesJS not loading"
- Check browser console for errors
- Ensure `ClientOnly` wrapper is used
- Clear cache and reload

### "Database error"
- Run migrations: `alembic upgrade head`
- Check database connection in `.env`

### "Template not saving"
- Check console for validation errors
- Ensure all required fields are filled
- Check slug is unique

### "PDF generation fails"
- Verify WeasyPrint is installed correctly
- Check template syntax (Jinja2)
- Validate JSON data format

---

## 📚 Learn More

- **Full Documentation**: See `PDF_TEMPLATES_README.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **GrapesJS Docs**: https://grapesjs.com/docs/
- **WeasyPrint Docs**: https://doc.courtbouillon.org/weasyprint/

---

## ✅ Checklist

Before going to production:

- [ ] Install all system dependencies
- [ ] Run database migrations
- [ ] Configure file storage path
- [ ] Set up backup for generated PDFs
- [ ] Configure PDF expiration policy
- [ ] Test on different browsers
- [ ] Test PDF generation with large data
- [ ] Set up monitoring for PDF generation
- [ ] Configure proper authentication
- [ ] Test multi-tenant isolation

---

## 🎉 You're Ready!

You now have a fully functional PDF template designer with:
- ✅ Visual drag-and-drop editor
- ✅ Dynamic data injection
- ✅ Version control
- ✅ PDF generation
- ✅ Download tracking

Start creating beautiful PDFs! 🚀
