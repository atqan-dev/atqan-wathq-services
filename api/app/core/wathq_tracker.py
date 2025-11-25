"""
WATHQ API call tracking utility.
"""

import time
from typing import Any, Dict, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.wathq_call_log import WathqCallLog
from app.crud.crud_wathq_offline_data import wathq_offline_data


class WathqCallTracker:
    """
    Utility class to track WATHQ API calls.
    """

    @staticmethod
    def log_call(
        db: Session,
        tenant_id: int,
        user_id: int,
        service_slug: str,
        endpoint: str,
        method: str,
        status_code: int,
        response_body: Dict[str, Any],
        request_data: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None
    ) -> WathqCallLog:
        """
        Log a WATHQ API call to the database.
        """
        call_log = WathqCallLog(
            tenant_id=tenant_id,
            user_id=user_id,
            service_slug=service_slug,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            request_data=request_data,
            response_body=response_body,
            duration_ms=duration_ms
        )
        
        db.add(call_log)
        db.commit()
        db.refresh(call_log)
        
        return call_log

    @staticmethod
    def track_call(
        db: Session,
        tenant_id: int,
        user_id: int,
        service_slug: str,
        endpoint: str,
        method: str = "POST"
    ):
        """
        Context manager to track WATHQ API calls with timing.
        """
        return WathqCallContext(db, tenant_id, user_id, service_slug, endpoint, method)


class WathqCallContext:
    """
    Context manager for tracking WATHQ API calls.
    """

    def __init__(
        self,
        db: Session,
        tenant_id: int,
        user_id: int,
        service_slug: str,
        endpoint: str,
        method: str = "POST"
    ):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.service_slug = service_slug
        self.endpoint = endpoint
        self.method = method
        self.start_time = None
        self.request_data = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # This will be called after the API call completes
        pass

    def set_request_data(self, data: Dict[str, Any]):
        """Set the request data."""
        self.request_data = data

    def log_response(self, status_code: int, response_body: Dict[str, Any], service_id: Optional[UUID] = None, full_url: Optional[str] = None):
        """Log the response data and save offline data if successful."""
        duration_ms = None
        if self.start_time:
            duration_ms = int((time.time() - self.start_time) * 1000)

        WathqCallTracker.log_call(
            db=self.db,
            tenant_id=self.tenant_id,
            user_id=self.user_id,
            service_slug=self.service_slug,
            endpoint=self.endpoint,
            method=self.method,
            status_code=status_code,
            response_body=response_body,
            request_data=self.request_data,
            duration_ms=duration_ms
        )
        
        # Save offline data if successful and service_id provided
        # Only save for tenant users (not management users who have None tenant_id)
        if status_code == 200 and service_id and full_url and self.tenant_id and self.user_id:
            wathq_offline_data.create_offline_data(
                db=self.db,
                service_id=service_id,
                tenant_id=self.tenant_id,
                fetched_by=self.user_id,
                full_external_url=full_url,
                response_body=response_body
            )