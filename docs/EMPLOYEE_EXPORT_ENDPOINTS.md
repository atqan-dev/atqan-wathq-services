# Employee Export Endpoints Documentation

## Overview
Comprehensive export functionality for wathq-data/employees with the same template structure as `cr_database_template_v2.html`.

## Endpoints

### 1. PDF Export
**Endpoint:** `GET /api/v1/wathq/pdf/database/employee/{employee_id}/pdf`

**Description:** Exports employee data as a professionally formatted PDF document.

**Response:** PDF file download

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/wathq/pdf/database/employee/1/pdf" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output employee_1.pdf
```

---

### 2. HTML Preview
**Endpoint:** `GET /api/v1/wathq/pdf/database/employee/{employee_id}/preview`

**Description:** Previews employee data as HTML with embedded export buttons.

**Response:** HTML content

**Features:**
- Interactive preview
- Export buttons for PDF, JSON, CSV, Excel
- Print functionality

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/wathq/pdf/database/employee/1/preview" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 3. JSON Export
**Endpoint:** `GET /api/v1/wathq/pdf/database/employee/{employee_id}/json`

**Description:** Exports employee data as structured JSON.

**Response:** JSON file download

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/wathq/pdf/database/employee/1/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output employee_1.json
```

**Sample Response:**
```json
{
  "employee_id": 1,
  "name": "أحمد محمد",
  "nationality": "سعودي",
  "working_months": 24,
  "fetched_at": "2025-02-03T15:30:00",
  "created_at": "2025-01-01T10:00:00",
  "updated_at": "2025-02-03T15:30:00",
  "employment_details": [
    {
      "employment_id": 1,
      "employer": "شركة الاتقان",
      "status": "نشط",
      "basic_wage": 5000.00,
      "housing_allowance": 1500.00,
      "other_allowance": 500.00,
      "full_wage": 7000.00
    }
  ]
}
```

---

### 4. CSV Export
**Endpoint:** `GET /api/v1/wathq/pdf/database/employee/{employee_id}/csv`

**Description:** Exports employee data as CSV format.

**Response:** CSV file download

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/wathq/pdf/database/employee/1/csv" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output employee_1.csv
```

**CSV Structure:**
```csv
Employee Information
Field,Value
Employee ID,1
Name,أحمد محمد
Nationality,سعودي
Working Months,24
Fetched At,2025-02-03 15:30:00

Employment Details
Employer,Status,Basic Wage,Housing Allowance,Other Allowance,Full Wage
شركة الاتقان,نشط,5000.00,1500.00,500.00,7000.00
```

---

### 5. Excel Export
**Endpoint:** `GET /api/v1/wathq/pdf/database/employee/{employee_id}/excel`

**Description:** Exports employee data as Excel (XLSX) with professional formatting.

**Response:** Excel file download

**Features:**
- Styled headers with company colors (#004074)
- Section separators
- Proper column widths
- Formatted numbers

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/wathq/pdf/database/employee/1/excel" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output employee_1.xlsx
```

---

## Template Details

### Template File
`/api/templates/employee_database_template.html`

### Template Features
- **RTL Support:** Full Arabic language support
- **Responsive Design:** A4 page format (210mm x 297mm)
- **Professional Styling:** Matches CR template design
- **Watermark:** Company logo watermark
- **Print Optimized:** CSS print media queries

### Template Sections
1. **Header Section:**
   - Document title
   - Employee name
   - Metadata (Employee ID, search date, print date, page number)

2. **Employee Information:**
   - Name
   - Nationality
   - Working months
   - Fetched date

3. **Employment Details Table:**
   - Employer
   - Status (with badge styling)
   - Basic wage
   - Housing allowance
   - Other allowance
   - Full wage

---

## Database Schema

### Employee Table (wathq.employees)
```python
class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = {"schema": "wathq"}
    
    employee_id = Column(Integer, primary_key=True)
    log_id = Column(UUID(as_uuid=True), ForeignKey("wathq_call_logs.id"))
    fetched_at = Column(DateTime(timezone=True))
    name = Column(String(255))
    nationality = Column(String(100))
    working_months = Column(Integer)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    
    employment_details = relationship("EmploymentDetail", back_populates="employee")
```

