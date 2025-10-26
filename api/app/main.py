"""
FastAPI application factory and configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
import os
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.multitenancy import tenant_identification_middleware
from app.middleware.request_counter import RequestCounterMiddleware

# Setup logging
setup_logging()


def create_application() -> FastAPI:
    """
    Create FastAPI application with all configurations.
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add trusted host middleware for production
    if not settings.DEBUG:
        application.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,
        )

    # Add tenant identification middleware
    application.middleware("http")(tenant_identification_middleware)
    
    # Add request counter middleware
    application.add_middleware(RequestCounterMiddleware)

    # Include API router
    application.include_router(api_router, prefix=settings.API_V1_STR)

    # Mount static files for uploads
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    application.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

    # Root endpoint
    @application.get("/")
    async def read_root():
        """
        Root endpoint with basic API information.
        """
        return {
            "message": "Welcome to FastAPI Starter",
            "description": settings.PROJECT_DESCRIPTION,
            "version": settings.VERSION,
            "docs_url": "/docs"
            if settings.DEBUG
            else "Documentation disabled in production",
            "health_check": f"{settings.API_V1_STR}/health/",
            "api_prefix": settings.API_V1_STR,
        }

    # Global exception handler
    @application.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "status_code": exc.status_code,
            },
        )

    return application


app = create_application()
