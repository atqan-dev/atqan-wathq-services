"""
Service for tracking and analyzing API requests.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from uuid import UUID
import logging

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, Integer
from fastapi import Request, Response

from app.models.api_request_counter import ApiRequestCounter, RequestType
from app.models.user import User
from app.models.tenant import Tenant
from app.models.service import Service
from app.models.management_user import ManagementUser
from app.schemas.api_request_counter import (
    ApiRequestStats,
    EndpointStats,
    UserRequestStats,
    ServiceUsageStats,
    RequestTimeline,
    DashboardStats,
    RequestDetails
)

logger = logging.getLogger(__name__)


class RequestCounterService:
    """Service for managing API request counters and analytics."""
    
    @staticmethod
    def track_request(
        db: Session,
        request: Request,
        response: Response,
        response_time_ms: int,
        request_type: str = RequestType.INTERNAL,
        user: Optional[User] = None,
        management_user: Optional[ManagementUser] = None,
        service_id: Optional[UUID] = None,
        service_slug: Optional[str] = None,
        is_cached: bool = False,
        error_message: Optional[str] = None,
        request_params: Optional[Dict[str, Any]] = None
    ) -> ApiRequestCounter:
        """
        Track an API request.
        
        Args:
            db: Database session
            request: FastAPI request object
            response: FastAPI response object
            response_time_ms: Response time in milliseconds
            request_type: Type of request (internal/external/cached)
            user: User making the request
            management_user: Management user if applicable
            service_id: WATHQ service ID if applicable
            service_slug: WATHQ service slug
            is_cached: Whether response was from cache
            error_message: Error message if failed
            request_params: Sanitized request parameters
        """
        try:
            # Extract request details
            endpoint = str(request.url.path)
            method = request.method
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("User-Agent", "")[:500]  # Limit length
            
            # Determine success based on status code
            is_successful = 200 <= response.status_code < 400
            
            # Create counter entry
            counter = ApiRequestCounter(
                request_type=request_type,
                endpoint=endpoint,
                method=method,
                user_id=user.id if user else None,
                tenant_id=user.tenant_id if user and hasattr(user, 'tenant_id') else None,
                management_user_id=management_user.id if management_user else None,
                service_id=service_id,
                service_slug=service_slug,
                ip_address=ip_address,
                user_agent=user_agent,
                request_params=request_params,
                request_size=int(request.headers.get("Content-Length", 0)),
                response_status=response.status_code,
                response_time_ms=response_time_ms,
                response_size=int(response.headers.get("Content-Length", 0)),
                error_message=error_message,
                is_successful=is_successful,
                is_cached=is_cached,
                is_rate_limited=(response.status_code == 429)
            )
            
            db.add(counter)
            db.commit()
            db.refresh(counter)
            
            return counter
            
        except Exception as e:
            logger.error(f"Failed to track request: {str(e)}")
            db.rollback()
            return None
    
    @staticmethod
    def get_request_stats(
        db: Session,
        period: str = "today",
        tenant_id: Optional[int] = None,
        user_id: Optional[int] = None,
        service_id: Optional[UUID] = None
    ) -> ApiRequestStats:
        """
        Get aggregated request statistics.
        
        Args:
            db: Database session
            period: Time period (today, week, month, all)
            tenant_id: Filter by tenant
            user_id: Filter by user
            service_id: Filter by service
        """
        # Determine time range
        now = datetime.utcnow()
        if period == "today":
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_time = now - timedelta(days=7)
        elif period == "month":
            start_time = now - timedelta(days=30)
        else:
            start_time = None
        
        # Build query
        query = db.query(ApiRequestCounter)
        
        if start_time:
            query = query.filter(ApiRequestCounter.created_at >= start_time)
        if tenant_id:
            query = query.filter(ApiRequestCounter.tenant_id == tenant_id)
        if user_id:
            query = query.filter(ApiRequestCounter.user_id == user_id)
        if service_id:
            query = query.filter(ApiRequestCounter.service_id == service_id)
        
        # Get all records for aggregation
        records = query.all()
        
        if not records:
            return ApiRequestStats(
                period=period,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                cached_requests=0,
                external_requests=0,
                internal_requests=0,
                avg_response_time_ms=0,
                max_response_time_ms=0,
                min_response_time_ms=0,
                cache_hit_rate=0,
                success_rate=0,
                unique_users=0,
                unique_endpoints=0
            )
        
        # Calculate statistics
        total = len(records)
        successful = sum(1 for r in records if r.is_successful)
        failed = total - successful
        cached = sum(1 for r in records if r.is_cached)
        external = sum(1 for r in records if r.request_type == RequestType.EXTERNAL)
        internal = sum(1 for r in records if r.request_type == RequestType.INTERNAL)
        
        response_times = [r.response_time_ms for r in records]
        avg_response = sum(response_times) / len(response_times) if response_times else 0
        
        unique_users = len(set(r.user_id for r in records if r.user_id))
        unique_endpoints = len(set(r.endpoint for r in records))
        
        return ApiRequestStats(
            period=period,
            total_requests=total,
            successful_requests=successful,
            failed_requests=failed,
            cached_requests=cached,
            external_requests=external,
            internal_requests=internal,
            avg_response_time_ms=round(avg_response, 2),
            max_response_time_ms=max(response_times) if response_times else 0,
            min_response_time_ms=min(response_times) if response_times else 0,
            cache_hit_rate=round((cached / total * 100) if total > 0 else 0, 2),
            success_rate=round((successful / total * 100) if total > 0 else 0, 2),
            unique_users=unique_users,
            unique_endpoints=unique_endpoints
        )
    
    @staticmethod
    def get_endpoint_stats(
        db: Session,
        limit: int = 10,
        period: str = "today"
    ) -> List[EndpointStats]:
        """Get statistics for top endpoints."""
        # Determine time range
        now = datetime.utcnow()
        if period == "today":
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_time = now - timedelta(days=7)
        else:
            start_time = now - timedelta(days=30)
        
        # Query for endpoint statistics
        query = db.query(
            ApiRequestCounter.endpoint,
            ApiRequestCounter.method,
            func.count(ApiRequestCounter.id).label('total_calls'),
            func.sum(ApiRequestCounter.is_successful.cast(Integer)).label('success_count'),
            func.avg(ApiRequestCounter.response_time_ms).label('avg_response'),
            func.sum(ApiRequestCounter.is_cached.cast(Integer)).label('cached_count'),
            func.max(ApiRequestCounter.created_at).label('last_called')
        ).filter(
            ApiRequestCounter.created_at >= start_time
        ).group_by(
            ApiRequestCounter.endpoint,
            ApiRequestCounter.method
        ).order_by(
            desc('total_calls')
        ).limit(limit)
        
        results = query.all()
        
        stats = []
        for r in results:
            success_rate = (r.success_count / r.total_calls * 100) if r.total_calls > 0 else 0
            stats.append(EndpointStats(
                endpoint=r.endpoint,
                method=r.method,
                total_calls=r.total_calls,
                success_rate=round(success_rate, 2),
                avg_response_time_ms=round(r.avg_response or 0, 2),
                cached_calls=r.cached_count or 0,
                failed_calls=r.total_calls - (r.success_count or 0),
                last_called=r.last_called
            ))
        
        return stats
    
    @staticmethod
    def get_user_stats(
        db: Session,
        limit: int = 10,
        period: str = "today"
    ) -> List[UserRequestStats]:
        """Get statistics for top users."""
        # Determine time range
        now = datetime.utcnow()
        if period == "today":
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_time = now - timedelta(days=7)
        else:
            start_time = now - timedelta(days=30)
        
        # Query for user statistics
        query = db.query(
            User.id,
            User.email,
            Tenant.name.label('tenant_name'),
            func.count(ApiRequestCounter.id).label('total_requests'),
            func.sum(ApiRequestCounter.is_successful.cast(Integer)).label('successful_requests'),
            func.sum((ApiRequestCounter.request_type == RequestType.EXTERNAL).cast(Integer)).label('external_calls'),
            func.sum((ApiRequestCounter.request_type == RequestType.INTERNAL).cast(Integer)).label('internal_calls'),
            func.sum(ApiRequestCounter.is_cached.cast(Integer)).label('cached_calls'),
            func.avg(ApiRequestCounter.response_time_ms).label('avg_response'),
            func.max(ApiRequestCounter.created_at).label('last_request')
        ).join(
            ApiRequestCounter, User.id == ApiRequestCounter.user_id
        ).outerjoin(
            Tenant, User.tenant_id == Tenant.id
        ).filter(
            ApiRequestCounter.created_at >= start_time
        ).group_by(
            User.id, User.email, Tenant.name
        ).order_by(
            desc('total_requests')
        ).limit(limit)
        
        results = query.all()
        
        stats = []
        for r in results:
            # Get most used endpoints for this user
            endpoint_query = db.query(
                ApiRequestCounter.endpoint,
                func.count(ApiRequestCounter.id).label('count')
            ).filter(
                and_(
                    ApiRequestCounter.user_id == r.id,
                    ApiRequestCounter.created_at >= start_time
                )
            ).group_by(
                ApiRequestCounter.endpoint
            ).order_by(
                desc('count')
            ).limit(5)
            
            top_endpoints = [
                {"endpoint": e.endpoint, "count": e.count}
                for e in endpoint_query.all()
            ]
            
            stats.append(UserRequestStats(
                user_id=r.id,
                user_email=r.email,
                tenant_name=r.tenant_name,
                total_requests=r.total_requests,
                successful_requests=r.successful_requests or 0,
                failed_requests=r.total_requests - (r.successful_requests or 0),
                external_calls=r.external_calls or 0,
                internal_calls=r.internal_calls or 0,
                cached_calls=r.cached_calls or 0,
                avg_response_time_ms=round(r.avg_response or 0, 2),
                most_used_endpoints=top_endpoints,
                last_request=r.last_request
            ))
        
        return stats
    
    @staticmethod
    def get_service_usage_stats(
        db: Session,
        period: str = "today"
    ) -> List[ServiceUsageStats]:
        """Get WATHQ service usage statistics."""
        # Determine time range
        now = datetime.utcnow()
        if period == "today":
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_time = now - timedelta(days=7)
        else:
            start_time = now - timedelta(days=30)
        
        # Query for service statistics
        results = db.query(
            Service.id,
            Service.name,
            Service.slug,
            Service.price,
            func.count(ApiRequestCounter.id).label('total_calls'),
            func.sum(ApiRequestCounter.is_cached.cast(Integer)).label('cached_calls'),
            func.sum(ApiRequestCounter.is_successful.cast(Integer)).label('success_count'),
            func.avg(ApiRequestCounter.response_time_ms).label('avg_response'),
            func.count(func.distinct(ApiRequestCounter.user_id)).label('unique_users')
        ).join(
            ApiRequestCounter, Service.id == ApiRequestCounter.service_id
        ).filter(
            ApiRequestCounter.created_at >= start_time
        ).group_by(
            Service.id, Service.name, Service.slug, Service.price
        ).all()
        stats = []
        for r in results:
            success_rate = (r.success_count / r.total_calls * 100) if r.total_calls > 0 else 0
            direct_calls = r.total_calls - (r.cached_calls or 0)
            total_cost = float(r.price) * direct_calls if r.price else None
            
            stats.append(ServiceUsageStats(
                service_id=r.id,
                service_name=r.name,
                service_slug=r.slug,
                total_calls=r.total_calls,
                cached_calls=r.cached_calls or 0,
                direct_calls=direct_calls,
                success_rate=round(success_rate, 2),
                avg_response_time_ms=round(r.avg_response or 0, 2),
                unique_users=r.unique_users,
                total_cost=total_cost
            ))
        
        return stats
    
    @staticmethod
    def get_request_timeline(
        db: Session,
        hours: int = 24,
        tenant_id: Optional[int] = None
    ) -> List[RequestTimeline]:
        """Get hourly request timeline."""
        now = datetime.utcnow()
        start_time = now - timedelta(hours=hours)
        
        # Build base query
        query = db.query(
            func.date_trunc('hour', ApiRequestCounter.created_at).label('hour'),
            func.count(ApiRequestCounter.id).label('request_count'),
            func.sum(ApiRequestCounter.is_successful.cast(Integer)).label('success_count'),
            func.avg(ApiRequestCounter.response_time_ms).label('avg_response'),
            func.sum((ApiRequestCounter.request_type == RequestType.EXTERNAL).cast(Integer)).label('external_count'),
            func.sum((ApiRequestCounter.request_type == RequestType.INTERNAL).cast(Integer)).label('internal_count'),
            func.sum(ApiRequestCounter.is_cached.cast(Integer)).label('cached_count')
        ).filter(
            ApiRequestCounter.created_at >= start_time
        )
        
        if tenant_id:
            query = query.filter(ApiRequestCounter.tenant_id == tenant_id)
        
        query = query.group_by('hour').order_by('hour')
        
        results = query.all()
        
        timeline = []
        for r in results:
            timeline.append(RequestTimeline(
                timestamp=r.hour,
                request_count=r.request_count,
                success_count=r.success_count or 0,
                failed_count=r.request_count - (r.success_count or 0),
                avg_response_time_ms=round(r.avg_response or 0, 2),
                external_count=r.external_count or 0,
                internal_count=r.internal_count or 0,
                cached_count=r.cached_count or 0
            ))
        
        return timeline
    
    @staticmethod
    def get_recent_requests(
        db: Session,
        limit: int = 100,
        tenant_id: Optional[int] = None,
        user_id: Optional[int] = None,
        service_id: Optional[UUID] = None,
        only_failed: bool = False
    ) -> List[RequestDetails]:
        """Get recent request details."""
        query = db.query(ApiRequestCounter)
        
        if tenant_id:
            query = query.filter(ApiRequestCounter.tenant_id == tenant_id)
        if user_id:
            query = query.filter(ApiRequestCounter.user_id == user_id)
        if service_id:
            query = query.filter(ApiRequestCounter.service_id == service_id)
        if only_failed:
            query = query.filter(ApiRequestCounter.is_successful == False)
        
        query = query.order_by(desc(ApiRequestCounter.created_at)).limit(limit)
        
        records = query.all()
        
        details = []
        for r in records:
            # Get user email
            user_email = None
            tenant_name = None
            if r.user_id:
                user = db.query(User).filter(User.id == r.user_id).first()
                if user:
                    user_email = user.email
                    if user.tenant_id:
                        tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
                        if tenant:
                            tenant_name = tenant.name
            
            # Get service name
            service_name = None
            if r.service_id:
                service = db.query(Service).filter(Service.id == r.service_id).first()
                if service:
                    service_name = service.name
            
            details.append(RequestDetails(
                id=r.id,
                request_type=r.request_type,
                endpoint=r.endpoint,
                method=r.method,
                user_email=user_email,
                tenant_name=tenant_name,
                service_name=service_name,
                ip_address=r.ip_address,
                user_agent=r.user_agent,
                request_params=r.request_params,
                response_status=r.response_status,
                response_time_ms=r.response_time_ms,
                response_size=r.response_size,
                error_message=r.error_message,
                is_successful=r.is_successful,
                is_cached=r.is_cached,
                is_rate_limited=r.is_rate_limited,
                created_at=r.created_at
            ))
        
        return details
    
    @staticmethod
    def get_dashboard_stats(db: Session) -> DashboardStats:
        """Get comprehensive dashboard statistics for management."""
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        
        # Get request counts
        total_today = db.query(ApiRequestCounter).filter(
            ApiRequestCounter.created_at >= today_start
        ).count()
        
        total_week = db.query(ApiRequestCounter).filter(
            ApiRequestCounter.created_at >= week_start
        ).count()
        
        total_month = db.query(ApiRequestCounter).filter(
            ApiRequestCounter.created_at >= month_start
        ).count()
        
        # Get performance metrics
        today_stats = db.query(
            func.avg(ApiRequestCounter.response_time_ms).label('avg_response'),
            func.sum(ApiRequestCounter.is_successful.cast(Integer)).label('success_count'),
            func.sum(ApiRequestCounter.is_cached.cast(Integer)).label('cached_count')
        ).filter(
            ApiRequestCounter.created_at >= today_start
        ).first()
        
        week_stats = db.query(
            func.sum(ApiRequestCounter.is_successful.cast(Integer)).label('success_count'),
            func.sum(ApiRequestCounter.is_cached.cast(Integer)).label('cached_count'),
            func.count(ApiRequestCounter.id).label('total_count')
        ).filter(
            ApiRequestCounter.created_at >= week_start
        ).first()
        
        # Calculate rates
        success_rate_today = (today_stats.success_count / total_today * 100) if total_today > 0 else 0
        success_rate_week = (week_stats.success_count / week_stats.total_count * 100) if week_stats.total_count > 0 else 0
        cache_hit_rate_today = (today_stats.cached_count / total_today * 100) if total_today > 0 else 0
        cache_hit_rate_week = (week_stats.cached_count / week_stats.total_count * 100) if week_stats.total_count > 0 else 0
        
        # Get top metrics
        top_endpoints = RequestCounterService.get_endpoint_stats(db, limit=5, period="today")
        top_users = RequestCounterService.get_user_stats(db, limit=5, period="today")
        top_services = RequestCounterService.get_service_usage_stats(db, period="today")
        
        # Get timeline
        hourly_timeline = RequestCounterService.get_request_timeline(db, hours=24)
        
        # Get slow endpoints (avg response > 1000ms)
        slow_endpoints_query = db.query(
            ApiRequestCounter.endpoint,
            func.avg(ApiRequestCounter.response_time_ms).label('avg_response'),
            func.count(ApiRequestCounter.id).label('count')
        ).filter(
            ApiRequestCounter.created_at >= today_start
        ).group_by(
            ApiRequestCounter.endpoint
        ).having(
            func.avg(ApiRequestCounter.response_time_ms) > 1000
        ).order_by(
            desc('avg_response')
        ).limit(5)
        
        slow_endpoints = [
            {
                "endpoint": r.endpoint,
                "avg_response_time_ms": round(r.avg_response, 2),
                "request_count": r.count
            }
            for r in slow_endpoints_query.all()
        ]
        
        # Get failing endpoints (success rate < 90%)
        failing_endpoints_query = db.query(
            ApiRequestCounter.endpoint,
            func.count(ApiRequestCounter.id).label('total'),
            func.sum(ApiRequestCounter.is_successful.cast(Integer)).label('success')
        ).filter(
            ApiRequestCounter.created_at >= today_start
        ).group_by(
            ApiRequestCounter.endpoint
        ).having(
            func.sum(ApiRequestCounter.is_successful.cast(Integer)) < func.count(ApiRequestCounter.id) * 0.9
        ).limit(5)
        
        failing_endpoints = [
            {
                "endpoint": r.endpoint,
                "success_rate": round((r.success / r.total * 100) if r.total > 0 else 0, 2),
                "failed_count": r.total - (r.success or 0)
            }
            for r in failing_endpoints_query.all()
        ]
        
        # Get rate limited users
        rate_limited_query = db.query(
            User.email,
            func.count(ApiRequestCounter.id).label('limited_count')
        ).join(
            ApiRequestCounter, User.id == ApiRequestCounter.user_id
        ).filter(
            and_(
                ApiRequestCounter.created_at >= today_start,
                ApiRequestCounter.is_rate_limited == True
            )
        ).group_by(
            User.email
        ).order_by(
            desc('limited_count')
        ).limit(5)
        
        rate_limited_users = [
            {"email": r.email, "limited_requests": r.limited_count}
            for r in rate_limited_query.all()
        ]
        
        # Determine response time trend
        yesterday_start = today_start - timedelta(days=1)
        yesterday_end = today_start
        
        yesterday_avg = db.query(
            func.avg(ApiRequestCounter.response_time_ms)
        ).filter(
            and_(
                ApiRequestCounter.created_at >= yesterday_start,
                ApiRequestCounter.created_at < yesterday_end
            )
        ).scalar() or 0
        
        today_avg = today_stats.avg_response or 0
        
        if yesterday_avg > 0:
            if today_avg > yesterday_avg * 1.1:
                trend = "up"
            elif today_avg < yesterday_avg * 0.9:
                trend = "down"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return DashboardStats(
            total_requests_today=total_today,
            total_requests_this_week=total_week,
            total_requests_this_month=total_month,
            avg_response_time_today_ms=round(today_avg, 2),
            avg_response_time_trend=trend,
            success_rate_today=round(success_rate_today, 2),
            success_rate_this_week=round(success_rate_week, 2),
            cache_hit_rate_today=round(cache_hit_rate_today, 2),
            cache_hit_rate_this_week=round(cache_hit_rate_week, 2),
            top_endpoints=top_endpoints,
            top_users=top_users,
            top_services=top_services,
            hourly_timeline=hourly_timeline,
            slow_endpoints=slow_endpoints,
            failing_endpoints=failing_endpoints,
            rate_limited_users=rate_limited_users
        )


# Singleton instance
request_counter_service = RequestCounterService()
