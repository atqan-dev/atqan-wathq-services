# PDF Variable Replacement Fix Applied ✅

## Problem
Generated PDFs were showing variable placeholders like `{crNationalNumber}` and `{crNumber}/{name}` instead of actual values.

## Root Cause
The template was using **single curly braces** `{variable}` but the backend expected **double curly braces** `{{ variable }}` (Jinja2 format).

## Solution Applied
Updated `/api/app/services/pdf_generator.py` to automatically convert single braces to double braces before rendering.

### Code Changes
```python
def _render_template(self, html_content: str, data: Dict[str, Any]) -> str:
    import re
    
    # Convert {variable} to {{ variable }}
    def replace_single_braces(match):
        var_name = match.group(1)
        return f"{{{{ {var_name} }}}}"
    
    # Replace single braces with double braces
    html_content = re.sub(
        r'(?<!\{)\{([a-zA-Z_][a-zA-Z0-9_]*)\}(?!\})', 
        replace_single_braces, 
        html_content
    )
    
    # Render with Jinja2
    template = Template(html_content)
    return template.render(**data)
```

## How to Apply the Fix

### Step 1: Restart the API Server
```bash
cd /home/aziztech/Desktop/atqan-apps-2025/atqan-wathq-services
docker-compose restart api
```

Or if running directly:
```bash
cd api
# Kill the running process and restart
python -m uvicorn app.main:app --reload
```

### Step 2: Test the Fix

#### Option A: Use Existing Template (No Changes Needed)
Your template with `{crNationalNumber}` will now work automatically!

**Generate PDF with this data:**
```json
{
  "crNationalNumber": "1234567890",
  "crNumber": "CR-2024-001",
  "name": "Ahmed Mohammed"
}
```

#### Option B: Update Template (Recommended for Clarity)
For better clarity and to use Jinja2 features, update your template:

**Change from:**
```html
{crNationalNumber}
{crNumber}/{name}
```

**To:**
```html
{{ crNationalNumber }}
{{ crNumber }}/{{ name }}
```

## Testing Steps

### 1. Via Dashboard
1. Go to your PDF template detail page
2. Click "Generate PDF"
3. Enter this JSON data:
```json
{
  "crNationalNumber": "1234567890",
  "crNumber": "CR-2024-001",
  "name": "Ahmed Mohammed"
}
```
4. Click "Generate"
5. Download and verify the PDF shows actual values

### 2. Via API (curl)
```bash
curl -X POST "http://localhost:8000/api/v1/pdf-templates/templates/{template_id}/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "crNationalNumber": "1234567890",
      "crNumber": "CR-2024-001",
      "name": "Ahmed Mohammed"
    },
    "filename": "test-certificate.pdf"
  }'
```

### 3. Via API (Python)
```python
import requests

url = "http://localhost:8000/api/v1/pdf-templates/templates/{template_id}/generate"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
}
data = {
    "data": {
        "crNationalNumber": "1234567890",
        "crNumber": "CR-2024-001",
        "name": "Ahmed Mohammed"
    },
    "filename": "test-certificate.pdf"
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

## Expected Result

### Before Fix ❌
```
{crNationalNumber}
{crNumber}/{name}
```

### After Fix ✅
```
1234567890
CR-2024-001/Ahmed Mohammed
```

## Supported Variable Formats

The system now supports **both** formats:

### Format 1: Single Braces (Simple)
```html
{variableName}
{crNationalNumber}
{name}
```

### Format 2: Double Braces (Jinja2)
```html
{{ variableName }}
{{ crNationalNumber }}
{{ name }}
```

## Advanced Features (Using Double Braces)

With double braces, you can use Jinja2 features:

### Filters
```html
{{ name | upper }}              <!-- AHMED MOHAMMED -->
{{ price | round(2) }}          <!-- 99.99 -->
{{ date | default('N/A') }}     <!-- N/A if date is empty -->
```

### Conditionals
```html
{% if isActive %}
    <span>Active</span>
{% else %}
    <span>Inactive</span>
{% endif %}
```

### Loops
```html
{% for item in items %}
    <li>{{ item.name }}</li>
{% endfor %}
```

## Troubleshooting

### Issue: Still showing placeholders after fix

**Check 1: Variable names match exactly**
```javascript
// ❌ Wrong
Template: {customerName}
Data: { "customer_name": "Ahmed" }

// ✅ Correct
Template: {customerName}
Data: { "customerName": "Ahmed" }
```

**Check 2: Data is provided**
```json
{
  "crNationalNumber": "1234567890",  // ✅ Must be present
  "crNumber": "CR-2024-001",         // ✅ Must be present
  "name": "Ahmed Mohammed"           // ✅ Must be present
}
```

**Check 3: API server restarted**
```bash
docker-compose restart api
# or
systemctl restart your-api-service
```

### Issue: Some variables work, others don't

**Cause:** Variable name mismatch (case-sensitive)

**Solution:** Check exact spelling and case:
```html
{crNumber}     ✅ Correct
{crnumber}     ❌ Wrong
{CrNumber}     ❌ Wrong
{cr_number}    ❌ Wrong
```

### Issue: Special characters not displaying

**Cause:** Encoding issue

**Solution:** Ensure UTF-8 encoding in your data:
```json
{
  "name": "أحمد محمد",
  "description": "شهادة إتمام"
}
```

## Verification Checklist

- [ ] API server restarted
- [ ] Template has variables in format `{var}` or `{{ var }}`
- [ ] Data JSON has matching variable names (case-sensitive)
- [ ] Generated PDF downloaded successfully
- [ ] PDF shows actual values instead of placeholders

## Files Modified

1. **`/api/app/services/pdf_generator.py`**
   - Updated `_render_template()` method
   - Added regex to convert single to double braces
   - Backward compatible with existing templates

## Documentation

See detailed documentation in:
- `PDF_VARIABLE_SYNTAX.md` - Complete variable syntax guide
- `UI_IMPROVEMENTS.md` - UI/UX improvements documentation
- `DESIGN_CHANGES_SUMMARY.md` - Design changes summary

## Need Help?

If the issue persists after applying the fix:

1. Check API logs for errors:
```bash
docker-compose logs api
```

2. Verify the data being sent:
```bash
# Check network tab in browser DevTools
# Look for the POST request to /generate
```

3. Test with simple data first:
```json
{
  "test": "Hello World"
}
```

Template:
```html
<p>{test}</p>
```

Expected output:
```html
<p>Hello World</p>
```

## Summary

✅ **Fix applied** - Single braces `{var}` now work automatically  
✅ **Backward compatible** - Existing templates with `{{ var }}` still work  
✅ **No template changes required** - Your current template will work after API restart  
✅ **Enhanced features** - Can now use Jinja2 filters and conditionals  

**Next step:** Restart the API server and test!
