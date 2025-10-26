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
from app.db.session import SessionLocal
from app.crud.crud_management_user_profile import management_user_profile
from app.models.management_user import ManagementUser
from app.schemas.management_user_profile import ManagementUserProfileCreate
import logging

logger = logging.getLogger(__name__)

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

    # Startup event to initialize default management user profiles
    @application.on_event("startup")
    async def startup_event():
        """Initialize default management user profiles for tenant 1."""
        try:
            db = SessionLocal()
            try:
                # Get all management users without a profile
                all_management_users = db.query(ManagementUser).all()
                
                for mgmt_user in all_management_users:
                    # Check if profile exists
                    existing_profile = management_user_profile.get_by_management_user_id(
                        db, 
                        management_user_id=mgmt_user.id
                    )
                    
                    # If no profile exists, create one
                    if not existing_profile:
                        profile_data = ManagementUserProfileCreate(
                            management_user_id=mgmt_user.id,
                            fullname=f"{mgmt_user.first_name} {mgmt_user.last_name}",
                            email=mgmt_user.email,
                            is_active=mgmt_user.is_active
                        )
                        management_user_profile.create(db, obj_in=profile_data)
                        logger.info(f"Created default profile for management user {mgmt_user.email}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error initializing management user profiles: {str(e)}", exc_info=True)

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
