# National Address Export Backend Implementation

## Add these endpoints to `/api/app/api/v1/endpoints/wathq_pdf_export.py`

Add at the end of the file (after line 1807):

```python
# ============================================================================
# NATIONAL ADDRESS EXPORT ENDPOINTS
# ============================================================================

@router.get("/database/national-address/{address_id}/pdf")
async def export_database_national_address_pdf(
    address_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User | models.ManagementUser = Depends(
        deps.get_current_active_user_or_management
    ),
) -> Response:
    """Export National Address PDF from database record"""
    try:
        from app.models.wathq_national_address import Address
        from jinja2 import Template
        from datetime import datetime as dt
        from urllib.parse import quote
        import pdfkit

        # Fetch address from database
        address = db.query(Address).filter(Address.pk_address_id == address_id).first()

        if not address:
            raise HTTPException(
                status_code=404, detail=f"Address with ID {address_id} not found"
            )

        # Load template
        template_path = pdf_service.templates_dir / "national_address_database_template_v2.html"
        if not template_path.exists():
            raise HTTPException(status_code=500, detail="National address template not found")

        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        template = Template(template_content)

        template_data = {
            "document_title": f"العنوان الوطني - {address.title or address_id}",
            "search_date": (
                address.fetched_at.strftime("%Y-%m-%d")
                if address.fetched_at
                else dt.now().strftime("%Y-%m-%d")
            ),
            "print_date": dt.now().strftime("%Y-%m-%d"),
            "pk_address_id": address.pk_address_id,
            "title": address.title,
            "address": address.address,
            "address2": address.address2,
            "building_number": address.building_number,
            "street": address.street,
            "unit_number": address.unit_number,
            "additional_number": address.additional_number,
            "district": address.district,
            "district_id": address.district_id,
            "city": address.city,
            "city_id": address.city_id,
            "post_code": address.post_code,
            "region_name": address.region_name,
            "region_id": address.region_id,
            "latitude": f"{address.latitude:.6f}" if address.latitude else None,
            "longitude": f"{address.longitude:.6f}" if address.longitude else None,
            "is_primary_address": address.is_primary_address,
            "status": address.status,
            "restriction": address.restriction,
            "fetched_at": (
                address.fetched_at.strftime("%Y-%m-%d %H:%M:%S")
                if address.fetched_at
                else "غير محدد"
            ),
        }

        html_content = template.render(**template_data)

        # Generate PDF
        pdf_options = {
            "page-size": "A4",
            "margin-top": "0mm",
            "margin-right": "0mm",
            "margin-bottom": "0mm",
            "margin-left": "0mm",
            "encoding": "UTF-8",
            "enable-local-file-access": None,
            "print-media-type": None,
            "orientation": "portrait",
        }

        pdf_bytes = pdfkit.from_string(html_content, False, options=pdf_options)

        filename = f"national_address_{address_id}.pdf"
        encoded_filename = quote(filename)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate national address PDF: {str(e)}"
        )


@router.get("/database/national-address/{address_id}/preview")
async def preview_database_national_address_html(
    address_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User | models.ManagementUser = Depends(
        deps.get_current_active_user_or_management
    ),
) -> Response:
    """Preview National Address HTML"""
    try:
        from app.models.wathq_national_address import Address
        from jinja2 import Template
        from datetime import datetime as dt

        address = db.query(Address).filter(Address.pk_address_id == address_id).first()

        if not address:
            raise HTTPException(
                status_code=404, detail=f"Address with ID {address_id} not found"
            )

        template_path = pdf_service.templates_dir / "national_address_database_template_v2.html"
        if not template_path.exists():
            raise HTTPException(status_code=500, detail="National address template not found")

        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        template = Template(template_content)

        template_data = {
            "document_title": f"العنوان الوطني - {address.title or address_id}",
            "search_date": (
                address.fetched_at.strftime("%Y-%m-%d")
                if address.fetched_at
                else dt.now().strftime("%Y-%m-%d")
            ),
            "print_date": dt.now().strftime("%Y-%m-%d"),
            "pk_address_id": address.pk_address_id,
            "title": address.title,
            "address": address.address,
            "address2": address.address2,
            "building_number": address.building_number,
            "street": address.street,
            "unit_number": address.unit_number,
            "additional_number": address.additional_number,
            "district": address.district,
            "district_id": address.district_id,
            "city": address.city,
            "city_id": address.city_id,
            "post_code": address.post_code,
            "region_name": address.region_name,
            "region_id": address.region_id,
            "latitude": f"{address.latitude:.6f}" if address.latitude else None,
            "longitude": f"{address.longitude:.6f}" if address.longitude else None,
            "is_primary_address": address.is_primary_address,
            "status": address.status,
            "restriction": address.restriction,
            "fetched_at": (
                address.fetched_at.strftime("%Y-%m-%d %H:%M:%S")
                if address.fetched_at
                else "غير محدد"
            ),
        }

        html_content = template.render(**template_data)

        return Response(content=html_content, media_type="text/html")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate national address preview: {str(e)}"
        )


@router.get("/database/national-address/{address_id}/json")
async def export_database_national_address_json(
    address_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User | models.ManagementUser = Depends(
        deps.get_current_active_user_or_management
    ),
) -> Response:
    """Export National Address data as JSON"""
    try:
        from app.models.wathq_national_address import Address
        from urllib.parse import quote
        import json

        address = db.query(Address).filter(Address.pk_address_id == address_id).first()

        if not address:
            raise HTTPException(
                status_code=404, detail=f"Address with ID {address_id} not found"
            )

        address_data = {
            "pk_address_id": address.pk_address_id,
            "title": address.title,
            "address": address.address,
            "address2": address.address2,
            "building_number": address.building_number,
            "street": address.street,
            "unit_number": address.unit_number,
            "additional_number": address.additional_number,
            "district": address.district,
            "district_id": address.district_id,
            "city": address.city,
            "city_id": address.city_id,
            "post_code": address.post_code,
            "region_name": address.region_name,
            "region_id": address.region_id,
            "latitude": float(address.latitude) if address.latitude else None,
            "longitude": float(address.longitude) if address.longitude else None,
            "is_primary_address": address.is_primary_address,
            "status": address.status,
            "restriction": address.restriction,
            "fetched_at": address.fetched_at.isoformat() if address.fetched_at else None,
            "created_at": address.created_at.isoformat() if address.created_at else None,
            "updated_at": address.updated_at.isoformat() if address.updated_at else None,
        }

        json_content = json.dumps(address_data, ensure_ascii=False, indent=2)

        filename = f"national_address_{address_id}.json"
        encoded_filename = quote(filename)

        return Response(
            content=json_content,
            media_type="application/json; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to export national address JSON: {str(e)}"
        )


@router.get("/database/national-address/{address_id}/csv")
async def export_database_national_address_csv(
    address_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User | models.ManagementUser = Depends(
        deps.get_current_active_user_or_management
    ),
) -> Response:
    """Export National Address data as CSV with UTF-8 encoding"""
    try:
        from app.models.wathq_national_address import Address
        from urllib.parse import quote
        import csv
        from io import StringIO

        address = db.query(Address).filter(Address.pk_address_id == address_id).first()

        if not address:
            raise HTTPException(
                status_code=404, detail=f"Address with ID {address_id} not found"
            )

        output = StringIO()
        writer = csv.writer(output)

        # Write address information
        writer.writerow(["National Address Information"])
        writer.writerow(["Field", "Value"])
        writer.writerow(["Address ID", address.pk_address_id or ""])
        writer.writerow(["Title", address.title or ""])
        writer.writerow(["Address", address.address or ""])
        writer.writerow(["Address 2", address.address2 or ""])
        writer.writerow(["Building Number", address.building_number or ""])
        writer.writerow(["Street", address.street or ""])
        writer.writerow(["Unit Number", address.unit_number or ""])
        writer.writerow(["Additional Number", address.additional_number or ""])
        writer.writerow(["District", address.district or ""])
        writer.writerow(["District ID", address.district_id or ""])
        writer.writerow(["City", address.city or ""])
        writer.writerow(["City ID", address.city_id or ""])
        writer.writerow(["Post Code", address.post_code or ""])
        writer.writerow(["Region", address.region_name or ""])
        writer.writerow(["Region ID", address.region_id or ""])
        writer.writerow(["Latitude", f"{address.latitude:.6f}" if address.latitude else ""])
        writer.writerow(["Longitude", f"{address.longitude:.6f}" if address.longitude else ""])
        writer.writerow(["Primary Address", "Yes" if address.is_primary_address else "No"])
        writer.writerow(["Status", address.status or ""])
        writer.writerow(["Restriction", address.restriction or ""])
        writer.writerow([
            "Fetched At",
            address.fetched_at.strftime("%Y-%m-%d %H:%M:%S") if address.fetched_at else ""
        ])

        csv_content = output.getvalue()
        output.close()

        # Add UTF-8 BOM for Excel
        csv_bytes = "\ufeff".encode("utf-8") + csv_content.encode("utf-8")

        filename = f"national_address_{address_id}.csv"
        encoded_filename = quote(filename)

        return Response(
            content=csv_bytes,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to export national address CSV: {str(e)}"
        )


@router.get("/database/national-address/{address_id}/excel")
async def export_database_national_address_excel(
    address_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User | models.ManagementUser = Depends(
        deps.get_current_active_user_or_management
    ),
) -> Response:
    """Export National Address data as Excel (XLSX)"""
    try:
        from app.models.wathq_national_address import Address
        from urllib.parse import quote
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
        from io import BytesIO

        address = db.query(Address).filter(Address.pk_address_id == address_id).first()

        if not address:
            raise HTTPException(
                status_code=404, detail=f"Address with ID {address_id} not found"
            )

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "National Address"

        # Header styling
        header_fill = PatternFill(start_color="004074", end_color="004074", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True, size=12)
        header_alignment = Alignment(horizontal="center", vertical="center")

        # Title
        ws.merge_cells("A1:B1")
        ws["A1"] = "National Address Information"
        ws["A1"].fill = header_fill
        ws["A1"].font = header_font
        ws["A1"].alignment = header_alignment

        # Data rows
        row = 3
        data_rows = [
            ("Address ID", address.pk_address_id),
            ("Title", address.title),
            ("Address", address.address),
            ("Address 2", address.address2),
            ("Building Number", address.building_number),
            ("Street", address.street),
            ("Unit Number", address.unit_number),
            ("Additional Number", address.additional_number),
            ("District", address.district),
            ("District ID", address.district_id),
            ("City", address.city),
            ("City ID", address.city_id),
            ("Post Code", address.post_code),
            ("Region", address.region_name),
            ("Region ID", address.region_id),
            ("Latitude", f"{address.latitude:.6f}" if address.latitude else ""),
            ("Longitude", f"{address.longitude:.6f}" if address.longitude else ""),
            ("Primary Address", "Yes" if address.is_primary_address else "No"),
            ("Status", address.status),
            ("Restriction", address.restriction),
            ("Fetched At", address.fetched_at.strftime("%Y-%m-%d %H:%M:%S") if address.fetched_at else ""),
        ]

        for label, value in data_rows:
            ws[f"A{row}"] = label
            ws[f"B{row}"] = value or ""
            ws[f"A{row}"].font = Font(bold=True)
            row += 1

        # Column widths
        ws.column_dimensions["A"].width = 25
        ws.column_dimensions["B"].width = 50

        # Save to BytesIO
        excel_file = BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)

        filename = f"national_address_{address_id}.xlsx"
        encoded_filename = quote(filename)

        return Response(
            content=excel_file.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to export national address Excel: {str(e)}"
        )
```

## Next: Create the HTML template

Create file: `/api/templates/national_address_database_template_v2.html`

Copy from `employee_database_template_v2.html` and replace the employee section with national address fields as shown in the template_data above.

The template should include:
- Header with address title
- Address Information section (all address fields)
- Location Information section (coordinates, region)
- Status and restriction information
