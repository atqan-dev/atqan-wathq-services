"""
Dedicated logging system for WATHQ external API calls.
Tracks all external API requests to WATHQ services with detailed metrics.
"""

import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

# Create WATHQ-specific logger
wathq_logger = logging.getLogger("wathq_api")
wathq_logger.setLevel(logging.DEBUG)

# Create file handler for WATHQ logs
wathq_handler = logging.FileHandler("logs/wathq_api.log")
wathq_handler.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
wathq_handler.setFormatter(formatter)

# Add handler to logger
if not wathq_logger.handlers:
    wathq_logger.addHandler(wathq_handler)


class WathqRequestStatus(str, Enum):
    """Status of WATHQ API request."""
    SUCCESS = "success"
    FAILED = "failed"
    UNAUTHORIZED = "unauthorized"
    TIMEOUT = "timeout"
    INVALID_REQUEST = "invalid_request"
    SERVER_ERROR = "server_error"


class WathqAPILogger:
    """
    Dedicated logger for WATHQ external API calls.
    Tracks requests, responses, and performance metrics.
    """

    @staticmethod
    def log_request(
        request_id: str,
        service: str,
        endpoint: str,
        method: str = "GET",
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
        management_user_id: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Log outgoing WATHQ API request.
        
        Args:
            request_id: Unique request identifier
            service: Service name (e.g., 'commercial-registration')
            endpoint: API endpoint path
            method: HTTP method (GET, POST, etc.)
            user_id: Tenant user ID (if applicable)
            tenant_id: Tenant ID
            management_user_id: Management user ID (if applicable)
            params: Request parameters
            headers: Request headers (sensitive data redacted)
        """
        log_data = {
            "event": "wathq_request_sent",
            "request_id": request_id,
            "service": service,
            "endpoint": endpoint,
            "method": method,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "management_user_id": management_user_id,
            "params": params or {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Redact sensitive headers
        if headers:
            redacted_headers = {
                k: "***REDACTED***" if k.lower() in ["apikey", "authorization"]
                else v
                for k, v in headers.items()
            }
            log_data["headers"] = redacted_headers

        wathq_logger.info(
            f"Outgoing request to {service}/{endpoint}",
            extra={"request_id": request_id},
        )
        wathq_logger.debug(json.dumps(log_data), extra={"request_id": request_id})

    @staticmethod
    def log_response(
        request_id: str,
        service: str,
        endpoint: str,
        status_code: int,
        response_time_ms: int,
        response_size_bytes: int,
        status: WathqRequestStatus,
        response_body: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
        management_user_id: Optional[int] = None,
    ) -> None:
        """
        Log WATHQ API response.
        
        Args:
            request_id: Unique request identifier
            service: Service name
            endpoint: API endpoint path
            status_code: HTTP status code
            response_time_ms: Response time in milliseconds
            response_size_bytes: Response body size in bytes
            status: Request status (success, failed, etc.)
            response_body: Response body (truncated if large)
            error_message: Error message if request failed
            user_id: Tenant user ID
            tenant_id: Tenant ID
            management_user_id: Management user ID
        """
        # Truncate large responses
        truncated_body = response_body
        if response_body and isinstance(response_body, dict):
            body_str = json.dumps(response_body)
            if len(body_str) > 1000:
                truncated_body = {
                    "truncated": True,
                    "size": len(body_str),
                    "preview": body_str[:500] + "..."
                }

        log_data = {
            "event": "wathq_response_received",
            "request_id": request_id,
            "service": service,
            "endpoint": endpoint,
            "status_code": status_code,
            "status": status.value,
            "response_time_ms": response_time_ms,
            "response_size_bytes": response_size_bytes,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "management_user_id": management_user_id,
            "error_message": error_message,
            "response_body": truncated_body,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Log level based on status
        if status == WathqRequestStatus.SUCCESS:
            log_level = logging.INFO
            message = f"✓ {service}/{endpoint} - {status_code} ({response_time_ms}ms)"
        elif status == WathqRequestStatus.UNAUTHORIZED:
            log_level = logging.WARNING
            message = f"✗ {service}/{endpoint} - 401 Unauthorized"
        elif status == WathqRequestStatus.TIMEOUT:
            log_level = logging.WARNING
            message = f"✗ {service}/{endpoint} - Timeout after {response_time_ms}ms"
        else:
            log_level = logging.ERROR
            message = f"✗ {service}/{endpoint} - {status_code} {status.value}"

        wathq_logger.log(
            log_level,
            message,
            extra={"request_id": request_id},
        )
        wathq_logger.debug(json.dumps(log_data), extra={"request_id": request_id})

    @staticmethod
    def log_error(
        request_id: str,
        service: str,
        endpoint: str,
        error_type: str,
        error_message: str,
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
        management_user_id: Optional[int] = None,
    ) -> None:
        """
        Log WATHQ API error.
        
        Args:
            request_id: Unique request identifier
            service: Service name
            endpoint: API endpoint path
            error_type: Type of error (e.g., 'ConnectionError', 'TimeoutError')
            error_message: Error message
            user_id: Tenant user ID
            tenant_id: Tenant ID
            management_user_id: Management user ID
        """
        log_data = {
            "event": "wathq_error",
            "request_id": request_id,
            "service": service,
            "endpoint": endpoint,
            "error_type": error_type,
            "error_message": error_message,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "management_user_id": management_user_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        wathq_logger.error(
            f"Error in {service}/{endpoint}: {error_type} - {error_message}",
            extra={"request_id": request_id},
        )
        wathq_logger.debug(json.dumps(log_data), extra={"request_id": request_id})

    @staticmethod
    def log_performance_summary(
        service: str,
        total_requests: int,
        successful_requests: int,
        failed_requests: int,
        avg_response_time_ms: float,
        total_data_transferred_mb: float,
    ) -> None:
        """
        Log performance summary for a service.
        
        Args:
            service: Service name
            total_requests: Total number of requests
            successful_requests: Number of successful requests
            failed_requests: Number of failed requests
            avg_response_time_ms: Average response time in milliseconds
            total_data_transferred_mb: Total data transferred in MB
        """
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0

        log_data = {
            "event": "wathq_performance_summary",
            "service": service,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate_percent": success_rate,
            "avg_response_time_ms": avg_response_time_ms,
            "total_data_transferred_mb": total_data_transferred_mb,
            "timestamp": datetime.utcnow().isoformat(),
        }

        wathq_logger.info(
            f"Performance Summary - {service}: {success_rate:.1f}% success rate, "
            f"avg {avg_response_time_ms:.0f}ms, {total_data_transferred_mb:.2f}MB transferred"
        )
        wathq_logger.debug(json.dumps(log_data))
