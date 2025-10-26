"""
WATHQ export endpoints for downloading data in various formats.
"""

from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from app.core.wathq_export import (
    export_wathq_to_xls,
    export_wathq_records_to_xls,
    export_wathq_with_nested_sheets
)

router = APIRouter()


@router.get("/offline-data/export-xls/{data_id}")
def export_offline_data_xls(
    data_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Export a single offline WATHQ data record to XLS format.
    """
    # Get offline data
    offline_data = db.query(models.WathqOfflineData).filter(
        models.WathqOfflineData.id == data_id,
        models.WathqOfflineData.tenant_id == current_user.tenant_id
    ).first()
    
    if not offline_data:
        raise HTTPException(status_code=404, detail="Offline data not found")

    # Export to XLS
    xls_file = export_wathq_to_xls(offline_data.response_body)
    
    return StreamingResponse(
        iter([xls_file.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=wathq_data_{data_id}.xlsx"}
    )


@router.get("/offline-data/export-xls-nested/{data_id}")
def export_offline_data_xls_nested(
    data_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Export a single offline WATHQ data record to XLS format with nested objects in separate sheets.
    """
    # Get offline data
    offline_data = db.query(models.WathqOfflineData).filter(
        models.WathqOfflineData.id == data_id,
        models.WathqOfflineData.tenant_id == current_user.tenant_id
    ).first()
    
    if not offline_data:
        raise HTTPException(status_code=404, detail="Offline data not found")

    # Export to XLS with nested sheets
    xls_file = export_wathq_with_nested_sheets(offline_data.response_body)
    
    return StreamingResponse(
        iter([xls_file.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=wathq_data_detailed_{data_id}.xlsx"}
    )


@router.get("/offline-data/export-xls-batch")
def export_offline_data_batch_xls(
    service_id: UUID = Query(..., description="Service ID to filter by"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Export multiple offline WATHQ data records to XLS format.
    """
    # Get offline data for service and tenant
    offline_data_list = db.query(models.WathqOfflineData).filter(
        models.WathqOfflineData.service_id == service_id,
        models.WathqOfflineData.tenant_id == current_user.tenant_id
    ).offset(skip).limit(limit).all()
    
    if not offline_data_list:
        raise HTTPException(status_code=404, detail="No offline data found")

    # Extract response bodies
    records = [data.response_body for data in offline_data_list]

    # Export to XLS
    xls_file = export_wathq_records_to_xls(records)
    
    return StreamingResponse(
        iter([xls_file.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=wathq_data_batch_{service_id}.xlsx"}
    )


@router.get("/call-logs/export-xls")
def export_call_logs_xls(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Export WATHQ call logs for current user to XLS format.
    """
    # Get call logs
    call_logs = crud.wathq_call_log.get_by_user(
        db=db, 
        user_id=current_user.id, 
        skip=skip, 
        limit=limit
    )
    
    if not call_logs:
        raise HTTPException(status_code=404, detail="No call logs found")

    # Convert to dict format
    records = []
    for log in call_logs:
        records.append({
            "id": str(log.id),
            "service_slug": log.service_slug,
            "endpoint": log.endpoint,
            "method": log.method,
            "status_code": log.status_code,
            "duration_ms": log.duration_ms,
            "fetched_at": log.fetched_at.isoformat() if log.fetched_at else None,
            "request_data": log.request_data,
            "response_body": log.response_body
        })

    # Export to XLS
    xls_file = export_wathq_records_to_xls(records)
    
    return StreamingResponse(
        iter([xls_file.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=wathq_call_logs.xlsx"}
    )


@router.get("/call-logs/export-xls-tenant")
def export_tenant_call_logs_xls(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Export all WATHQ call logs for current tenant to XLS format.
    """
    # Get call logs for tenant
    call_logs = crud.wathq_call_log.get_by_tenant(
        db=db, 
        tenant_id=current_user.tenant_id, 
        skip=skip, 
        limit=limit
    )
    
    if not call_logs:
        raise HTTPException(status_code=404, detail="No call logs found")

    # Convert to dict format
    records = []
    for log in call_logs:
        records.append({
            "id": str(log.id),
            "user_id": log.user_id,
            "service_slug": log.service_slug,
            "endpoint": log.endpoint,
            "method": log.method,
            "status_code": log.status_code,
            "duration_ms": log.duration_ms,
            "fetched_at": log.fetched_at.isoformat() if log.fetched_at else None,
            "request_data": log.request_data,
            "response_body": log.response_body
        })

    # Export to XLS
    xls_file = export_wathq_records_to_xls(records)
    
    return StreamingResponse(
        iter([xls_file.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=wathq_call_logs_tenant.xlsx"}
    )
