# National Address Export Implementation Summary

## Overview
Implemented complete export and print functionality for national addresses page matching the employee export implementation.

## Frontend Implementation ✅

### 1. Created Composable
**File:** `/dashboard/composables/useNationalAddressExport.ts`

**Functions:**
- `exportToPDF(addressId)` - Export as PDF
- `exportToJSON(addressId)` - Export as JSON
- `exportToCSV(addressId)` - Export as CSV
- `exportToExcel(addressId)` - Export as Excel
- `previewAddress(addressId)` - HTML preview in new tab
- `printAddress(addressId)` - Print dialog

**Features:**
- Native fetch API for binary downloads
- Authorization headers with JWT token
- Toast notifications for success/error
- Proper blob handling for file downloads

### 2. Updated National Address Detail Page
**File:** `/dashboard/pages/wathq-data/national-addresses/[id].vue`

**Changes:**
- Added export dropdown menu with 5 options
- Added print button
- Integrated `useNationalAddressExport` composable
- Export handlers for all formats

**UI Components:**
```vue
<!-- Export Dropdown -->
<UDropdown :items="exportMenuItems">
  <UButton icon="i-heroicons-arrow-down-tray" color="primary" trailing-icon="i-heroicons-chevron-down">
    Export
  </UButton>
</UDropdown>

<!-- Print Button -->
<UButton icon="i-heroicons-printer" color="gray" variant="outline" @click="handlePrint">
  Print
</UButton>
```

## Backend Implementation Needed

### Required Endpoints (to be added to `wathq_pdf_export.py`)

```python
# 1. PDF Export
@router.get("/database/national-address/{address_id}/pdf")
async def export_database_national_address_pdf(address_id: str, db: Session, current_user)

# 2. HTML Preview
@router.get("/database/national-address/{address_id}/preview")
async def preview_database_national_address_html(address_id: str, db: Session, current_user)

# 3. JSON Export
@router.get("/database/national-address/{address_id}/json")
async def export_database_national_address_json(address_id: str, db: Session, current_user)

# 4. CSV Export
@router.get("/database/national-address/{address_id}/csv")
async def export_database_national_address_csv(address_id: str, db: Session, current_user)

# 5. Excel Export
@router.get("/database/national-address/{address_id}/excel")
async def export_database_national_address_excel(address_id: str, db: Session, current_user)
```

### Required Template
**File:** `/api/templates/national_address_database_template_v2.html`

**Template Structure:**
- Copy from `cr_database_template_v2.html` for consistent design
- Replace with national address fields:
  - Address ID (pk_address_id)
  - Title
  - Full Address (address, address2)
  - Building Number, Street, Unit Number
  - District, City, Post Code
  - Region Information
  - Coordinates (latitude, longitude)
  - Status
  - Primary Address flag
  - Restriction (if any)

### Database Model
**Table:** `wathq.national_addresses`

**Key Fields:**
- pk_address_id (Primary Key)
- title
- address, address2
- building_number, street, unit_number, additional_number
- district, district_id
- city, city_id
- post_code
- region_name, region_id
- latitude, longitude
- is_primary_address
- status
- restriction
- created_at, updated_at

## Implementation Steps for Backend

1. **Add import for NationalAddress model**
2. **Create 5 export endpoints** (PDF, Preview, JSON, CSV, Excel)
3. **Create HTML template** based on CR design
4. **Handle encoding** (UTF-8 with BOM for CSV, URL-encoded filenames)
5. **Test all formats**

## File Naming Convention
- PDF: `national_address_{address_id}.pdf`
- JSON: `national_address_{address_id}.json`
- CSV: `national_address_{address_id}.csv`
- Excel: `national_address_{address_id}.xlsx`

## Features Implemented

### Frontend ✅
- Export dropdown with 5 formats
- Print button
- Native fetch for binary downloads
- Toast notifications
- Error handling
- Proper authentication

### Backend ⏳ (Pending)
- PDF generation with template
- HTML preview rendering
- JSON serialization
- CSV export with UTF-8 BOM
- Excel export with styling
- URL-encoded filenames

## Testing Checklist

- [ ] PDF export downloads correctly
- [ ] Preview opens in new tab with proper styling
- [ ] JSON export contains all address data
- [ ] CSV export opens correctly in Excel with Arabic text
- [ ] Excel export has professional styling
- [ ] Print dialog opens and prints correctly
- [ ] All exports handle missing data gracefully
- [ ] Authentication works for all endpoints
- [ ] Error messages display properly

## Notes

- Frontend implementation is complete and ready
- Backend endpoints follow same pattern as employee exports
- Template should match CR design for consistency
- All encoding issues handled (UTF-8, URL encoding)
- Uses native fetch API to avoid Nuxt proxy issues

## Next Steps

1. Create backend endpoints in `wathq_pdf_export.py`
2. Create HTML template `national_address_database_template_v2.html`
3. Test all export formats
4. Verify Arabic text displays correctly
5. Test print functionality

## Related Files

**Frontend:**
- `/dashboard/composables/useNationalAddressExport.ts`
- `/dashboard/pages/wathq-data/national-addresses/[id].vue`

**Backend (to be created):**
- `/api/app/api/v1/endpoints/wathq_pdf_export.py` (add endpoints)
- `/api/templates/national_address_database_template_v2.html` (create template)

**Reference Implementation:**
- Employee export: `/dashboard/composables/useEmployeeExport.ts`
- Employee template: `/api/templates/employee_database_template_v2.html`
- Employee endpoints: Lines 1195-1797 in `wathq_pdf_export.py`
