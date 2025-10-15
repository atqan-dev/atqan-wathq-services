"""
Middleware for automatic request counting and tracking.
"""

import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.db.session import SessionLocal
from app.services.request_counter_service import request_counter_service
from app.models.api_request_counter import RequestType


class RequestCounterMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically track API requests."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # Define paths to exclude from tracking
        self.exclude_paths = {
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/health",
            "/favicon.ico",
            "/static"
        }
        
        # Define external API path patterns
        self.external_patterns = [
            "/api/v1/wathq/external",
            "/api/v1/management/wathq/external"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process and track the request."""
        # Skip tracking for excluded paths
        path = str(request.url.path)
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            return await call_next(request)
        
        # Start timing
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Track the request asynchronously (don't block the response)
        await self._track_request(request, response, response_time_ms)
        
        return response
    
    async def _track_request(
        self,
        request: Request,
        response: Response,
        response_time_ms: int
    ):
        """Track the request in the database."""
        db = SessionLocal()
        try:
            # Determine request type
            path = str(request.url.path)
            if any(pattern in path for pattern in self.external_patterns):
                request_type = RequestType.EXTERNAL
            else:
                request_type = RequestType.INTERNAL
            
            # Try to get current user (if authenticated)
            user = None
            management_user = None
            
            # Check if user is in request state (set by auth middleware)
            if hasattr(request.state, "user"):
                user = request.state.user
            elif hasattr(request.state, "management_user"):
                management_user = request.state.management_user
            
            # Extract service information from path if it's a WATHQ endpoint
            service_slug = None
            if "/wathq/" in path:
                # Extract service slug from path
                parts = path.split("/")
                if "wathq" in parts:
                    idx = parts.index("wathq")
                    if idx + 1 < len(parts):
                        service_slug = parts[idx + 1]
            
            # Check if response is from cache (look for cache header)
            is_cached = response.headers.get("X-Cache-Hit", "false").lower() == "true"
            
            # Extract sanitized request parameters
            request_params = None
            if request.method in ["POST", "PUT", "PATCH"]:
                # Try to get body for logging (be careful with sensitive data)
                if hasattr(request.state, "body"):
                    try:
                        body = json.loads(request.state.body)
                        # Sanitize sensitive fields
                        sanitized = self._sanitize_params(body)
                        request_params = sanitized
                    except (json.JSONDecodeError, AttributeError):
                        pass
            elif request.method == "GET":
                # Get query parameters
                if request.query_params:
                    request_params = dict(request.query_params)
            
            # Extract error message if failed
            error_message = None
            if response.status_code >= 400:
                if hasattr(response, "body"):
                    try:
                        body = json.loads(response.body)
                        error_message = body.get("detail", str(body))[:500]
                    except (json.JSONDecodeError, AttributeError):
                        pass
            
            # Track the request
            request_counter_service.track_request(
                db=db,
                request=request,
                response=response,
                response_time_ms=response_time_ms,
                request_type=request_type,
                user=user,
                management_user=management_user,
                service_slug=service_slug,
                is_cached=is_cached,
                error_message=error_message,
                request_params=request_params
            )
            
        except Exception as e:
            # Don't let tracking errors affect the response
            print(f"Error tracking request: {str(e)}")
        finally:
            db.close()
    
    def _sanitize_params(self, params: dict) -> dict:
        """Sanitize sensitive parameters."""
        if not params:
            return {}
        
        # List of sensitive field names to redact
        sensitive_fields = {
            "password", "token", "secret", "api_key", "apikey",
            "authorization", "credit_card", "ssn", "pin"
        }
        
        sanitized = {}
        for key, value in params.items():
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_params(value)
            else:
                sanitized[key] = value
        
        return sanitized
