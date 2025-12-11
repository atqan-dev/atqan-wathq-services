# PDF Template Variable Syntax Guide

## Overview
The PDF template system now supports **both** single and double curly brace syntax for variables, making it more flexible and user-friendly.

## Supported Syntax

### Option 1: Single Curly Braces (Simple)
```html
{variableName}
{crNationalNumber}
{crNumber}
{name}
```

### Option 2: Double Curly Braces (Jinja2 Standard)
```html
{{ variableName }}
{{ crNationalNumber }}
{{ crNumber }}
{{ name }}
```

**Both formats work!** The system automatically converts single braces to double braces before rendering.

## Variable Naming Rules

Variables must follow these rules:
- Start with a letter or underscore: `a-z`, `A-Z`, `_`
- Can contain letters, numbers, and underscores: `a-z`, `A-Z`, `0-9`, `_`
- Case-sensitive: `{name}` is different from `{Name}`

### ✅ Valid Variable Names
```html
{name}
{firstName}
{first_name}
{customer_id}
{_privateVar}
{item1}
```

### ❌ Invalid Variable Names
```html
{1name}          <!-- Cannot start with number -->
{first-name}     <!-- Hyphens not allowed -->
{first name}     <!-- Spaces not allowed -->
{first.name}     <!-- Dots not allowed -->
```

## Example Template

### HTML Template
```html
<!DOCTYPE html>
<html>
<head>
    <title>Certificate</title>
</head>
<body>
    <h1>Certificate of Completion</h1>
    
    <p>This certifies that <strong>{name}</strong></p>
    <p>National ID: {crNationalNumber}</p>
    <p>Registration: {crNumber}</p>
    
    <p>Date: {issueDate}</p>
    <p>Valid until: {expiryDate}</p>
</body>
</html>
```

### Sample Data (JSON)
```json
{
  "name": "Ahmed Mohammed",
  "crNationalNumber": "1234567890",
  "crNumber": "CR-2024-001",
  "issueDate": "2024-10-20",
  "expiryDate": "2025-10-20"
}
```

### Generated Output
```html
<!DOCTYPE html>
<html>
<head>
    <title>Certificate</title>
</head>
<body>
    <h1>Certificate of Completion</h1>
    
    <p>This certifies that <strong>Ahmed Mohammed</strong></p>
    <p>National ID: 1234567890</p>
    <p>Registration: CR-2024-001</p>
    
    <p>Date: 2024-10-20</p>
    <p>Valid until: 2025-10-20</p>
</body>
</html>
```

## Advanced Features (Jinja2)

If you use double curly braces `{{ }}`, you can access advanced Jinja2 features:

### 1. Filters
```html
{{ name | upper }}           <!-- AHMED MOHAMMED -->
{{ name | lower }}           <!-- ahmed mohammed -->
{{ name | title }}           <!-- Ahmed Mohammed -->
{{ price | round(2) }}       <!-- 99.99 -->
```

### 2. Default Values
```html
{{ name | default('Unknown') }}
{{ email | default('N/A') }}
```

### 3. Conditional Display
```html
{% if isActive %}
    <p>Status: Active</p>
{% else %}
    <p>Status: Inactive</p>
{% endif %}
```

### 4. Loops
```html
<ul>
{% for item in items %}
    <li>{{ item.name }} - {{ item.price }}</li>
{% endfor %}
</ul>
```

### 5. Nested Variables
```html
{{ customer.name }}
{{ customer.address.city }}
{{ order.items[0].name }}
```

## Common Issues & Solutions

### Issue 1: Variables Not Replaced
**Problem:** PDF shows `{variableName}` instead of actual value

**Solutions:**
1. ✅ Check variable name matches exactly (case-sensitive)
2. ✅ Ensure data is provided in the JSON
3. ✅ Verify variable name follows naming rules

**Example:**
```javascript
// ❌ Wrong - variable name mismatch
Template: {customerName}
Data: { "customer_name": "Ahmed" }

// ✅ Correct - names match
Template: {customerName}
Data: { "customerName": "Ahmed" }
```

### Issue 2: Special Characters in Values
**Problem:** Arabic text or special characters not displaying

**Solution:** Ensure proper encoding in your data
```json
{
  "name": "أحمد محمد",
  "description": "شهادة إتمام"
}
```

### Issue 3: Missing Variables
**Problem:** Some variables are undefined

**Solution:** Use default values
```html
{{ name | default('N/A') }}
{{ email | default('Not provided') }}
```

## Best Practices

### 1. Use Descriptive Variable Names
```html
<!-- ❌ Bad -->
{n}
{d}
{x}

<!-- ✅ Good -->
{customerName}
{issueDate}
{certificateNumber}
```

### 2. Provide Sample Data
Always include sample data in your template for testing:
```json
{
  "customerName": "John Doe",
  "certificateNumber": "CERT-001",
  "issueDate": "2024-10-20"
}
```

### 3. Document Your Variables
Add comments in your data mapping:
```json
{
  "data_mapping": {
    "customerName": "string - Full name of the customer",
    "crNumber": "string - Commercial registration number",
    "issueDate": "string - Date in YYYY-MM-DD format"
  }
}
```

### 4. Handle Missing Data
Always provide defaults for optional fields:
```html
<p>Email: {{ email | default('Not provided') }}</p>
<p>Phone: {{ phone | default('N/A') }}</p>
```

### 5. Test with Real Data
Before deploying, test your template with actual data to ensure all variables are replaced correctly.

## API Usage

### Generate PDF with Data
```bash
POST /api/v1/pdf-templates/templates/{template_id}/generate
Content-Type: application/json

{
  "data": {
    "name": "Ahmed Mohammed",
    "crNationalNumber": "1234567890",
    "crNumber": "CR-2024-001",
    "issueDate": "2024-10-20"
  },
  "filename": "certificate.pdf"
}
```

### Response
```json
{
  "pdf": {
    "id": "uuid",
    "filename": "certificate.pdf",
    "file_size": 45678,
    "created_at": "2024-10-20T00:00:00Z"
  },
  "download_url": "/api/v1/pdf-templates/downloads/uuid"
}
```

## Troubleshooting

### Debug Mode
To see what variables are being replaced, check the generated HTML before PDF conversion:

1. Generate PDF with your data
2. Check the `grapesjs_html` field in the response
3. Verify all variables are replaced

### Common Errors

**Error:** `Template syntax error`
- **Cause:** Invalid Jinja2 syntax
- **Fix:** Check for unclosed tags or invalid expressions

**Error:** `Variable not found`
- **Cause:** Variable name mismatch
- **Fix:** Ensure variable names match exactly (case-sensitive)

**Error:** `Invalid JSON data`
- **Cause:** Malformed JSON in data field
- **Fix:** Validate JSON syntax before sending

## Support

For more information about Jinja2 templating:
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Template Designer Documentation](https://jinja.palletsprojects.com/en/3.0.x/templates/)

## Changelog

### v1.1.0 (2024-10-20)
- ✅ Added support for single curly braces `{var}`
- ✅ Automatic conversion from `{var}` to `{{ var }}`
- ✅ Backward compatible with existing templates
- ✅ Improved error messages for variable issues
