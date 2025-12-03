# WATHQ PDF Integration Test Guide

## Overview
This guide helps you test the new WATHQ PDF template integration with the commercial registration page.

## Prerequisites
1. API server running on port 5551
2. Dashboard running on port 4551
3. Valid WATHQ API credentials configured
4. User authenticated in the dashboard

## Test Steps

### 1. Test PDF Export Feature

1. **Navigate to Commercial Registration Page**
   - Go to `http://localhost:4551/wathq/commercial-registration`
   - Login if not already authenticated

2. **Test API Endpoint**
   - Select "Full Info" endpoint from the dropdown
   - Enter a valid CR ID (e.g., `1010711252`)
   - Click "Send Request"
   - Wait for response data

3. **Export PDF**
   - Click the red "Export PDF" button in the response section
   - Should download a PDF file named `commercial_registration_{cr_id}.pdf`
   - PDF should use the new modern template with:
     - Blue header line
     - Orange accent section
     - Company logo and text
     - Professional Arabic formatting
     - WATHQ data displayed in organized sections

### 2. Test PDF Preview Feature

1. **Preview PDF**
   - After getting a successful response, click the purple "Preview" button
   - Should open a new browser window/tab
   - Should display HTML preview of the PDF with the new template design
   - Check for proper Arabic RTL layout and branding

### 3. Test Other Services

1. **Test Non-CR Services**
   - Navigate to other WATHQ service pages (if available)
   - Test PDF export and preview
   - Should use the new template with generic WATHQ data display

### 4. Verify Template Features

**Check PDF Content:**
- [ ] Header with blue line and orange accent
- [ ] Company logo and Arabic/English text
- [ ] Professional document title
- [ ] WATHQ data in organized format
- [ ] Watermark with "وثق" text
- [ ] Footer with contact information
- [ ] Signature section
- [ ] Proper Arabic font (Tahoma)

**Check Functionality:**
- [ ] PDF downloads correctly
- [ ] Preview opens in new window
- [ ] Authentication works for both features
- [ ] Error handling for failed requests
- [ ] Loading states during generation

## Expected Results

### PDF Export
- File downloads automatically
- Filename: `commercial_registration_{cr_id}.pdf`
- File size: ~20-50KB (depending on data)
- Professional appearance matching company branding

### PDF Preview
- Opens in new browser window
- Shows HTML version of PDF layout
- Proper Arabic text rendering
- All WATHQ data displayed clearly

## Troubleshooting

### Common Issues

1. **"Template not found" error**
   - Ensure `wathq-modern-template.html` exists in `/api/templates/`
   - Check template assets are in `/api/templates/assets/`

2. **Authentication errors**
   - Verify user is logged in
   - Check API token is valid
   - Ensure proper CORS settings

3. **PDF generation fails**
   - Check WeasyPrint is installed
   - Verify template syntax is correct
   - Check server logs for detailed errors

4. **Preview window blocked**
   - Allow popups for the dashboard domain
   - Check browser popup blocker settings

### Debug Steps

1. **Check Browser Console**
   ```javascript
   // Look for errors in browser console
   console.log('PDF export clicked')
   ```

2. **Check Network Tab**
   - Verify API calls to `/wathq/pdf/` endpoints
   - Check response status codes
   - Verify authentication headers

3. **Check Server Logs**
   - Look for template loading errors
   - Check PDF generation errors
   - Verify WATHQ API responses

## Success Criteria

✅ **Integration Successful When:**
- PDF export downloads file with new template design
- Preview shows proper HTML layout
- All WATHQ data is displayed correctly
- Arabic text renders properly
- Company branding is visible
- No console errors or API failures

## Next Steps

After successful testing:
1. Test with different CR IDs and data sets
2. Test with different user roles (tenant vs management)
3. Test error scenarios (invalid CR IDs, API failures)
4. Performance testing with large data sets
5. Cross-browser compatibility testing