### Employment Detail Table (wathq.employment_details)
```python
class EmploymentDetail(Base):
    __tablename__ = "employment_details"
    __table_args__ = {"schema": "wathq"}
    
    employment_id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("wathq.employees.employee_id"))
    employer = Column(String(255))
    status = Column(String(50))
    basic_wage = Column(Numeric(12, 2))
    housing_allowance = Column(Numeric(12, 2))
    other_allowance = Column(Numeric(12, 2))
    full_wage = Column(Numeric(12, 2))
    
    employee = relationship("Employee", back_populates="employment_details")
```

---

## Authentication
All endpoints require authentication using Bearer token:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

Supports both:
- Regular users (tenant-specific)
- Management users (global access)

---

## Error Handling

### 404 Not Found
```json
{
  "detail": "Employee with ID {employee_id} not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to generate employee PDF: {error_message}"
}
```

---

## Print Functionality

The preview endpoint includes a print button that triggers the browser's print dialog:
```javascript
function printDocument() {
  window.print();
}
```

The template includes print-optimized CSS:
```css
@media print {
  body {
    padding: 0;
    background: white;
    margin: 0;
  }
  
  .page {
    margin: 0 !important;
    box-shadow: none;
    page-break-after: always;
  }
  
  @page {
    size: A4;
    margin: 0 !important;
  }
}
```

---

## Integration Example

### Frontend Integration (Vue.js/Nuxt)
```javascript
// Export to PDF
async function exportEmployeePDF(employeeId) {
  const response = await fetch(
    `/api/v1/wathq/pdf/database/employee/${employeeId}/pdf`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `employee_${employeeId}.pdf`;
  a.click();
}

// Preview in new window
function previewEmployee(employeeId) {
  window.open(
    `/api/v1/wathq/pdf/database/employee/${employeeId}/preview`,
    '_blank'
  );
}

// Export to JSON
async function exportEmployeeJSON(employeeId) {
  window.location.href = 
    `/api/v1/wathq/pdf/database/employee/${employeeId}/json`;
}

// Export to CSV
async function exportEmployeeCSV(employeeId) {
  window.location.href = 
    `/api/v1/wathq/pdf/database/employee/${employeeId}/csv`;
}

// Export to Excel
async function exportEmployeeExcel(employeeId) {
  window.location.href = 
    `/api/v1/wathq/pdf/database/employee/${employeeId}/excel`;
}
```

---

## Dependencies

### Required Python Packages
- `pdfkit` - PDF generation
- `jinja2` - Template rendering
- `openpyxl` - Excel file generation
- `sqlalchemy` - Database ORM

### System Dependencies
- `wkhtmltopdf` - Required for pdfkit

---

## Testing

### Manual Testing
```bash
# 1. Get employee list
curl -X GET "http://localhost:8000/api/v1/wathq-data/employees" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 2. Preview employee
curl -X GET "http://localhost:8000/api/v1/wathq/pdf/database/employee/1/preview" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Export PDF
curl -X GET "http://localhost:8000/api/v1/wathq/pdf/database/employee/1/pdf" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output employee.pdf

# 4. Export JSON
curl -X GET "http://localhost:8000/api/v1/wathq/pdf/database/employee/1/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output employee.json

# 5. Export CSV
curl -X GET "http://localhost:8000/api/v1/wathq/pdf/database/employee/1/csv" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output employee.csv

# 6. Export Excel
curl -X GET "http://localhost:8000/api/v1/wathq/pdf/database/employee/1/excel" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output employee.xlsx
```

---

## Files Modified/Created

### Created Files
1. `/api/templates/employee_database_template.html` - Employee HTML template

### Modified Files
1. `/api/app/api/v1/endpoints/wathq_pdf_export.py` - Added 5 new endpoints

### Existing Files (Referenced)
1. `/api/app/models/wathq_employee.py` - Employee and EmploymentDetail models
2. `/api/app/api/v1/endpoints/wathq_employees.py` - Employee CRUD endpoints

---

## Notes

- Template design matches `cr_database_template_v2.html` styling
- All exports use the same data source (wathq schema)
- Employment details are eagerly loaded using SQLAlchemy joinedload
- Numeric values are properly formatted (2 decimal places)
- Arabic text is fully supported in all export formats
- Excel export includes professional styling with company colors
