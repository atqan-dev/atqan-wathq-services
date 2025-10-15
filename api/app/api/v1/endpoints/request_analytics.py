"""
API endpoints for request analytics and monitoring.
Only accessible to management users.
"""

from typing import Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app import models
from app.api import deps
from app.services.request_counter_service import request_counter_service
from app.schemas.api_request_counter import (
    ApiRequestStats,
    EndpointStats,
    UserRequestStats,
    ServiceUsageStats,
    RequestTimeline,
    RequestDetails,
    DashboardStats
)

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStats)
def get_analytics_dashboard(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Get comprehensive analytics dashboard.
    Shows overall system metrics, top users, endpoints, and services.
    """
    return request_counter_service.get_dashboard_stats(db)


@router.get("/stats", response_model=ApiRequestStats)
def get_request_statistics(
    *,
    db: Session = Depends(deps.get_db),
    period: str = Query("today", description="Period: today, week, month, all"),
    tenant_id: Optional[int] = Query(None, description="Filter by tenant"),
    user_id: Optional[int] = Query(None, description="Filter by user"),
    service_id: Optional[UUID] = Query(None, description="Filter by service"),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Get aggregated request statistics.
    Can filter by tenant, user, or service.
    """
    return request_counter_service.get_request_stats(
        db=db,
        period=period,
        tenant_id=tenant_id,
        user_id=user_id,
        service_id=service_id
    )


@router.get("/endpoints", response_model=List[EndpointStats])
def get_endpoint_statistics(
    *,
    db: Session = Depends(deps.get_db),
    limit: int = Query(10, le=100, description="Number of top endpoints to return"),
    period: str = Query("today", description="Period: today, week, month"),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Get statistics for top API endpoints.
    Shows most called endpoints with performance metrics.
    """
    return request_counter_service.get_endpoint_stats(
        db=db,
        limit=limit,
        period=period
    )


@router.get("/users", response_model=List[UserRequestStats])
def get_user_statistics(
    *,
    db: Session = Depends(deps.get_db),
    limit: int = Query(10, le=100, description="Number of top users to return"),
    period: str = Query("today", description="Period: today, week, month"),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Get statistics for top API users.
    Shows most active users with their request patterns.
    """
    return request_counter_service.get_user_stats(
        db=db,
        limit=limit,
        period=period
    )


@router.get("/services", response_model=List[ServiceUsageStats])
def get_service_usage_statistics(
    *,
    db: Session = Depends(deps.get_db),
    period: str = Query("today", description="Period: today, week, month"),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Get WATHQ service usage statistics.
    Shows which external services are being used most.
    """
    return request_counter_service.get_service_usage_stats(
        db=db,
        period=period
    )


@router.get("/timeline", response_model=List[RequestTimeline])
def get_request_timeline(
    *,
    db: Session = Depends(deps.get_db),
    hours: int = Query(24, le=168, description="Number of hours to show"),
    tenant_id: Optional[int] = Query(None, description="Filter by tenant"),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Get hourly request timeline.
    Shows request patterns over time.
    """
    return request_counter_service.get_request_timeline(
        db=db,
        hours=hours,
        tenant_id=tenant_id
    )


@router.get("/requests", response_model=List[RequestDetails])
def get_recent_requests(
    *,
    db: Session = Depends(deps.get_db),
    limit: int = Query(100, le=1000, description="Number of requests to return"),
    tenant_id: Optional[int] = Query(None, description="Filter by tenant"),
    user_id: Optional[int] = Query(None, description="Filter by user"),
    service_id: Optional[UUID] = Query(None, description="Filter by service"),
    only_failed: bool = Query(False, description="Show only failed requests"),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Get detailed information about recent requests.
    Can filter by various criteria and show only failures.
    """
    return request_counter_service.get_recent_requests(
        db=db,
        limit=limit,
        tenant_id=tenant_id,
        user_id=user_id,
        service_id=service_id,
        only_failed=only_failed
    )


@router.get("/user/{user_id}/activity", response_model=UserRequestStats)
def get_user_activity(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    period: str = Query("today", description="Period: today, week, month"),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Get detailed activity for a specific user.
    Shows all request patterns and usage statistics.
    """
    # Check if user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    stats = request_counter_service.get_user_stats(
        db=db,
        limit=1,
        period=period
    )
    
    # Find the specific user's stats
    for stat in stats:
        if stat.user_id == user_id:
            return stat
    
    # If no stats found, return empty stats for the user
    return UserRequestStats(
        user_id=user_id,
        user_email=user.email,
        tenant_name=user.tenant.name if user.tenant else None,
        total_requests=0,
        successful_requests=0,
        failed_requests=0,
        external_calls=0,
        internal_calls=0,
        cached_calls=0,
        avg_response_time_ms=0,
        most_used_endpoints=[],
        last_request=datetime.utcnow()
    )


@router.get("/tenant/{tenant_id}/activity")
def get_tenant_activity(
    *,
    db: Session = Depends(deps.get_db),
    tenant_id: int,
    period: str = Query("today", description="Period: today, week, month"),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Get aggregated activity for a specific tenant.
    Shows all users and their combined usage.
    """
    # Check if tenant exists
    tenant = db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Get stats for this tenant
    stats = request_counter_service.get_request_stats(
        db=db,
        period=period,
        tenant_id=tenant_id
    )
    
    # Get timeline for this tenant
    timeline = request_counter_service.get_request_timeline(
        db=db,
        hours=24,
        tenant_id=tenant_id
    )
    
    # Get top users for this tenant
    users = db.query(models.User).filter(
        models.User.tenant_id == tenant_id
    ).all()
    
    user_stats = []
    for user in users:
        user_stat = request_counter_service.get_user_stats(
            db=db,
            limit=100,
            period=period
        )
        for stat in user_stat:
            if stat.user_id == user.id:
                user_stats.append(stat)
                break
    
    return {
        "tenant": {
            "id": tenant.id,
            "name": tenant.name,
            "slug": tenant.slug
        },
        "stats": stats,
        "timeline": timeline,
        "user_activity": user_stats,
        "total_users": len(users),
        "active_users": len(user_stats)
    }


@router.post("/export")
def export_request_data(
    *,
    db: Session = Depends(deps.get_db),
    start_date: datetime = Query(..., description="Start date for export"),
    end_date: datetime = Query(..., description="End date for export"),
    format: str = Query("csv", description="Export format: csv or json"),
    tenant_id: Optional[int] = Query(None, description="Filter by tenant"),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Export request data for analysis.
    Returns data in CSV or JSON format.
    """
    from app.models.api_request_counter import ApiRequestCounter
    import csv
    import io
    
    # Query request data
    query = db.query(ApiRequestCounter).filter(
        ApiRequestCounter.created_at >= start_date,
        ApiRequestCounter.created_at <= end_date
    )
    
    if tenant_id:
        query = query.filter(ApiRequestCounter.tenant_id == tenant_id)
    
    records = query.all()
    
    if format == "csv":
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "Timestamp", "Request Type", "Endpoint", "Method",
            "User Email", "Tenant", "Service", "Status Code",
            "Response Time (ms)", "Success", "Cached", "Error"
        ])
        
        # Write data
        for r in records:
            user_email = ""
            tenant_name = ""
            service_name = ""
            
            if r.user_id:
                user = db.query(models.User).filter(models.User.id == r.user_id).first()
                if user:
                    user_email = user.email
                    if user.tenant:
                        tenant_name = user.tenant.name
            
            if r.service_id:
                service = db.query(models.Service).filter(models.Service.id == r.service_id).first()
                if service:
                    service_name = service.name
            
            writer.writerow([
                r.created_at.isoformat(),
                r.request_type,
                r.endpoint,
                r.method,
                user_email,
                tenant_name,
                service_name,
                r.response_status,
                r.response_time_ms,
                r.is_successful,
                r.is_cached,
                r.error_message or ""
            ])
        
        return {
            "format": "csv",
            "data": output.getvalue(),
            "records": len(records)
        }
    
    else:
        # Return JSON
        data = []
        for r in records:
            user_email = ""
            tenant_name = ""
            service_name = ""
            
            if r.user_id:
                user = db.query(models.User).filter(models.User.id == r.user_id).first()
                if user:
                    user_email = user.email
                    if user.tenant:
                        tenant_name = user.tenant.name
            
            if r.service_id:
                service = db.query(models.Service).filter(models.Service.id == r.service_id).first()
                if service:
                    service_name = service.name
            
            data.append({
                "timestamp": r.created_at.isoformat(),
                "request_type": r.request_type,
                "endpoint": r.endpoint,
                "method": r.method,
                "user_email": user_email,
                "tenant_name": tenant_name,
                "service_name": service_name,
                "status_code": r.response_status,
                "response_time_ms": r.response_time_ms,
                "is_successful": r.is_successful,
                "is_cached": r.is_cached,
                "error_message": r.error_message
            })
        
        return {
            "format": "json",
            "data": data,
            "records": len(records)
        }
